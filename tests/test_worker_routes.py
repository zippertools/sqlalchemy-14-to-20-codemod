from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_cloudflare_assets_runs_worker_for_checkout_and_webhooks() -> None:
    config = json.loads(Path("wrangler.jsonc").read_text(encoding="utf-8"))

    run_worker_first = set(config["assets"]["run_worker_first"])
    assert run_worker_first >= {
        "/scan",
        "/go/*",
        "/stripe/*",
        "/payhip",
        "/payhip/*",
        "/__stripe_paid_assets/*",
    }
    assert not any(
        route.startswith("/go/") and route != "/go/*" for route in run_worker_first
    )
    assert "analytics_engine_datasets" not in config
    assert config["observability"]["enabled"] is True
    # Conversion routes write structured Worker logs. Keeping this out of
    # Analytics Engine avoids a dashboard feature gate during zero-cost deploys.
    # The retired checkout paths run through the Worker so stale assets cannot
    # be served if an old deployment artifact exists.


def test_worker_tracks_source_tagged_go_routes() -> None:
    script = """
import worker from './worker/index.mjs';
const env = {
  ASSETS: { fetch: async () => new Response('asset') },
  STRIPE_SECRET_KEY: 'sk_test_unit',
  SALE_NOW_ISO: '2026-05-07T12:00:00Z',
};
const originalFetch = globalThis.fetch;
globalThis.fetch = async (url, init) => {
  const params = new URLSearchParams(init.body);
  console.log([
    url,
    params.get('metadata[product_slug]'),
    params.get('metadata[source]'),
    params.get('line_items[0][price_data][unit_amount]'),
  ].join(' '));
  return new Response(
    JSON.stringify({ url: 'https://checkout.stripe.com/c/pay/cs_test_sa20' }),
    { status: 200 },
  );
};
const request = new Request('https://zippertools.org/go/sa20-pack/product-sa20-pack');
const response = await worker.fetch(request, env);
globalThis.fetch = originalFetch;
console.log(response.status);
console.log(response.headers.get('location'));
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    lines = result.stdout.strip().splitlines()
    assert "conversion_route" in lines[0]
    assert lines[1] == (
        "https://api.stripe.com/v1/checkout/sessions sa20-pack product-sa20-pack 29999"
    )
    assert lines[-2] == "303"
    assert lines[-1] == "https://checkout.stripe.com/c/pay/cs_test_sa20"


def test_all_paid_go_routes_create_stripe_checkout_sessions() -> None:
    script = """
import worker from './worker/index.mjs';
const env = {
  ASSETS: { fetch: async () => new Response('asset') },
  STRIPE_SECRET_KEY: 'sk_test_unit',
  SALE_NOW_ISO: '2026-05-07T12:00:00Z',
};
const routes = [
  ['/go/fit-report', 'fit-report', '9900'],
  ['/go/sa20-pack', 'sa20-pack', '29999'],
  ['/go/sa20-preset', 'sa20-preset', '14999'],
  ['/go/pydantic-v2-porter', 'pydantic-v2-porter', '24999'],
];
const originalLog = console.log;
console.log = () => {};
const originalFetch = globalThis.fetch;
globalThis.fetch = async (_url, init) => {
  const params = new URLSearchParams(init.body);
  const product = params.get('metadata[product_slug]');
  const amount = params.get('line_items[0][price_data][unit_amount]');
  const coupon = params.get('discounts[0][coupon]');
  const saleName = params.get('metadata[sale_name]');
  const checkoutUrl =
    `https://checkout.stripe.com/c/pay/cs_test_${product}_${amount}_${coupon}_${saleName}`;
  return new Response(
    JSON.stringify({ url: checkoutUrl }),
    { status: 200 },
  );
};
for (const [route] of routes) {
  const request = new Request(`https://zippertools.org${route}/unit-test`);
  const response = await worker.fetch(request, env);
  const location = new URL(response.headers.get('location'));
  const payload = decodeURIComponent(location.pathname.split('cs_test_').at(-1));
  originalLog([
    response.status,
    location.host,
    payload,
  ].join(' '));
}
globalThis.fetch = originalFetch;
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip().splitlines() == [
        "303 checkout.stripe.com fit-report_9900_ro5ZyRLf_Migration Sprint Sale",
        "303 checkout.stripe.com sa20-pack_29999_ro5ZyRLf_Migration Sprint Sale",
        "303 checkout.stripe.com sa20-preset_14999_ro5ZyRLf_Migration Sprint Sale",
        (
            "303 checkout.stripe.com "
            "pydantic-v2-porter_24999_ro5ZyRLf_Migration Sprint Sale"
        ),
    ]


