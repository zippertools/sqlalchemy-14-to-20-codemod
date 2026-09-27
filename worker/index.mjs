import {
  checkoutProducts,
  checkoutSale,
  goRoutes,
} from "../site/product_catalog.mjs";

const MAX_WEBHOOK_BYTES = 256 * 1024;
const STRIPE_WEBHOOK_PATH = "/stripe/webhook";
const STRIPE_DELIVERY_PATH = "/stripe/delivery";
const STRIPE_CHECKOUT_API_URL = "https://api.stripe.com/v1/checkout/sessions";
const STRIPE_CHECKOUT_SESSION_API_URL =
  "https://api.stripe.com/v1/checkout/sessions";
const STRIPE_WEBHOOK_TOLERANCE_SECONDS = 5 * 60;
const LEGACY_PAID_ASSET_PATH_PREFIX = "/__stripe_paid_assets/";
const RETIRED_PAYHIP_PATH = "/payhip";
const CANCEL_PATH = "/cancel";
const SCAN_PATH = "/scan";

const DELIVERY_ARTIFACTS = {
  "fit-report": {
    artifactKey: "fit-report-add-on.zip",
    downloadName: "zippertools-fit-report-add-on.zip",
  },
  "sa20-pack": {
    artifactKey: "sa20-pack-edge-case-pack-v0.1.2.zip",
    downloadName: "sa20-pack-edge-case-pack-v0.1.2.zip",
  },
  "sa20-preset": {
    artifactKey: "sa20-pack-preset-bundle.zip",
    downloadName: "sa20-pack-preset-bundle.zip",
  },
  "pydantic-v2-porter": {
    artifactKey: "pydantic-v2-porter-v0.1.2.zip",
    downloadName: "pydantic-v2-porter-v0.1.2.zip",
  },
};

export const STRIPE_PRODUCTS = Object.freeze(
  Object.fromEntries(
    Object.values(checkoutProducts).map((product) => {
      const delivery = DELIVERY_ARTIFACTS[product.checkoutSlug];
      return [
        product.checkoutSlug,
        {
          slug: product.checkoutSlug,
          label: product.checkoutSlug,
          name: product.name,
          description: product.description,
          unitAmount: product.amountCents,
          currency: product.currency,
          artifactKey: delivery.artifactKey,
          downloadName: delivery.downloadName,
        },
      ];
    }),
  ),
);

export const GO_ROUTES = goRoutes;
export const CHECKOUT_SALE = checkoutSale;

function jsonResponse(value, init = {}) {
  const headers = new Headers(init.headers);
  headers.set("content-type", "application/json; charset=utf-8");
  headers.set("cache-control", "no-store");
  return new Response(JSON.stringify(value), { ...init, headers });
}

function matchGoRoute(url) {
  const pathname = url.pathname;
  const candidates = Object.entries(GO_ROUTES).sort(
    ([left], [right]) => right.length - left.length,
  );
  for (const [basePath, route] of candidates) {
    if (pathname === basePath) {
      return {
        basePath,
        route,
        source: safeSource(url.searchParams.get("source") || "unknown"),
      };
    }
    if (pathname.startsWith(`${basePath}/`)) {
      const source = pathname.slice(basePath.length + 1) || "unknown";
      return { basePath, route, source: safeSource(source) };
    }
  }
  return null;
}

function appendTrackingParam(target, source) {
  let url;
  try {
    url = new URL(target);
  } catch {
    return target;
  }
  if (!["http:", "https:"].includes(url.protocol)) {
    return target;
  }
  if (source && source !== "unknown") {
    url.searchParams.set("utm_term", source.slice(0, 120));
  }
  return url.toString();
}

function writeConversionEvent(env, event) {
  console.log("conversion_route", JSON.stringify(event));
  if (env.CONVERSION_EVENTS?.writeDataPoint) {
    env.CONVERSION_EVENTS.writeDataPoint({
      blobs: [
        event.kind,
        event.label,
        event.source,
        event.path,
        event.country,
        event.refererHost,
      ],
      doubles: [Date.now()],
      indexes: [event.label],
    });
  }
}

function siteOrigin(request) {
  const url = new URL(request.url);
  return `${url.protocol}//${url.host}`;
}

