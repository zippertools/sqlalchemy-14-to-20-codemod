#!/usr/bin/env node

import worker, { STRIPE_PRODUCTS } from "../worker/index.mjs";

const DEFAULT_SITE_URL = "https://zippertools.org";
const AUDIT_SOURCE = "stripe-audit";
const SALE_COUPON_ID = "ro5ZyRLf";
const SALE_NOW_ISO = "2026-05-07T12:00:00Z";
const PRODUCTS = Object.values(STRIPE_PRODUCTS).map((product) => ({
  label: product.label,
  route: `/go/${product.slug}`,
  amount: String(product.unitAmount),
  name: product.name,
  artifactKey: product.artifactKey,
  downloadName: product.downloadName,
}));

function parseArgs(argv) {
  const args = { siteUrl: DEFAULT_SITE_URL };
  for (let index = 2; index < argv.length; index += 1) {
    const item = argv[index];
    if (item === "--site-url") {
      args.siteUrl = argv[index + 1];
      index += 1;
    } else {
      throw new Error(`Unknown argument: ${item}`);
    }
  }

  if (!args.siteUrl || !/^https?:\/\//.test(args.siteUrl)) {
    throw new Error("--site-url must be an absolute URL");
  }
  args.siteUrl = args.siteUrl.replace(/\/$/, "");
  return args;
}

function assertAudit(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

async function auditProduct(args, product) {
  let observedParams = null;
  const previousFetch = globalThis.fetch;
  const previousLog = console.log;
  console.log = () => {};
  globalThis.fetch = async (url, init) => {
    assertAudit(
      url === "https://api.stripe.com/v1/checkout/sessions",
      `${product.route} called unexpected Stripe URL: ${url}`,
    );
    observedParams = new URLSearchParams(init.body);
    return new Response(
      JSON.stringify({
        url: `https://checkout.stripe.com/c/pay/cs_test_${product.label}`,
      }),
      { status: 200 },
    );
  };

  try {
    const request = new Request(`${args.siteUrl}${product.route}/${AUDIT_SOURCE}`, {method: "POST", headers: {origin: args.siteUrl}});
    const env = {
      ASSETS: { fetch: async () => new Response("asset") },
      STRIPE_SECRET_KEY: "sk_test_audit",
      SALE_NOW_ISO,
    };
    const response = await worker.fetch(request, env);
    const location = response.headers.get("location") || "";

    assertAudit(response.status === 303, `${product.route} returned ${response.status}`);
    assertAudit(
      location.startsWith("https://checkout.stripe.com/"),
      `${product.route} did not return a Stripe Checkout URL`,
    );
    assertAudit(observedParams, `${product.route} did not create a Checkout Session`);
    assertAudit(
      observedParams.get("mode") === "payment",
      `${product.route} did not create a payment-mode Checkout Session`,
    );
    assertAudit(
      observedParams.get("metadata[product_slug]") === product.label,
      `${product.route} sent the wrong product slug`,
    );
    assertAudit(
      observedParams.get("metadata[source]") === AUDIT_SOURCE,
      `${product.route} did not preserve the source tag`,
    );
    assertAudit(
      observedParams.get("line_items[0][price_data][unit_amount]") === product.amount,
      `${product.route} sent the wrong Stripe amount`,
    );
    assertAudit(
      observedParams.get("line_items[0][price_data][product_data][name]") ===
        product.name,
      `${product.route} sent the wrong product name`,
    );
    assertAudit(
      observedParams.get("discounts[0][coupon]") === SALE_COUPON_ID,
      `${product.route} did not apply the sale coupon`,
    );
    assertAudit(
      !observedParams.has("allow_promotion_codes"),
      `${product.route} should not mix automatic discounts with promotion-code entry`,
    );
    assertAudit(
      observedParams.get("metadata[sale_name]") === "Migration Sprint Sale",
      `${product.route} did not include sale metadata`,
    );
    return { route: product.route, location };
  } finally {
    globalThis.fetch = previousFetch;
    console.log = previousLog;
  }
}

async function auditDelivery(args, product) {
  const previousFetch = globalThis.fetch;
  const previousLog = console.log;
  console.log = () => {};
  const artifactHits = [];
  globalThis.fetch = async (url) => {
    assertAudit(
      url === "https://api.stripe.com/v1/checkout/sessions/cs_test_paid",
      `${product.route} delivery called unexpected Stripe URL: ${url}`,
    );
    return new Response(
      JSON.stringify({
        id: "cs_test_paid",
        payment_status: "paid",
        metadata: { product_slug: product.label },
      }),
      { status: 200 },
    );
  };

  try {
    const request = new Request(`${args.siteUrl}/stripe/delivery?session_id=cs_test_paid`);
    const env = {
      ASSETS: {
        fetch: async () => new Response("asset"),
      },
      PAID_ARTIFACTS: {
        get: async (key) => {
          artifactHits.push(key);
          if (key === `manifest:${product.artifactKey}`) {
            return JSON.stringify({ chunks: 1, bytes: 9 });
          }
          if (key === `chunk:${product.artifactKey}:0`) {
            return btoa("zip-bytes");
          }
          return null;
        },
      },
      STRIPE_SECRET_KEY: "sk_test_audit",
    };
    const response = await worker.fetch(request, env);
    assertAudit(response.status === 200, `${product.route} delivery returned ${response.status}`);
    assertAudit(
      artifactHits[0] === `manifest:${product.artifactKey}`,
      `${product.route} delivery fetched ${artifactHits[0] || "nothing"} instead of ${product.artifactKey}`,
    );
    assertAudit(
      response.headers.get("content-disposition") ===
        `attachment; filename="${product.downloadName}"`,
      `${product.route} delivery used the wrong download filename`,
    );
    return { route: product.route, artifactKey: product.artifactKey };
  } finally {
    globalThis.fetch = previousFetch;
    console.log = previousLog;
  }
}

async function auditDirectAssetBlock(args, product) {
  const env = {
    ASSETS: {
      fetch: async () => new Response("asset should not be public", { status: 200 }),
    },
  };
  const response = await worker.fetch(
    new Request(`${args.siteUrl}/__stripe_paid_assets/${product.artifactKey}`),
    env,
  );
  assertAudit(
    response.status === 404,
    `${product.artifactKey} should be blocked from direct public access`,
  );
}

async function main() {
  const args = parseArgs(process.argv);
  const results = [];
  const deliveries = [];
  for (const product of PRODUCTS) {
    results.push(await auditProduct(args, product));
    deliveries.push(await auditDelivery(args, product));
    await auditDirectAssetBlock(args, product);
  }

  console.log(`local Stripe checkout audit passed for ${results.length} products`);
  for (const result of results) {
    console.log(`${result.route} -> ${result.location}`);
  }
  console.log(`local Stripe delivery audit passed for ${deliveries.length} products`);
  for (const result of deliveries) {
    console.log(`${result.route} -> ${result.artifactKey}`);
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
