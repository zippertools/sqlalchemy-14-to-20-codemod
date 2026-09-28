const SITE_URL = "https://zippertools.org";
const REPO_URL =
  "https://github.com/zippertools/sqlalchemy-14-to-20-codemod";
const PYDANTIC_REPO_URL = REPO_URL;
const PUBLIC_RELEASE_TAG = "v0.1.2";
const SUPPORT_EMAIL = "support@zippertools.org";
export const checkoutSale = Object.freeze({
  active: true,
  name: "Migration Sprint Sale",
  badge: "90% off",
  discountPercent: 90,
  stripeCouponId: "ro5ZyRLf",
  startsAt: "2026-05-06T07:00:00Z",
  endsAt: "2026-05-28T06:59:59Z",
  endsLabel: "May 27, 2026 at 11:59 PM Pacific",
  note:
    "90% off every listed paid product through May 27, 2026 at 11:59 PM Pacific. Discount is applied automatically in Stripe Checkout.",
});

const routes = Object.freeze({
  freeScan: "/go/free-scan",
  actionGuardFreeScan: "/go/actions-upgrade-guard-free",
  pydanticFreeScan: "/go/pydantic-free-scan",
  flatconfigFreeScan: "/go/flatconfig-free-scan",
  fitReport: "/go/fit-report",
  sa20: "/go/sa20-pack",
  sa20Preset: "/go/sa20-preset",
  pydantic: "/go/pydantic-v2-porter",
});

const prices = Object.freeze({
  freeScan: Object.freeze({ display: "$0", detail: "$0", amountCents: 0 }),
  fitReport: Object.freeze({
    display: "$99",
    detail: "$99 per team",
    amountCents: 9900,
    saleDisplay: "$9.90",
    saleDetail: "$9.90 during Migration Sprint Sale; normally $99 per team",
    saleAmountCents: 990,
  }),
  sa20: Object.freeze({
    display: "$299.99",
    detail: "$299.99 per team",
    amountCents: 29999,
    saleDisplay: "$30",
    saleDetail: "$30 during Migration Sprint Sale; normally $299.99 per team",
    saleAmountCents: 3000,
  }),
  sa20Preset: Object.freeze({
    display: "$149.99",
    detail: "$149.99 per team",
    amountCents: 14999,
    saleDisplay: "$15",
    saleDetail: "$15 during Migration Sprint Sale; normally $149.99 per team",
    saleAmountCents: 1500,
  }),
  pydantic: Object.freeze({
    display: "$249.99",
    detail: "$249.99 per team",
    amountCents: 24999,
    saleDisplay: "$25",
    saleDetail: "$25 during Migration Sprint Sale; normally $249.99 per team",
    saleAmountCents: 2500,
  }),
});

export function saleIsActive(now = Date.now()) {
  return checkoutSale.active && now >= Date.parse(checkoutSale.startsAt) && now <= Date.parse(checkoutSale.endsAt);
}

function salePrice(price) {
  return saleIsActive() ? price.saleDisplay || price.display : price.display;
}

function salePriceDetail(price) {
  return saleIsActive() ? price.saleDetail || price.detail : price.detail;
}

function saleCtaPrice(price) {
  return saleIsActive() ? `${salePrice(price)} sale` : salePrice(price);
}

const statuses = Object.freeze({
  available: "available",
  proofOnly: "proof_only",
});

function repoBlobUrl(path, content) {
  return `${REPO_URL}/blob/main/${path}?utm_source=zippertools&utm_medium=site&utm_campaign=free_scan&utm_content=${content}`;
}

function pydanticRepoBlobUrl(path, content) {
  return `${PYDANTIC_REPO_URL}/blob/main/products/pydantic-v2-porter/${path}?utm_source=zippertools&utm_medium=site&utm_campaign=free_scan&utm_content=${content}`;
}

const paidAssurances = Object.freeze([
  "Stripe Checkout handles secure payment and receipts.",
  "Download your purchased ZIP after payment.",
  "Runs locally; no hosted API, repo upload, or production credentials needed.",
  "14-day refund review for published-scope or delivery mismatches.",
]);