function safeSource(value) {
  return String(value || "unknown").slice(0, 120);
}

function saleClockMs(env) {
  if (env.SALE_NOW_ISO) {
    const override = Date.parse(env.SALE_NOW_ISO);
    if (Number.isFinite(override)) {
      return override;
    }
  }
  return Date.now();
}

function activeCheckoutSale(env) {
  if (!CHECKOUT_SALE?.active || !CHECKOUT_SALE.stripeCouponId) {
    return null;
  }
  const startsAt = Date.parse(CHECKOUT_SALE.startsAt || "");
  const endsAt = Date.parse(CHECKOUT_SALE.endsAt || "");
  const now = saleClockMs(env);
  if (
    !Number.isFinite(startsAt) ||
    !Number.isFinite(endsAt) ||
    now < startsAt ||
    now > endsAt
  ) {
    return null;
  }
  return CHECKOUT_SALE;
}

function buildStripeCheckoutBody(request, env, product, source) {
  const origin = siteOrigin(request);
  const body = new URLSearchParams();
  body.set("mode", "payment");
  body.set("success_url", `${origin}/success?session_id={CHECKOUT_SESSION_ID}`);
  body.set("cancel_url", `${origin}/cancel?product=${product.slug}`);
  const sale = activeCheckoutSale(env);
  if (sale) {
    body.set("discounts[0][coupon]", sale.stripeCouponId);
  } else {
    body.set("allow_promotion_codes", "true");
  }
  body.set(
    "automatic_tax[enabled]",
    env.STRIPE_AUTOMATIC_TAX_ENABLED === "true" ? "true" : "false",
  );
  body.set("line_items[0][quantity]", "1");
  body.set("line_items[0][price_data][currency]", product.currency);
  body.set(
    "line_items[0][price_data][unit_amount]",
    String(product.unitAmount),
  );
  body.set("line_items[0][price_data][product_data][name]", product.name);
  body.set(
    "line_items[0][price_data][product_data][description]",
    product.description,
  );
  body.set(
    "line_items[0][price_data][product_data][images][0]",
    `${origin}/og-preview.svg`,
  );
  body.set(
    "line_items[0][price_data][product_data][metadata][product_slug]",
    product.slug,
  );
  body.set("metadata[product_slug]", product.slug);
  body.set("metadata[source]", safeSource(source));
  if (sale) {
    body.set("metadata[sale_name]", sale.name);
    body.set("metadata[sale_discount_percent]", String(sale.discountPercent));
    body.set("metadata[sale_ends_at]", sale.endsAt);
  }
  body.set("payment_intent_data[metadata][product_slug]", product.slug);
  body.set("payment_intent_data[metadata][source]", safeSource(source));
  if (sale) {
    body.set("payment_intent_data[metadata][sale_name]", sale.name);
    body.set("payment_intent_data[metadata][sale_discount_percent]", String(sale.discountPercent));
  }
  body.set("client_reference_id", `${product.slug}:${safeSource(source)}`);
  return body;
}

function summarizeStripeError(status, payload) {
  const error = payload?.error || {};
  return {
    status,
    type: error.type || "",
    code: error.code || "",
    decline_code: error.decline_code || "",
    message: error.message || "Stripe API request failed",
  };
}

async function parseStripeJsonResponse(response) {
  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch {
    return { raw: text.slice(0, 500) };
  }
}

async function createStripeCheckoutSession(request, env, product, source) {
  if (!env.STRIPE_SECRET_KEY) {
    console.warn("stripe_checkout_missing_secret");
    return jsonResponse(
      {
        ok: false,
        error: "stripe_not_configured",
        detail: "Missing STRIPE_SECRET_KEY Worker secret.",
      },
      { status: 503 },
    );
  }

  const stripeResponse = await fetch(STRIPE_CHECKOUT_API_URL, {
    method: "POST",
    headers: {
      authorization: `Bearer ${env.STRIPE_SECRET_KEY}`,
      "content-type": "application/x-www-form-urlencoded",
    },
    body: buildStripeCheckoutBody(request, env, product, source),
  });
  const payload = await parseStripeJsonResponse(stripeResponse);

  if (!stripeResponse.ok || typeof payload.url !== "string") {
    const summary = summarizeStripeError(stripeResponse.status, payload);
    console.warn("stripe_checkout_create_failed", JSON.stringify(summary));
    return jsonResponse(
      { ok: false, error: "stripe_checkout_create_failed", stripe: summary },
      { status: 502 },
    );
  }

  const headers = new Headers({
    location: payload.url,
    "cache-control": "no-store",
  });
  return new Response(null, { status: 303, headers });
}