def test_paid_go_routes_stop_sale_discount_after_deadline() -> None:
    script = """
import worker from './worker/index.mjs';
const env = {
  ASSETS: { fetch: async () => new Response('asset') },
  STRIPE_SECRET_KEY: 'sk_test_unit',
  SALE_NOW_ISO: '2026-05-29T12:00:00Z',
};
let observedParams = null;
const originalLog = console.log;
console.log = () => {};
const originalFetch = globalThis.fetch;
globalThis.fetch = async (_url, init) => {
  observedParams = new URLSearchParams(init.body);
  return new Response(
    JSON.stringify({ url: 'https://checkout.stripe.com/c/pay/cs_test_after_sale' }),
    { status: 200 },
  );
};
const response = await worker.fetch(
  new Request('https://zippertools.org/go/sa20-pack/unit-test'),
  env,
);
globalThis.fetch = originalFetch;
originalLog([
  response.status,
  observedParams.get('discounts[0][coupon]') || 'no-coupon',
  observedParams.get('allow_promotion_codes') || 'no-promo-field',
  observedParams.get('metadata[sale_name]') || 'no-sale-metadata',
].join(' '));
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == "303 no-coupon true no-sale-metadata"


def test_all_free_scan_routes_land_on_matching_public_docs() -> None:
    script = """
import worker from './worker/index.mjs';
const env = { ASSETS: { fetch: async () => new Response('asset') } };
const routes = [
  ['/go/free-scan', '/docs/quickstart.md'],
  ['/go/actions-upgrade-guard-free', '/products/actions-upgrade-guard/README.md'],
  ['/go/pydantic-free-scan', '/products/pydantic-v2-porter/README.md'],
  ['/go/flatconfig-free-scan', '/products/flatconfig-lift/README.md'],
];
const originalLog = console.log;
console.log = () => {};
for (const [route, expectedPath] of routes) {
  const request = new Request(`https://zippertools.org${route}/unit-test`);
  const response = await worker.fetch(request, env);
  const location = new URL(response.headers.get('location'));
  originalLog([
    response.status,
    location.host,
    location.pathname,
    location.searchParams.get('utm_campaign'),
    location.searchParams.get('utm_term'),
  ].join(' '));
}
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip().splitlines() == [
        (
            "302 github.com /zippertools/sqlalchemy-14-to-20-codemod/blob/main/"
            "docs/quickstart.md free_scan unit-test"
        ),
        (
            "302 github.com /zippertools/sqlalchemy-14-to-20-codemod/blob/main/"
            "products/actions-upgrade-guard/README.md free_scan unit-test"
        ),
        (
            "302 github.com /zippertools/sqlalchemy-14-to-20-codemod/blob/main/"
            "products/pydantic-v2-porter/"
            "README.md free_scan unit-test"
        ),
        (
            "302 github.com /zippertools/sqlalchemy-14-to-20-codemod/blob/main/"
            "products/flatconfig-lift/README.md free_scan unit-test"
        ),
    ]