export const commerce = Object.freeze({
  checkoutProvider: "Stripe",
  supportEmail: SUPPORT_EMAIL,
  secureCheckoutNote: "Secure checkout is handled by Stripe.",
  checkoutLanguage: "Stripe Checkout handles secure payment and receipts.",
  refundLanguage: "14-day refund review for published-scope or delivery mismatches.",
  deliveryLanguage:
    "Download your purchased ZIP after payment.",
  localNoUploadClaim:
    "Runs locally; no hosted API, repo upload, or production credentials needed.",
  noSourceUploadClaim: "No source upload.",
  noHumanDeliveryLanguage: "No human service delivery.",
  saleName: checkoutSale.name,
  saleBadge: checkoutSale.badge,
  saleEndsLabel: checkoutSale.endsLabel,
  saleNote: checkoutSale.note,
});

export const products = Object.freeze({
  freeScan: Object.freeze({
    key: "freeScan",
    slug: "free-scan",
    checkoutSlug: "free-scan",
    name: "Free scan and report",
    shortName: "Free Scan",
    cardTitle: "Free Scan",
    description:
      "Run the public CLI, inspect supported findings, and qualify fit before spending money.",
    cardDescription:
      "Run the public CLI, inspect the report, and see whether the repo is a fit before spending money.",
    price: prices.freeScan.display,
    priceDetail: prices.freeScan.detail,
    amountCents: prices.freeScan.amountCents,
    currency: "usd",
    status: statuses.available,
    checkoutProvider: "GitHub",
    checkoutUrl: routes.freeScan,
    targetUrl: repoBlobUrl("docs/quickstart.md", "quickstart"),
    pricingId: "free-scan",
    offerLabel: "Free",
    stage: "Free",
    buyerQuestion: "Does my repo have the supported pattern?",
    offerName: "Free scan",
    ctaLabel: "Open quickstart",
    ctaLabelWithPrice: "Open quickstart",
    supportEmail: SUPPORT_EMAIL,
    bullets: Object.freeze([
      "Public CLI",
      "Public GitHub Action",
      "Core deterministic transforms",
      "Manual-review findings",
      "JSON migration report",
    ]),
    assurances: Object.freeze([
      "Local scan; no repository upload.",
      "Supported findings are separated from manual-review findings.",
    ]),
    pricingNote:
      "Start here before any checkout. The report is the buying evidence.",
    links: Object.freeze([
      Object.freeze({
        label: "Read public proof",
        href: "/proof/sqlalchemy-public-proof/",
      }),
    ]),
  }),
  actionGuard: Object.freeze({
    key: "actionGuard",
    slug: "actions-upgrade-guard",
    checkoutSlug: "actions-upgrade-guard",
    name: "GitHub Actions Upgrade Guard",
    shortName: "Action Guard",
    cardTitle: "GitHub Actions Upgrade Guard",
    description:
      "Local scanner for GitHub Actions workflow deprecations, runner drift, permissions risk, and source-linked manual guidance.",
    cardDescription:
      "Scan workflow YAML locally for deadline-sensitive Actions breakage and get source-linked findings plus manual migration guidance.",
    price: "",
    priceDetail: "Free scanner and proof page; paid SKU not listed yet",
    amountCents: null,
    currency: "usd",
    status: statuses.proofOnly,
    checkoutProvider: "GitHub",
    checkoutUrl: routes.actionGuardFreeScan,
    freeScanUrl: routes.actionGuardFreeScan,
    freeScanTargetUrl: repoBlobUrl(
      "products/actions-upgrade-guard/README.md",
      "actions-upgrade-guard",
    ),
    pricingId: "actions-upgrade-guard",
    offerLabel: "Free local scanner",
    stage: "Free local scanner",
    buyerQuestion: "Will my Actions workflows break on known platform changes?",
    offerName: "GitHub Actions upgrade scanner",
    ctaLabel: "Run free Action Guard scanner",
    ctaLabelWithPrice: "Run free Action Guard scanner",
    supportEmail: SUPPORT_EMAIL,
    bullets: Object.freeze([
      "Workflow YAML scanner",
      "Artifact/cache action deprecation findings",
      "Runner, Node runtime, and permission risk checks",
      "JSON and HTML reports",
      "Manual guidance; current rules make no automatic edits",
    ]),
    assurances: Object.freeze([
      "Runs locally with no GitHub token.",
      "No repository upload or hosted service account access.",
      "Uncertain workflow shapes are explicit findings.",
    ]),
    pricingNote:
      "Action Guard is free. No paid Action Guard package is currently offered.",
    links: Object.freeze([
      Object.freeze({
        label: "Read proof",
        href: "/proof/actions-upgrade-guard/",
      }),
      Object.freeze({
        label: "Open product page",
        href: "/products/actions-upgrade-guard/",
      }),
    ]),
  }),
  fitReport: Object.freeze({
    key: "fitReport",
    slug: "fit-report",
    checkoutSlug: "fit-report",
    name: "SQLAlchemy/Pydantic Fit Report Add-on",
    shortName: "SQLAlchemy/Pydantic Fit Report",
    cardTitle: "SQLAlchemy/Pydantic Fit Report",
    description:
      "Local software add-on that reads SQLAlchemy or Pydantic scanner output and produces an autonomous buy/do-not-buy migration fit summary.",
    cardDescription:
      "Run a software-only add-on against SQLAlchemy or Pydantic scanner output for a buy/do-not-buy recommendation.",
    price: salePrice(prices.fitReport),
    priceDetail: salePriceDetail(prices.fitReport),
    originalPrice: prices.fitReport.display,
    salePrice: prices.fitReport.saleDisplay,
    amountCents: prices.fitReport.amountCents,
    saleAmountCents: prices.fitReport.saleAmountCents,
    currency: "usd",
    status: statuses.available,
    checkoutProvider: commerce.checkoutProvider,
    checkoutUrl: routes.fitReport,
    pricingId: "fit-report",
    offerLabel: "Local download",
    stage: saleCtaPrice(prices.fitReport),
    buyerQuestion: "Is this SQLAlchemy or Pydantic repo worth automating before I buy the pack?",
    offerName: "SQLAlchemy/Pydantic fit report",
    ctaLabel: `Buy automated fit report - ${saleCtaPrice(prices.fitReport)}`,
    ctaLabelWithPrice: `Buy automated fit report - ${saleCtaPrice(prices.fitReport)}`,
    supportEmail: SUPPORT_EMAIL,
    bullets: Object.freeze([
      "Run the matching SQLAlchemy or Pydantic scanner locally and keep the report in your checkout.",
      "Use the add-on locally to summarize supported SQLAlchemy or Pydantic patterns.",
      "Generate manual-review risk notes and a buy/do-not-buy recommendation.",
      "No report submission, human review, consulting, or source upload.",
    ]),
    assurances: Object.freeze([
      "The displayed regular price matches the configured checkout amount.",
      "Software-only local report generation.",
      "No private source code, credentials, or reports need to be sent to a person.",
      commerce.refundLanguage,
    ]),
    pricingNote:
      `Use this only with SQLAlchemy or Pydantic scanner output. It is not listed for ESLint proof-only pages.`,
    links: Object.freeze([
      Object.freeze({
        label: "Read fit report details",
        href: "/products/fit-report/",
      }),
    ]),
  }),
  sa20: Object.freeze({
    key: "sa20",
    slug: "sa20-pack",
    checkoutSlug: "sa20-pack",
    name: "SQLAlchemy 1.4 to 2.0 Migration Cleanup Pack",
    shortName: "SQLAlchemy Cleanup Pack",
    cardTitle: "Cleanup Pack",
    description:
      "Deterministic local workflow for finding and cleaning up repeated SQLAlchemy 1.4 to 2.0 migration patterns.",
    cardDescription:
      "Apply deterministic rewrites locally for the documented SQLAlchemy cleanup subset, with reports and manual-review flags.",
    price: salePrice(prices.sa20),
    priceDetail: salePriceDetail(prices.sa20),
    originalPrice: prices.sa20.display,
    salePrice: prices.sa20.saleDisplay,
    amountCents: prices.sa20.amountCents,
    saleAmountCents: prices.sa20.saleAmountCents,
    currency: "usd",
    status: statuses.available,
    checkoutProvider: commerce.checkoutProvider,
    checkoutUrl: routes.sa20,
    pricingId: "sa20-pack",
    offerLabel: "One-time pack",
    stage: saleCtaPrice(prices.sa20),
    buyerQuestion: "Apply the repeated safe SQLAlchemy rewrites locally.",
    offerName: "SQLAlchemy cleanup pack",
    ctaLabel: `Buy cleanup pack - ${saleCtaPrice(prices.sa20)}`,
    ctaLabelWithPrice: `Buy cleanup pack - ${saleCtaPrice(prices.sa20)}`,
    supportEmail: SUPPORT_EMAIL,
    bullets: Object.freeze([
      "The displayed regular price matches the configured checkout amount.",
      "Deterministic local rewrites for the documented SQLAlchemy subset",
      "Preview/apply workflow with JSON report output",
      "Supported rewrite table and manual-review flags",
      "Rollback notes, rollout checklist, and manager summary",
      "No hosted API and no source-code upload",
    ]),
    assurances: paidAssurances,
    pricingNote:
      `Use this when the free scan proves the repo has repeated supported findings.`,
    links: Object.freeze([
      Object.freeze({
        label: "Read the SQLAlchemy migration tool overview",
        href: "/products/sa20-pack/",
      }),
    ]),
  }),
  sa20Preset: Object.freeze({
    key: "sa20Preset",
    slug: "sa20-preset",
    checkoutSlug: "sa20-preset",
    name: "Migration Preset Bundle",
    shortName: "Migration Preset Bundle",
    cardTitle: "Migration Preset Bundle",
    description:
      "Preset guidance, report templates, and rollout docs for teams turning a local migration scan into repeatable cleanup work.",
    cardDescription:
      "Add downloadable presets, report templates, and rollout notes for a repeatable software-only migration path.",
    price: salePrice(prices.sa20Preset),
    priceDetail: salePriceDetail(prices.sa20Preset),
    originalPrice: prices.sa20Preset.display,
    salePrice: prices.sa20Preset.saleDisplay,
    amountCents: prices.sa20Preset.amountCents,
    saleAmountCents: prices.sa20Preset.saleAmountCents,
    currency: "usd",
    status: statuses.available,
    checkoutProvider: commerce.checkoutProvider,
    checkoutUrl: routes.sa20Preset,
    pricingId: "sa20-preset",
    offerLabel: "Downloadable add-on",
    stage: saleCtaPrice(prices.sa20Preset),
    buyerQuestion: "Organize rollout docs and reusable presets.",
    offerName: "Preset bundle",
    ctaLabel: `Buy preset bundle - ${saleCtaPrice(prices.sa20Preset)}`,
    ctaLabelWithPrice: `Buy preset bundle - ${saleCtaPrice(prices.sa20Preset)}`,
    supportEmail: SUPPORT_EMAIL,
    bullets: Object.freeze([
      "The displayed regular price matches the configured checkout amount.",
      "Rollout checklist for staged SQLAlchemy 1.4-to-2.0 cleanup work",
      "Manager summary template that turns scan findings into a status update",
      "Migration-triage presets for common repo shapes",
      "Review buckets for supported / manual / unsupported findings",
      "Handoff notes for engineering teams picking up the cleanup",
      "License and support terms; no human delivery dependency",
    ]),
    assurances: Object.freeze([
      `Price: ${prices.sa20Preset.display}.`,
      commerce.checkoutLanguage,
      commerce.deliveryLanguage,
      "Downloadable docs and presets; no human delivery dependency.",
      commerce.refundLanguage,
    ]),
    pricingNote:
      `Use this when you want repeatable rollout structure without buying a service engagement.`,
    links: Object.freeze([
      Object.freeze({ label: "Read rollout kit details", href: "/products/sa20-preset/" }),
      Object.freeze({ label: "Compare all options", href: "/pricing" }),
    ]),
  }),
  pydantic: Object.freeze({
    key: "pydantic",
    slug: "pydantic-v2-porter",
    checkoutSlug: "pydantic-v2-porter",
    name: "Pydantic v1 to v2 Migration Cleanup Pack",
    shortName: "Pydantic Cleanup Pack",
    cardTitle: "Pydantic v1 to v2 Migration Cleanup Pack",
    description:
      "Deterministic local cleanup pack for supported Pydantic v1 to v2 imports, validators, config, and BaseSettings moves.",
    cardDescription:
      "Commercial cleanup pack for the documented Pydantic v1 to v2 subset, with fail-closed unsupported findings.",
    price: salePrice(prices.pydantic),
    priceDetail: salePriceDetail(prices.pydantic),
    originalPrice: prices.pydantic.display,
    salePrice: prices.pydantic.saleDisplay,
    amountCents: prices.pydantic.amountCents,
    saleAmountCents: prices.pydantic.saleAmountCents,
    currency: "usd",
    status: statuses.available,
    checkoutProvider: commerce.checkoutProvider,
    checkoutUrl: routes.pydantic,
    freeScanUrl: routes.pydanticFreeScan,
    freeScanTargetUrl: pydanticRepoBlobUrl("README.md", "pydantic-v2-porter"),
    pricingId: "pydantic-v2-porter",
    offerLabel: "Python migration pack",
    stage: saleCtaPrice(prices.pydantic),
    buyerQuestion: "Do the supported cleanup for Pydantic v1 to v2.",
    offerName: "Pydantic cleanup pack",
    ctaLabel: `Buy Pydantic cleanup pack - ${saleCtaPrice(prices.pydantic)}`,
    ctaLabelWithPrice: `Buy Pydantic cleanup pack - ${saleCtaPrice(prices.pydantic)}`,
    supportEmail: SUPPORT_EMAIL,
    bullets: Object.freeze([
      "The displayed regular price matches the configured checkout amount.",
      "Safe Pydantic v1 to v2 validator rewrites",
      "Safe Config to model_config conversion",
      "BaseSettings migration support for the documented subset",
      "Fail-closed unsupported findings",
    ]),
    assurances: paidAssurances,
    pricingNote:
      `Use this only after the Pydantic free scan shows the repo falls inside the documented supported subset.`,
    links: Object.freeze([
      Object.freeze({
        label: "Read the Pydantic pack details",
        href: "/products/pydantic-v2-porter/",
      }),
      Object.freeze({
        label: "See validator migration page",
        href: "/pydantic/validator-to-field-validator/",
      }),
    ]),
  }),
  flatconfig: Object.freeze({
    key: "flatconfig",
    slug: "flatconfig-lift",
    checkoutSlug: "flatconfig-lift",
    name: "ESLint Flat Config Migration Cleanup Pack",
    shortName: "ESLint Flat Config Pack",
    cardTitle: "ESLint Flat Config Migration Cleanup Pack",
    description:
      "Static-config migration cleanup pack for deterministic .eslintrc and package.json eslintConfig conversion into flat config.",
    cardDescription:
      "Static-config migration cleanup for deterministic .eslintrc and package.json eslintConfig conversion.",
    price: "",
    priceDetail: "Checkout not listed yet",
    amountCents: null,
    currency: "usd",
    status: statuses.proofOnly,
    checkoutProvider: "",
    checkoutUrl: "",
    freeScanUrl: routes.flatconfigFreeScan,
    freeScanTargetUrl: repoBlobUrl(
      "products/flatconfig-lift/README.md",
      "flatconfig-lift",
    ),
    pricingId: "flatconfig-lift",
    offerLabel: "Proof page only",
    stage: "Not listed",
    buyerQuestion: "Qualify static ESLint config migration fit.",
    offerName: "ESLint flat-config cleanup pack",
    ctaLabel: "Read proof",
    ctaLabelWithPrice: "Read proof",
    supportEmail: SUPPORT_EMAIL,
    bullets: Object.freeze([
      "Static JSON and YAML config discovery",
      "FlatCompat bridge generation in the supported subset",
      "Manual-review findings for JS configs and existing flat config files",
    ]),
    assurances: Object.freeze([
      "Use proof and docs before treating this as a purchase candidate.",
    ]),
    pricingNote: "Checkout is not listed yet.",
    links: Object.freeze([
      Object.freeze({
        label: "Read proof",
        href: "/proof/flatconfig-lift/",
      }),
    ]),
  }),
});