function buildConversionEvent(request, match) {
  const url = new URL(request.url);
  const referer = request.headers.get("referer") || "";
  let refererHost = "";
  try {
    refererHost = referer ? new URL(referer).host : "";
  } catch {
    refererHost = "";
  }

  return {
    kind: match.route.kind,
    label: match.route.label,
    source: match.source,
    path: url.pathname,
    method: request.method,
    country: request.cf?.country || "",
    colo: request.cf?.colo || "",
    refererHost,
  };
}

async function handleGoRoute(request, env, match) {
  const event = buildConversionEvent(request, match);
  writeConversionEvent(env, event);

  if (match.route.kind === "checkout") {
    const product = STRIPE_PRODUCTS[match.route.productSlug];
    if (!product) {
      return jsonResponse({ ok: false, error: "unknown_product" }, { status: 404 });
    }
    return createStripeCheckoutSession(request, env, product, match.source);
  }

  const headers = new Headers({
    location: appendTrackingParam(match.route.target, match.source),
    "cache-control": "no-store",
  });
  return new Response(null, { status: 302, headers });
}

function hexToBytes(value) {
  if (!/^[0-9a-f]+$/i.test(value) || value.length % 2 !== 0) {
    return null;
  }

  const bytes = new Uint8Array(value.length / 2);
  for (let index = 0; index < value.length; index += 2) {
    bytes[index / 2] = Number.parseInt(value.slice(index, index + 2), 16);
  }
  return bytes;
}

function timingSafeEqual(left, right) {
  if (left.byteLength !== right.byteLength) {
    return false;
  }

  let difference = 0;
  for (let index = 0; index < left.byteLength; index += 1) {
    difference |= left[index] ^ right[index];
  }
  return difference === 0;
}

async function hmacSha256Hex(secret, value) {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign("HMAC", key, encoder.encode(value));
  return Array.from(new Uint8Array(signature), (byte) =>
    byte.toString(16).padStart(2, "0"),
  ).join("");
}

function parseStripeSignatureHeader(value) {
  const result = { timestamp: "", signatures: [] };
  for (const part of String(value || "").split(",")) {
    const [key, ...rest] = part.split("=");
    const itemValue = rest.join("=");
    if (key === "t") {
      result.timestamp = itemValue;
    }
    if (key === "v1" && itemValue) {
      result.signatures.push(itemValue);
    }
  }
  return result;
}

async function verifyStripeSignature(payloadText, signatureHeader, webhookSecret) {
  const parsed = parseStripeSignatureHeader(signatureHeader);
  const timestamp = Number(parsed.timestamp);
  if (!Number.isFinite(timestamp) || parsed.signatures.length === 0) {
    return false;
  }

  const ageSeconds = Math.abs(Date.now() / 1000 - timestamp);
  if (ageSeconds > STRIPE_WEBHOOK_TOLERANCE_SECONDS) {
    return false;
  }

  const expectedHex = await hmacSha256Hex(
    webhookSecret,
    `${parsed.timestamp}.${payloadText}`,
  );
  const expected = hexToBytes(expectedHex);
  if (!expected) {
    return false;
  }

  return parsed.signatures.some((signature) => {
    const provided = hexToBytes(signature);
    return Boolean(provided && timingSafeEqual(provided, expected));
  });
}

function summarizeStripeSession(session) {
  return {
    id: session.id || "",
    mode: session.mode || "",
    payment_status: session.payment_status || "",
    amount_total: session.amount_total ?? null,
    currency: session.currency || "",
    product_slug: session.metadata?.product_slug || "",
    source: session.metadata?.source || "",
  };
}

function summarizeStripeEvent(event) {
  const object = event?.data?.object || {};
  return {
    id: event.id || "",
    type: event.type || "",
    livemode: Boolean(event.livemode),
    session: event.type?.startsWith("checkout.session")
      ? summarizeStripeSession(object)
      : null,
  };
}