def test_source_query_go_routes_and_scan_query_are_worker_owned() -> None:
    script = """
import worker from './worker/index.mjs';
const env = {
  ASSETS: {
    fetch: async () =>
      new Response('<title>scan</title>', {
        headers: { 'content-type': 'text/html' },
      }),
  },
  STRIPE_SECRET_KEY: 'sk_test_unit',
};
const originalLog = console.log;
console.log = () => {};
const originalFetch = globalThis.fetch;
globalThis.fetch = async (_url, init) => {
  const params = new URLSearchParams(init.body);
  const product = params.get('metadata[product_slug]');
  return new Response(
    JSON.stringify({ url: `https://checkout.stripe.com/c/pay/cs_test_${product}` }),
    { status: 200 },
  );
};
const checks = [
  new Request('https://zippertools.org/scan?source=home-hero'),
  new Request('https://zippertools.org/go/free-scan?source=pricing-free'),
  new Request('https://zippertools.org/go/actions-upgrade-guard-free?source=home-well'),
  new Request('https://zippertools.org/go/pydantic-free-scan?source=guide-pydantic-basesettings-moved'),
  new Request('https://zippertools.org/go/fit-report?source=guide-pydantic-basesettings-moved'),
  new Request('https://zippertools.org/go/pydantic-v2-porter?source=guide-pydantic-basesettings-moved'),
];
for (const request of checks) {
  const response = await worker.fetch(request, env);
  const location = response.headers.get('location') || '';
  originalLog([response.status, location].join(' '));
}
globalThis.fetch = originalFetch;
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    lines = result.stdout.strip().splitlines()
    assert lines[0] == "302 https://zippertools.org/scan"
    assert lines[1].startswith(
        "302 https://github.com/zippertools/sqlalchemy-14-to-20-codemod/blob/main/docs/quickstart.md"
    )
    assert "utm_term=pricing-free" in lines[1]
    assert lines[2].startswith(
        "302 https://github.com/zippertools/sqlalchemy-14-to-20-codemod/blob/main/products/actions-upgrade-guard/README.md"
    )
    assert "utm_term=home-well" in lines[2]
    assert lines[3].startswith(
        "302 https://github.com/zippertools/sqlalchemy-14-to-20-codemod/blob/main/products/pydantic-v2-porter/README.md"
    )
    assert "utm_term=guide-pydantic-basesettings-moved" in lines[3]
    assert lines[4].startswith(
        "303 https://checkout.stripe.com/c/pay/cs_test_fit-report"
    )
    assert lines[5].startswith(
        "303 https://checkout.stripe.com/c/pay/cs_test_pydantic-v2-porter"
    )


def test_legacy_fit_review_route_points_to_stripe_fit_report_checkout() -> None:
    script = """
import worker from './worker/index.mjs';
const env = { ASSETS: { fetch: async () => new Response('asset') } };
const originalLog = console.log;
console.log = () => {};
const request = new Request('https://zippertools.org/go/fit-review/unit-test');
const response = await worker.fetch(request, env);
const location = new URL(response.headers.get('location'));
console.log = originalLog;
console.log([response.status, location.host, location.pathname].join(' '));
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == "302 zippertools.org /go/fit-report"


def test_stripe_checkout_requires_secret_before_payment() -> None:
    script = """
import worker from './worker/index.mjs';
const env = { ASSETS: { fetch: async () => new Response('asset') } };
const originalLog = console.log;
const originalWarn = console.warn;
console.log = () => {};
console.warn = () => {};
const response = await worker.fetch(
  new Request('https://zippertools.org/go/sa20-pack/unit-test'),
  env,
);
console.log = originalLog;
console.warn = originalWarn;
console.log(response.status);
console.log(await response.text());
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    lines = result.stdout.strip().splitlines()
    assert lines[-2] == "503"
    assert '"stripe_not_configured"' in lines[-1]


def test_stripe_checkout_audit_passes_locally() -> None:
    result = subprocess.run(
        ["node", "scripts/audit_stripe_checkout.mjs"],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "local Stripe checkout audit passed for 4 products" in result.stdout


def test_stripe_delivery_serves_asset_after_paid_session() -> None:
    script = """
import worker from './worker/index.mjs';
const assetHits = [];
const env = {
  ASSETS: { fetch: async () => new Response('asset') },
  PAID_ARTIFACTS: {
    get: async (key) => {
      assetHits.push(key);
      if (key === 'manifest:sa20-pack-edge-case-pack-v0.1.2.zip') {
        return JSON.stringify({ chunks: 1, bytes: 9 });
      }
      if (key === 'chunk:sa20-pack-edge-case-pack-v0.1.2.zip:0') {
        return btoa('zip-bytes');
      }
      return null;
    },
  },
  STRIPE_SECRET_KEY: 'sk_test_unit',
};
const originalLog = console.log;
console.log = () => {};
const originalFetch = globalThis.fetch;
globalThis.fetch = async (url) => {
  originalLog(url);
  return new Response(JSON.stringify({
    id: 'cs_test_paid',
    payment_status: 'paid',
    metadata: { product_slug: 'sa20-pack' },
  }), { status: 200 });
};
const response = await worker.fetch(
  new Request('https://zippertools.org/stripe/delivery?session_id=cs_test_paid'),
  env,
);
globalThis.fetch = originalFetch;
console.log = originalLog;
console.log(assetHits[0]);
console.log(response.status);
console.log(response.headers.get('content-disposition'));
console.log(await response.text());
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip().splitlines() == [
        "https://api.stripe.com/v1/checkout/sessions/cs_test_paid",
        "manifest:sa20-pack-edge-case-pack-v0.1.2.zip",
        "200",
        'attachment; filename="sa20-pack-edge-case-pack-v0.1.2.zip"',
        "zip-bytes",
    ]


