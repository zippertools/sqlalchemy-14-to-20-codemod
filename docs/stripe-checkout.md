# Stripe Checkout Setup

Last updated: 2026-09-26

This uses repo-controlled Stripe Checkout Sessions created by the Cloudflare
Worker.

## What Stripe owns

- secure card checkout
- receipts
- payment records
- refund/dispute dashboard
- webhook events

## What the Worker owns

- product names, descriptions, prices, and checkout routing from
  `site/product_catalog.mjs`
- `/go/...` conversion tracking
- Checkout Session creation
- Stripe webhook signature verification at `/stripe/webhook`
- post-payment KV artifact delivery at `/stripe/delivery`

The Worker currently uses inline Stripe `price_data`, so the product names and
prices come from `site/product_catalog.mjs`. Live Stripe Products and Prices also
exist in the connected account for Dashboard clarity and future price-ID
checkout migration.

## Promotion status

The May 2026 sale has ended. The Worker uses the regular catalog amounts below.

## Live Stripe catalog

Connected account: `acct_1TKBtaATQfsHIwbt`.

| Product | Product ID | Price ID | Amount |
| --- | --- | --- | --- |
| SQLAlchemy/Pydantic Fit Report Add-on | `prod_USv2vXjZURK1Dn` | `price_1TTzD1ATQfsHIwbtPxiF2vgp` | `$99.00` |
| SQLAlchemy 1.4 to 2.0 Migration Cleanup Pack | `prod_USv3EjBVYLIFCP` | `price_1TTzD8ATQfsHIwbto494wZjV` | `$299.99` |
| Migration Preset Bundle | `prod_USv31CiaOaWfeo` | `price_1TTzDEATQfsHIwbteoXWXTUU` | `$149.99` |
| Pydantic v1 to v2 Migration Cleanup Pack | `prod_USv3bxBilT5QCy` | `price_1TTzDMATQfsHIwbtb4yDHTnt` | `$249.99` |

## Dashboard setup

Use the Stripe account that will receive Zipper Tools payouts.

1. In Stripe, set the public business/profile details:
   - public business name: `Zipper Tools`
   - support email: `support@zippertools.org`
   - support site: `https://zippertools.org/`
   - statement descriptor: `ZIPPERTOOLS`
2. Start in test mode.
3. Copy the test secret key from **Developers -> API keys**.
4. Add a webhook endpoint in **Developers -> Webhooks**:
   - endpoint URL: `https://zippertools.org/stripe/webhook`
   - events:
     - `checkout.session.completed`
     - `checkout.session.async_payment_succeeded`
     - `checkout.session.async_payment_failed`
5. Copy the webhook signing secret.

## Cloudflare secrets

Set these as Worker secrets, never in `site/config.js` and never in git:

```powershell
npx.cmd wrangler secret put STRIPE_SECRET_KEY
npx.cmd wrangler secret put STRIPE_WEBHOOK_SECRET
```

Paid artifacts are stored as chunked base64 values in the private Cloudflare
Workers KV namespace bound as `PAID_ARTIFACTS`. The Worker verifies the Stripe
Checkout Session, reconstructs the matching ZIP from KV, and streams it to the
buyer.

Do not put paid ZIPs in the public repo or link to them directly from site
HTML.

The old `site/__stripe_paid_assets/` staging path is still blocked by the
Worker, but live delivery should use KV so no paid artifact has a public asset
URL.

Optional:

```powershell
npx.cmd wrangler secret put STRIPE_AUTOMATIC_TAX_ENABLED
```

Use `true` only after Stripe Tax is configured. Leave it unset while testing.

## Test checkout without changing production secrets

Use the authorized Zipper Tools sandbox (`acct_1TKBtaATQfsHIwbt`) and a local
Worker. Confirm livemode is false before any simulated payment. Use Stripe CLI
forwarding to exercise signed webhooks. A `/test` suffix on a production `/go/`
route is only a tracking label: it does NOT select Stripe test mode.

Create sessions with the local Worker's catalog, complete payment with Stripe's
test fixture mechanisms, verify unpaid delivery denial, receive the signed
completion webhook, and download the matching private KV artifact through the
local delivery handler. Install and use each downloaded package separately.
Test values and local results do not establish production checkout health.

Do not replace production Stripe secrets to run tests. No real purchase or refund
is authorized for the September 26 release. Before deployment, verify catalog
amounts using read-only live API requests and record the existing Worker version.