function base64ToBytes(value) {
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}

async function readPaidArtifact(env, product) {
  if (!env.PAID_ARTIFACTS?.get) {
    return { ok: false, error: "delivery_not_configured" };
  }

  const manifestText = await env.PAID_ARTIFACTS.get(
    `manifest:${product.artifactKey}`,
  );
  if (!manifestText) {
    return { ok: false, error: "delivery_artifact_missing" };
  }

  let manifest;
  try {
    manifest = JSON.parse(manifestText);
  } catch {
    return { ok: false, error: "delivery_artifact_manifest_invalid" };
  }

  const chunkCount = Number(manifest.chunks);
  if (!Number.isInteger(chunkCount) || chunkCount <= 0 || chunkCount > 100) {
    return { ok: false, error: "delivery_artifact_manifest_invalid" };
  }

  const chunks = await Promise.all(
    Array.from({ length: chunkCount }, (_value, index) =>
      env.PAID_ARTIFACTS.get(`chunk:${product.artifactKey}:${index}`),
    ),
  );
  if (chunks.some((chunk) => !chunk)) {
    return { ok: false, error: "delivery_artifact_chunk_missing" };
  }

  return {
    ok: true,
    bytes: base64ToBytes(chunks.join("")),
    byteLength: Number(manifest.bytes) || null,
  };
}

async function handleStripeWebhook(request, env) {
  if (request.method === "GET" || request.method === "HEAD") {
    return jsonResponse({
      ok: true,
      endpoint: STRIPE_WEBHOOK_PATH,
      configured: Boolean(env.STRIPE_WEBHOOK_SECRET),
    });
  }

  if (request.method !== "POST") {
    return jsonResponse({ ok: false, error: "method_not_allowed" }, { status: 405 });
  }

  if (!env.STRIPE_WEBHOOK_SECRET) {
    console.warn("stripe_webhook_missing_secret");
    return jsonResponse({ ok: false, error: "not_configured" }, { status: 503 });
  }

  const contentLength = Number(request.headers.get("content-length") || "0");
  if (contentLength > MAX_WEBHOOK_BYTES) {
    return jsonResponse({ ok: false, error: "payload_too_large" }, { status: 413 });
  }

  const payloadText = await request.text();
  const valid = await verifyStripeSignature(
    payloadText,
    request.headers.get("stripe-signature") || "",
    env.STRIPE_WEBHOOK_SECRET,
  );
  if (!valid) {
    console.warn("stripe_webhook_invalid_signature");
    return jsonResponse({ ok: false, error: "invalid_signature" }, { status: 401 });
  }

  let event;
  try {
    event = JSON.parse(payloadText);
  } catch {
    return jsonResponse({ ok: false, error: "invalid_json" }, { status: 400 });
  }

  const summary = summarizeStripeEvent(event);
  if (
    event.type === "checkout.session.completed" ||
    event.type === "checkout.session.async_payment_succeeded"
  ) {
    console.log("stripe_checkout_paid", JSON.stringify(summary));
  } else if (event.type === "checkout.session.async_payment_failed") {
    console.warn("stripe_checkout_payment_failed", JSON.stringify(summary));
  } else {
    console.log("stripe_webhook_accepted", JSON.stringify(summary));
  }
  return jsonResponse({ ok: true });
}

async function retrieveStripeCheckoutSession(env, sessionId) {
  const encodedSessionId = encodeURIComponent(sessionId);
  const stripeResponse = await fetch(
    `${STRIPE_CHECKOUT_SESSION_API_URL}/${encodedSessionId}`,
    {
      method: "GET",
      headers: {
        authorization: `Bearer ${env.STRIPE_SECRET_KEY}`,
      },
    },
  );
  const payload = await parseStripeJsonResponse(stripeResponse);
  if (!stripeResponse.ok) {
    return { ok: false, status: stripeResponse.status, payload };
  }
  return { ok: true, status: stripeResponse.status, payload };
}