def test_paid_asset_paths_are_not_directly_public() -> None:
    script = """
import worker from './worker/index.mjs';
let assetFetchCount = 0;
const env = {
  ASSETS: {
    fetch: async () => {
      assetFetchCount += 1;
      return new Response('leaked');
    },
  },
};
const response = await worker.fetch(
  new Request('https://zippertools.org/__stripe_paid_assets/sa20-pack-edge-case-pack-v0.1.2.zip'),
  env,
);
console.log(response.status);
console.log(assetFetchCount);
console.log(await response.text());
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    lines = result.stdout.strip().splitlines()
    assert lines[0] == "404"
    assert lines[1] == "0"
    assert '"not_found"' in lines[2]


def test_retired_payhip_paths_are_not_public() -> None:
    script = """
import worker from './worker/index.mjs';
let assetFetchCount = 0;
const env = {
  ASSETS: {
    fetch: async () => {
      assetFetchCount += 1;
      return new Response('stale checkout');
    },
  },
};
for (const path of ['/payhip', '/payhip/old-product']) {
  const response = await worker.fetch(
    new Request(`https://zippertools.org${path}`),
    env,
  );
  console.log(response.status);
  console.log(await response.text());
}
console.log(assetFetchCount);
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    lines = result.stdout.strip().splitlines()
    assert lines == [
        "404",
        '{"ok":false,"error":"not_found"}',
        "404",
        '{"ok":false,"error":"not_found"}',
        "0",
    ]


def test_cancel_page_title_uses_product_query() -> None:
    script = """
import worker from './worker/index.mjs';
const env = {
  ASSETS: {
    fetch: async () =>
      new Response(
        '<!doctype html><title>Checkout canceled | Zipper Tools</title>' +
          '<h1>No charge was completed.</h1>',
        { headers: { 'content-type': 'text/html; charset=utf-8' } },
      ),
  },
};
for (const product of ['fit-report', 'sa20-preset']) {
  const response = await worker.fetch(
    new Request(`https://zippertools.org/cancel?product=${product}`),
    env,
  );
  console.log(response.status);
  console.log((await response.text()).match(/<title>(.*?)<\\/title>/)[1]);
}
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip().splitlines() == [
        "200",
        "Checkout canceled | SQLAlchemy/Pydantic Fit Report Add-on",
        "200",
        "Checkout canceled | Migration Preset Bundle",
    ]


def test_stripe_webhook_verifies_signed_checkout_event() -> None:
    script = """
import worker from './worker/index.mjs';
const secret = 'whsec_unit';
const payload = JSON.stringify({
  id: 'evt_unit',
  type: 'checkout.session.completed',
  livemode: false,
  data: {
    object: {
      id: 'cs_test_paid',
      mode: 'payment',
      payment_status: 'paid',
      amount_total: 29999,
      currency: 'usd',
      metadata: { product_slug: 'sa20-pack', source: 'unit-test' },
    },
  },
});
const timestamp = String(Math.floor(Date.now() / 1000));
const encoder = new TextEncoder();
const key = await crypto.subtle.importKey(
  'raw',
  encoder.encode(secret),
  { name: 'HMAC', hash: 'SHA-256' },
  false,
  ['sign'],
);
const signed = await crypto.subtle.sign(
  'HMAC',
  key,
  encoder.encode(`${timestamp}.${payload}`),
);
const hex = Array.from(new Uint8Array(signed), (byte) =>
  byte.toString(16).padStart(2, '0'),
).join('');
const env = {
  ASSETS: { fetch: async () => new Response('asset') },
  STRIPE_WEBHOOK_SECRET: secret,
};
const originalLog = console.log;
console.log = () => {};
const response = await worker.fetch(
  new Request('https://zippertools.org/stripe/webhook', {
    method: 'POST',
    body: payload,
    headers: { 'stripe-signature': `t=${timestamp},v1=${hex}` },
  }),
  env,
);
console.log = originalLog;
console.log(response.status);
console.log(await response.text());
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip().splitlines() == [
        "200",
        '{"ok":true}',
    ]