export const productOrder = Object.freeze([
  "actionGuard",
  "freeScan",
  "fitReport",
  "sa20",
  "sa20Preset",
  "pydantic",
  "flatconfig",
]);

export const checkoutProductKeys = Object.freeze([
  "fitReport",
  "sa20",
  "sa20Preset",
  "pydantic",
]);

export const checkoutProducts = Object.freeze(
  Object.fromEntries(
    checkoutProductKeys.map((key) => [products[key].checkoutSlug, products[key]]),
  ),
);

export const goRoutes = Object.freeze({
  [products.freeScan.checkoutUrl]: Object.freeze({
    kind: "free_scan",
    label: products.freeScan.checkoutSlug,
    target: products.freeScan.targetUrl,
  }),
  [products.actionGuard.freeScanUrl]: Object.freeze({
    kind: "free_scan",
    label: "actions-upgrade-guard-free",
    target: products.actionGuard.freeScanTargetUrl,
  }),
  [products.pydantic.freeScanUrl]: Object.freeze({
    kind: "free_scan",
    label: "pydantic-free-scan",
    target: products.pydantic.freeScanTargetUrl,
  }),
  [products.flatconfig.freeScanUrl]: Object.freeze({
    kind: "free_scan",
    label: "flatconfig-free-scan",
    target: products.flatconfig.freeScanTargetUrl,
  }),
  "/go/github-release": Object.freeze({
    kind: "trust",
    label: "github-release",
    target: `${REPO_URL}/releases/tag/${PUBLIC_RELEASE_TAG}?utm_source=zippertools&utm_medium=site&utm_campaign=trust&utm_content=${PUBLIC_RELEASE_TAG}`,
  }),
  [products.fitReport.checkoutUrl]: Object.freeze({
    kind: "checkout",
    label: products.fitReport.checkoutSlug,
    productSlug: products.fitReport.checkoutSlug,
  }),
  "/go/fit-review": Object.freeze({
    kind: "legacy",
    label: "fit-review",
    target: `${SITE_URL}${products.fitReport.checkoutUrl}`,
  }),
  [products.sa20.checkoutUrl]: Object.freeze({
    kind: "checkout",
    label: products.sa20.checkoutSlug,
    productSlug: products.sa20.checkoutSlug,
  }),
  [products.sa20Preset.checkoutUrl]: Object.freeze({
    kind: "checkout",
    label: products.sa20Preset.checkoutSlug,
    productSlug: products.sa20Preset.checkoutSlug,
  }),
  [products.pydantic.checkoutUrl]: Object.freeze({
    kind: "checkout",
    label: products.pydantic.checkoutSlug,
    productSlug: products.pydantic.checkoutSlug,
  }),
});

const aliases = Object.freeze({
  pack: "sa20",
  paidPack: "sa20",
  bundle: "sa20Preset",
  presetBundle: "sa20Preset",
  pydanticPack: "pydantic",
  pydanticV2Porter: "pydantic",
  free: "freeScan",
  freeStart: "freeScan",
  actionGuard: "actionGuard",
  actionsUpgradeGuard: "actionGuard",
  fit: "fitReport",
});

export function resolveProductKey(key) {
  return aliases[key] || key;
}

export function productByKey(key) {
  return products[resolveProductKey(key)] || null;
}

export function productBySlug(slug) {
  return (
    Object.values(products).find(
      (product) => product.slug === slug || product.checkoutSlug === slug,
    ) || null
  );
}

export function productTrackingUrl(product, source = "") {
  const baseUrl = product.checkoutUrl || product.links?.[0]?.href || "#";
  if (!source || !baseUrl.startsWith("/go/")) {
    return baseUrl;
  }
  return `${baseUrl}/${source}`;
}