async function handleStripeDelivery(request, env) {
  if (request.method !== "GET" && request.method !== "HEAD") {
    return jsonResponse({ ok: false, error: "method_not_allowed" }, { status: 405 });
  }

  if (!env.STRIPE_SECRET_KEY) {
    return jsonResponse({ ok: false, error: "stripe_not_configured" }, { status: 503 });
  }

  const url = new URL(request.url);
  const sessionId = url.searchParams.get("session_id") || "";
  if (!/^cs_(test|live)_[A-Za-z0-9_]+$/.test(sessionId)) {
    return jsonResponse({ ok: false, error: "invalid_session_id" }, { status: 400 });
  }

  const sessionResult = await retrieveStripeCheckoutSession(env, sessionId);
  if (!sessionResult.ok) {
    const summary = summarizeStripeError(
      sessionResult.status,
      sessionResult.payload,
    );
    console.warn("stripe_session_retrieve_failed", JSON.stringify(summary));
    return jsonResponse(
      { ok: false, error: "stripe_session_retrieve_failed" },
      { status: 502 },
    );
  }

  const session = sessionResult.payload;
  if (session.payment_status !== "paid") {
    return jsonResponse(
      { ok: false, error: "payment_not_complete", payment_status: session.payment_status },
      { status: 402 },
    );
  }

  const productSlug = session.metadata?.product_slug || "";
  const product = STRIPE_PRODUCTS[productSlug];
  if (!product) {
    return jsonResponse({ ok: false, error: "unknown_product" }, { status: 404 });
  }

  const artifact = await readPaidArtifact(env, product);
  if (!artifact.ok) {
    console.warn(
      "stripe_delivery_missing_artifact",
      JSON.stringify({
        product_slug: product.slug,
        artifact_key: product.artifactKey,
        error: artifact.error,
      }),
    );
    return jsonResponse(
      {
        ok: false,
        error: artifact.error,
        detail: `Missing paid asset for ${product.slug}.`,
      },
      { status: 503 },
    );
  }

  console.log(
    "stripe_delivery_artifact",
    JSON.stringify({ product_slug: product.slug, session_id: session.id || "" }),
  );
  const headers = new Headers({
    "content-type": "application/zip",
    "content-disposition": `attachment; filename="${product.downloadName}"`,
    "cache-control": "no-store",
    "x-robots-tag": "noindex, nofollow",
  });
  if (artifact.byteLength) {
    headers.set("content-length", String(artifact.byteLength));
  }
  return new Response(request.method === "HEAD" ? null : artifact.bytes, {
    status: 200,
    headers,
  });
}

async function handleCancelPage(request, env) {
  const response = await env.ASSETS.fetch(request);
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("text/html")) {
    return response;
  }

  const url = new URL(request.url);
  const product = STRIPE_PRODUCTS[url.searchParams.get("product") || ""];
  const title = product
    ? `Checkout canceled | ${product.name}`
    : "Checkout canceled | Zipper Tools";
  const body = (await response.text()).replace(
    /<title>.*?<\/title>/,
    `<title>${title}</title>`,
  );
  const headers = new Headers(response.headers);
  headers.set("cache-control", "no-store");
  return new Response(body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

function handleScanPage(request, env) {
  const url = new URL(request.url);
  if (url.search) {
    const headers = new Headers({
      location: `${url.origin}${SCAN_PATH}`,
      "cache-control": "no-store",
    });
    return new Response(null, { status: 302, headers });
  }
  return env.ASSETS.fetch(request);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (
      url.pathname === RETIRED_PAYHIP_PATH ||
      url.pathname.startsWith(`${RETIRED_PAYHIP_PATH}/`)
    ) {
      return jsonResponse({ ok: false, error: "not_found" }, { status: 404 });
    }
    if (url.pathname.startsWith(LEGACY_PAID_ASSET_PATH_PREFIX)) {
      return jsonResponse({ ok: false, error: "not_found" }, { status: 404 });
    }
    if (url.pathname === STRIPE_WEBHOOK_PATH) {
      return handleStripeWebhook(request, env);
    }
    if (url.pathname === STRIPE_DELIVERY_PATH) {
      return handleStripeDelivery(request, env);
    }
    if (url.pathname === CANCEL_PATH) {
      return handleCancelPage(request, env);
    }
    if (url.pathname === SCAN_PATH) {
      return handleScanPage(request, env);
    }

    const goRoute = matchGoRoute(url);
    if (goRoute) {
      return handleGoRoute(request, env, goRoute);
    }

    return env.ASSETS.fetch(request);
  },
};
