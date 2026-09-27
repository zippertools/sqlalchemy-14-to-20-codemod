from __future__ import annotations

import argparse
import json
import posixpath
import sys
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import date
from html import escape
from pathlib import Path, PurePosixPath
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.site_catalog import (
    ACTION_GUARD_FREE_SCAN_ROUTE,
    ACTION_GUARD_README_PATH,
    CHECKOUT_LANGUAGE,
    DELIVERY_LANGUAGE,
    FAMILY_DESCRIPTIONS,
    FAMILY_TITLES,
    FIT_REPORT_CTA,
    FIT_REPORT_LABEL,
    FIT_REPORT_PRICE,
    FIT_REPORT_PRODUCT_SLUGS,
    FIT_REPORT_ROUTE,
    FLATCONFIG_INSTALL_URL,
    GUIDES,
    INDEXNOW_KEY,
    LOCAL_NO_UPLOAD_LANGUAGE,
    PRODUCTS,
    PROOF_ONLY_CHECKOUT_NOTE,
    PUBLIC_RELEASE_TAG,
    PYDANTIC_INSTALL_URL,
    REFUND_LANGUAGE,
    REPO_URL,
    SA20_INSTALL_URL,
    SA20_PRESET_CHECKOUT_PATH,
    SA20_PRESET_NAME,
    SA20_PRESET_PRICE,
    SECURE_CHECKOUT_NOTE,
    SITE_NAME,
    SITE_URL,
    STATUS_AVAILABLE,
    STATUS_NOT_PURCHASABLE,
    STATUS_PROOF_ONLY,
    SUPPORT_EMAIL,
    GuidePage,
    ProductPage,
    price_detail,
    price_display,
)

# ruff: noqa: E501

INDEXABLE_STATIC_PAGES = (
    ("", "Home"),
    ("scan.html", "Scan"),
    ("pricing.html", "Pricing"),
    ("demo.html", "Demo"),
    ("guides/index.html", "Guides"),
    ("products/index.html", "Library"),
)

STATIC_PAGE_PATHS = (
    "scan.html",
    "pricing.html",
    "demo.html",
    "policies.html",
    "success.html",
    "cancel.html",
    "404.html",
)

FREE_SCAN_URL = (
    f"{REPO_URL}/blob/main/docs/quickstart.md"
    "?utm_source=zippertools&utm_medium=site&utm_campaign=free_scan&utm_content=quickstart"
)
PYDANTIC_FREE_SCAN_URL = (
    f"{REPO_URL}/blob/main/products/pydantic-v2-porter/README.md"
    "?utm_source=zippertools&utm_medium=site&utm_campaign=free_scan&utm_content=pydantic-v2-porter"
)
FLATCONFIG_FREE_SCAN_URL = (
    f"{REPO_URL}/blob/main/products/flatconfig-lift/README.md"
    "?utm_source=zippertools&utm_medium=site&utm_campaign=free_scan&utm_content=flatconfig-lift"
)
ACTION_GUARD_FREE_SCAN_URL = (
    f"{REPO_URL}/blob/main/{ACTION_GUARD_README_PATH}"
    "?utm_source=zippertools&utm_medium=site&utm_campaign=free_scan&utm_content=actions-upgrade-guard"
)
RELEASE_URL = (
    f"{REPO_URL}/releases/tag/{PUBLIC_RELEASE_TAG}"
    f"?utm_source=zippertools&utm_medium=site&utm_campaign=trust&utm_content={PUBLIC_RELEASE_TAG}"
)
PUBLIC_TRUST_BOUNDARY = (
    "Visible GitHub stars and forks are weak or absent social proof; treat the public repo as a fit signal, not as proof that the tool is safe for your repo.",
    "The public repo is scanner-first and does not expose the full paid apply engine.",
    "Public proof is intentionally narrow: a few supported examples plus fail-closed examples. Run on a branch and trust changes only after your own typecheck, build, and tests pass.",
)

PRICING_SECTION_IDS = {
    "fit-report": "fit-report",
    "sa20-pack": "sa20-pack",
    "sa20-preset": "sa20-preset",
    "pydantic-v2-porter": "pydantic-v2-porter",
}

FIT_REPORT_ADDON_LANGUAGE = (
    f"{FIT_REPORT_PRICE} {FIT_REPORT_LABEL} add-on is the lower-friction step "
    "when SQLAlchemy or Pydantic scan output is ambiguous."
)

REDIRECTS = (
    ("/favicon.ico", "/favicon.svg", 301),
    ("/go/free-scan", FREE_SCAN_URL, 302),
    (ACTION_GUARD_FREE_SCAN_ROUTE, ACTION_GUARD_FREE_SCAN_URL, 302),
    ("/go/pydantic-free-scan", PYDANTIC_FREE_SCAN_URL, 302),
    ("/go/flatconfig-free-scan", FLATCONFIG_FREE_SCAN_URL, 302),
    ("/go/github-release", RELEASE_URL, 302),
    # Paid checkout /go routes are owned by worker/index.mjs so they fail closed
    # instead of silently redirecting to pricing when the Worker is absent.
    ("/sqlalchemy-2-migration-scan", "/scan", 301),
    ("/sqlalchemy-2-migration-scan.html", "/scan", 301),
    ("/sqlalchemy-14-to-20-migration-pack", "/products/sa20-pack/", 301),
    ("/sqlalchemy-14-to-20-migration-pack.html", "/products/sa20-pack/", 301),
    ("/sqlalchemy-preset-bundle", "/pricing", 301),
    ("/sqlalchemy-preset-bundle.html", "/pricing", 301),
    ("/sqlalchemy-migration-tool", "/products/sa20-pack/", 301),
    ("/sqlalchemy-migration-tool.html", "/products/sa20-pack/", 301),
    ("/sqlalchemy-select-list-migration", "/sqlalchemy/select-list-syntax/", 301),
    ("/sqlalchemy-select-list-migration.html", "/sqlalchemy/select-list-syntax/", 301),
    ("/sqlalchemy-string-join-migration", "/sqlalchemy/string-join-paths/", 301),
    ("/sqlalchemy-string-join-migration.html", "/sqlalchemy/string-join-paths/", 301),
    (
        "/sqlalchemy-joinedload-string-migration",
        "/sqlalchemy/string-loader-options/",
        301,
    ),
    (
        "/sqlalchemy-joinedload-string-migration.html",
        "/sqlalchemy/string-loader-options/",
        301,
    ),
    ("/sqlalchemy-query-get-migration", "/sqlalchemy/session-query-get/", 301),
    ("/sqlalchemy-query-get-migration.html", "/sqlalchemy/session-query-get/", 301),
    (
        "/sqlalchemy-declarative-import-migration",
        "/sqlalchemy/declarative-imports/",
        301,
    ),
    (
        "/sqlalchemy-declarative-import-migration.html",
        "/sqlalchemy/declarative-imports/",
        301,
    ),
    ("/sqlalchemy-insert-values-migration", "/sqlalchemy/insert-values-kwargs/", 301),
    (
        "/sqlalchemy-insert-values-migration.html",
        "/sqlalchemy/insert-values-kwargs/",
        301,
    ),
    (
        "/sqlalchemy-joinedload-all-migration",
        "/sqlalchemy/joinedload-all-removed/",
        301,
    ),
    (
        "/sqlalchemy-joinedload-all-migration.html",
        "/sqlalchemy/joinedload-all-removed/",
        301,
    ),
    (
        "/sqlalchemy-session-query-migration",
        "/sqlalchemy/session-query-migration/",
        301,
    ),
    (
        "/sqlalchemy-session-query-migration.html",
        "/sqlalchemy/session-query-migration/",
        301,
    ),
    ("/sqlalchemy-engine-execute-removed", "/sqlalchemy/engine-execute-removed/", 301),
    (
        "/sqlalchemy-engine-execute-removed.html",
        "/sqlalchemy/engine-execute-removed/",
        301,
    ),
    ("/pydantic-v2-migration-pack", "/products/pydantic-v2-porter/", 301),
    ("/pydantic-v2-migration-pack.html", "/products/pydantic-v2-porter/", 301),
    (
        "/pydantic-validator-v2-migration",
        "/pydantic/validator-to-field-validator/",
        301,
    ),
    (
        "/pydantic-validator-v2-migration.html",
        "/pydantic/validator-to-field-validator/",
        301,
    ),
    ("/pydantic-basesettings-migration", "/pydantic/basesettings-moved/", 301),
    ("/pydantic-basesettings-migration.html", "/pydantic/basesettings-moved/", 301),
    ("/pydantic-root-validator-pre-migration", "/pydantic/root-validator-pre/", 301),
    (
        "/pydantic-root-validator-pre-migration.html",
        "/pydantic/root-validator-pre/",
        301,
    ),
    (
        "/optionengine-object-has-no-attribute-execute",
        "/sqlalchemy/optionengine-execute-error/",
        301,
    ),
    (
        "/optionengine-object-has-no-attribute-execute.html",
        "/sqlalchemy/optionengine-execute-error/",
        301,
    ),
    (
        "/sqlalchemy-optionengine-object-has-no-attribute-execute",
        "/sqlalchemy/optionengine-execute-error/",
        301,
    ),
    (
        "/attributeerror-optionengine-object-has-no-attribute-execute",
        "/sqlalchemy/optionengine-execute-error/",
        301,
    ),
    (
        "/engine-object-has-no-attribute-execute",
        "/sqlalchemy/engine-attribute-error-execute/",
        301,
    ),
    (
        "/engine-object-has-no-attribute-execute.html",
        "/sqlalchemy/engine-attribute-error-execute/",
        301,
    ),
    (
        "/sqlalchemy-engine-object-has-no-attribute-execute",
        "/sqlalchemy/engine-attribute-error-execute/",
        301,
    ),
    ("/legacyapiwarning-query-get", "/sqlalchemy/legacyapiwarning-query-get/", 301),
    (
        "/legacyapiwarning-query-get.html",
        "/sqlalchemy/legacyapiwarning-query-get/",
        301,
    ),
    (
        "/sqlalchemy-legacyapiwarning-query-get",
        "/sqlalchemy/legacyapiwarning-query-get/",
        301,
    ),
    (
        "/sqlalchemy-select-legacy-mode-warning",
        "/sqlalchemy/select-legacy-mode-warning/",
        301,
    ),
    (
        "/sqlalchemy-select-legacy-mode-warning.html",
        "/sqlalchemy/select-legacy-mode-warning/",
        301,
    ),
    ("/joinedload-all-is-not-defined", "/sqlalchemy/joinedload-all-nameerror/", 301),
    (
        "/joinedload-all-is-not-defined.html",
        "/sqlalchemy/joinedload-all-nameerror/",
        301,
    ),
    (
        "/sqlalchemy-2-migration-checklist",
        "/sqlalchemy/sqlalchemy-20-triage-checklist/",
        301,
    ),
    (
        "/sqlalchemy-2-migration-checklist.html",
        "/sqlalchemy/sqlalchemy-20-triage-checklist/",
        301,
    ),
    ("/sqlalchemy-2-codemod", "/sqlalchemy/sqlalchemy-manual-vs-codemod/", 301),
    ("/sqlalchemy-2-codemod.html", "/sqlalchemy/sqlalchemy-manual-vs-codemod/", 301),
    (
        "/basesettings-import-error-pydantic-v2",
        "/pydantic/basesettings-import-error/",
        301,
    ),
    (
        "/basesettings-import-error-pydantic-v2.html",
        "/pydantic/basesettings-import-error/",
        301,
    ),
    ("/pydantic-validator-deprecated", "/pydantic/validator-deprecation-warning/", 301),
    (
        "/pydantic-validator-deprecated.html",
        "/pydantic/validator-deprecation-warning/",
        301,
    ),
    (
        "/pydantic-class-config-deprecated",
        "/pydantic/config-class-deprecated-warning/",
        301,
    ),
    (
        "/pydantic-class-config-deprecated.html",
        "/pydantic/config-class-deprecated-warning/",
        301,
    ),
)


def canonical_url(path: str) -> str:
    return f"{SITE_URL}{public_path(path)}"


def is_page_path(path: str) -> bool:
    normalized = path.strip("/")
    return (
        normalized in {"", "index.html"}
        or normalized.endswith("/index.html")
        or normalized.endswith(".html")
    )


def public_path(path: str) -> str:
    normalized = path.strip("/")
    if normalized in {"", "index.html"}:
        return "/"
    if normalized.endswith("/index.html"):
        return f"/{normalized.removesuffix('index.html')}"
    if normalized.endswith(".html"):
        return f"/{normalized.removesuffix('.html')}"
    return f"/{normalized}"


def relative_href(from_path: str, to_path: str) -> str:
    if is_page_path(to_path):
        return public_path(to_path)
    start = posixpath.dirname(from_path) or "."
    return posixpath.relpath(to_path, start).replace("\\", "/")


def nav_html(path: str) -> str:
    repo_link = f'<a href="{REPO_URL}" data-repo-link>Repo</a>'
    return (
        '<header class="site-header"><div class="wrap nav">'
        f'<a class="brand" href="{relative_href(path, "index.html")}">Zipper Tools</a>'
        '<nav class="nav-links" aria-label="Primary">'
        f'<a href="{relative_href(path, "scan.html")}">Scan</a>'
        f'<a href="{relative_href(path, "products/index.html")}">Library</a>'
        f'<a href="{relative_href(path, "guides/index.html")}">Guides</a>'
        f'<a href="{relative_href(path, "pricing.html")}">Pricing</a>'
        f'<a href="{relative_href(path, "policies.html")}">Policies</a>'
        f"{repo_link}</nav></div></header>"
    )


def footer_html(path: str) -> str:
    contact_href = relative_href(path, "policies.html") + "#contact"
    return (
        '<footer class="site-footer"><div class="wrap footer-grid">'
        '<div><p class="footer-title">Zipper Tools</p>'
        '<p class="caption">Autonomous deadline-readiness tools for software teams.</p>'
        "</div>"
        '<div class="footer-links">'
        f'<a href="{relative_href(path, "scan.html")}">Scan</a>'
        f'<a href="{relative_href(path, "products/index.html")}">Library</a>'
        f'<a href="{relative_href(path, "guides/index.html")}">Guides</a>'
        f'<a href="{relative_href(path, "pricing.html")}">Pricing</a>'
        f'<a href="{relative_href(path, "demo.html")}">Demo</a>'
        f'<a href="{relative_href(path, "policies.html")}">Policies</a>'
        f'<a href="{REPO_URL}" data-repo-link>Repo</a>'
        f'<a href="{contact_href}">Contact</a>'
        "</div>"
        f'<p class="caption footer-note">Support: '
        f'<a href="{contact_href}">'
        f"<span data-contact-email>{SUPPORT_EMAIL}</span></a></p>"
        "</div></footer>"
    )


def breadcrumb_html(path: str, crumbs: list[tuple[str, str]]) -> str:
    items: list[str] = []
    for href, label in crumbs[:-1]:
        items.append(
            f'<li><a href="{relative_href(path, href)}">{escape(label)}</a></li>'
        )
    items.append(f'<li aria-current="page">{escape(crumbs[-1][1])}</li>')
    return (
        '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>'
        + "".join(items)
        + "</ol></nav>"
    )


def breadcrumb_schema(crumbs: list[tuple[str, str]]) -> dict[str, object]:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": idx,
                "name": label,
                "item": canonical_url(href),
            }
            for idx, (href, label) in enumerate(crumbs, start=1)
        ],
    }


def webpage_schema(title: str, description: str, path: str) -> dict[str, object]:
    return {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "url": canonical_url(path),
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": f"{SITE_URL}/"},
    }


def product_schema(product: ProductPage, path: str) -> dict[str, object]:
    schema: dict[str, object] = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.name,
        "category": "DeveloperApplication",
        "description": product.description,
        "url": canonical_url(path),
        "brand": {"@type": "Brand", "name": SITE_NAME},
    }
    if product.price:
        schema["offers"] = {
            "@type": "Offer",
            "price": price_display(product.price).removeprefix("$"),
            "priceCurrency": product.currency,
            "availability": f"https://schema.org/{product.availability}",
            "url": canonical_url(path),
            "seller": {"@type": "Organization", "name": SITE_NAME},
        }
    return schema


def software_application_schema(product: ProductPage, path: str) -> dict[str, object]:
    schema: dict[str, object] = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": product.name,
        "applicationCategory": "DeveloperApplication",
        "operatingSystem": "Windows, macOS, Linux",
        "description": product.description,
        "url": canonical_url(path),
    }
    if product.price:
        schema["offers"] = {
            "@type": "Offer",
            "price": price_display(product.price).removeprefix("$"),
            "priceCurrency": product.currency,
            "availability": f"https://schema.org/{product.availability}",
            "url": canonical_url(path),
        }
    return schema


def faq_schema(items: tuple[tuple[str, str], ...]) -> dict[str, object]:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answer,
                },
            }
            for question, answer in items
        ],
    }


def code_block(value: str) -> str:
    return f'<pre class="code-block"><code>{escape(value)}</code></pre>'


def clean_list_html(items: Iterable[str]) -> str:
    return (
        '<ul class="clean">'
        + "".join(f"<li>{escape(item)}</li>" for item in items)
        + "</ul>"
    )


def trust_boundary_section() -> str:
    return f"""      <section class="section">
        <article class="page-panel">
          <p class="kicker">Trust boundary</p>
          <h2>Do not trust this blindly with your project</h2>
          {clean_list_html(PUBLIC_TRUST_BOUNDARY)}
        </article>
      </section>
"""


def action_list_html(actions: Iterable[str]) -> str:
    filtered = [action for action in actions if action]
    if not filtered:
        return ""
    return (
        '<ul class="action-list">'
        + "".join(
            f'<li>{action}<span class="sr-only">.</span></li>' for action in filtered
        )
        + "</ul>"
    )


def product_by_slug(slug: str) -> ProductPage | None:
    return next((product for product in PRODUCTS if product.slug == slug), None)


def tracking_source(path: str, context: str) -> str:
    normalized = path.strip("/")
    normalized = normalized.removesuffix("/index.html").removesuffix(".html")
    normalized = normalized.replace("/", "-") or "home"
    return f"{context}-{normalized}"[:120]


def tracked_go_path(path: str, source: str) -> str:
    if not path.startswith("/go/"):
        return path
    return f"{path}/{source}"


def repo_doc_href(doc_path: str) -> str:
    if doc_path.startswith(("https://", "http://")):
        return doc_path
    return f"{REPO_URL}/blob/main/{doc_path}"


def free_scan_go_path(product: ProductPage | None, source: str) -> str:
    """Public buyer-path scan target.

    SQLAlchemy / generic free-scan CTAs route to the controlled `/scan` page
    so buyers stay on-site for the first step. Pydantic and ESLint CTAs keep
    their dedicated `/go/...` redirects to the matching public README so the
    user lands on the right scanner instead of the SQLAlchemy quickstart.
    """
    if product is not None and product.slug == "pydantic-v2-porter":
        return tracked_go_path("/go/pydantic-free-scan", source)
    if product is not None and product.slug == "flatconfig-lift":
        return tracked_go_path("/go/flatconfig-free-scan", source)
    if product is not None and product.slug == "actions-upgrade-guard":
        return tracked_go_path(ACTION_GUARD_FREE_SCAN_ROUTE, source)
    # SQLAlchemy + generic: keep buyers on a single canonical /scan page.
    # Query-tagged scan URLs have been a stale-cache failure mode, so source
    # attribution stays on /go routes and /scan itself remains cache-stable.
    return "/scan"


def supports_fit_report(product: ProductPage | None) -> bool:
    return product is not None and product.slug in FIT_REPORT_PRODUCT_SLUGS


def free_scan_cta_label(product: ProductPage | None) -> str:
    if product is None:
        return "Run the free local scanner"
    if product.slug == "pydantic-v2-porter":
        return "Run the Pydantic scan first"
    if product.slug == "flatconfig-lift":
        return "Run the static-config scan"
    if product.slug == "actions-upgrade-guard":
        return "Run the Action Guard scan"
    return "Run the SQLAlchemy scan first"


def checkout_cta_label(product: ProductPage) -> str:
    if product.slug == "fit-report":
        return "Buy automated fit report"
    if product.slug == "pydantic-v2-porter":
        return "Buy Pydantic cleanup pack"
    if product.slug == "sa20-preset":
        return "Buy preset bundle"
    return "Buy cleanup pack"


def product_price_line(product: ProductPage) -> str:
    return price_detail(product.price) if product.price else STATUS_NOT_PURCHASABLE


def product_buy_cta(product: ProductPage) -> str:
    return f"{checkout_cta_label(product)} - {price_display(product.price)}"


def product_page_path(product: ProductPage) -> str:
    return f"products/{product.slug}/index.html"


def product_proof_path(product: ProductPage) -> str:
    if product.slug == "sa20-pack":
        return "proof/sqlalchemy-public-proof/index.html"
    return f"proof/{product.slug}/index.html"


def has_product_proof(product: ProductPage) -> bool:
    return product.slug in {
        "actions-upgrade-guard",
        "sa20-pack",
        "pydantic-v2-porter",
        "flatconfig-lift",
    }


def pricing_section_href(path: str, product: ProductPage) -> str | None:
    anchor = PRICING_SECTION_IDS.get(product.slug)
    if anchor is None:
        return None
    return f"{relative_href(path, 'pricing.html')}#{anchor}"


@dataclass(frozen=True)
class ProductPageTemplate:
    headline: str
    subheadline: str
    cta_heading: str
    cta_copy: str
    what_this_fixes: tuple[str, ...]
    what_you_get: tuple[str, ...]
    use_this_if: tuple[str, ...]
    do_not_use_if: tuple[str, ...]
    delivery_steps: tuple[str, ...]
    support_note: str


def product_page_template(product: ProductPage) -> ProductPageTemplate:
    if product.slug == "actions-upgrade-guard":
        return ProductPageTemplate(
            headline="Find GitHub Actions breakage before it turns into a release blocker",
            subheadline=(
                "A local workflow scanner for deprecated artifact/cache actions, runner drift, Node runtime pressure, broad permissions, local actions, and fail-closed workflow YAML findings."
            ),
            cta_heading="Run the free scanner and review its findings.",
            cta_copy=(
                "Run the free local scanner and inspect its JSON/HTML report. Check the documented scope and manual migration guidance."
            ),
            what_this_fixes=(
                "Deprecated actions/upload-artifact@v3 and actions/download-artifact@v3 references.",
                "Retired actions/cache@v1 and actions/cache@v2 usage.",
                "Runner label drift such as ubuntu-20.04 retirement and macos-latest migration risk.",
                "Node runtime and temporary Node 20 opt-out findings for Actions.",
                "Missing or broad GITHUB_TOKEN permissions blocks.",
                "Invalid workflow YAML and local/composite action inventory that should not be guessed through.",
            ),
            what_you_get=(
                "Local scanner with JSON and HTML report output.",
                "Patch preview for deterministic artifact/cache action upgrades.",
                "Rule-pack version, source-backed findings, deadlines, fixability classification, and confidence scoring.",
                "Fail-closed findings for workflow shapes the scanner cannot patch safely.",
            ),
            use_this_if=product.who_it_is_for,
            do_not_use_if=product.not_for,
            delivery_steps=(
                "Open the public README and run the scanner against a local checkout.",
                "Review actions-upgrade-report.json and actions-upgrade-report.html.",
                "Apply only deterministic action-version patches when the diff matches your branch policy.",
                "No paid Action Guard package is currently offered.",
            ),
            support_note=(
                "No Action Guard purchase is available yet. Use the proof page and public scanner for fit questions; do not send private workflow files through support."
            ),
        )
    if product.slug == "fit-report":
        return ProductPageTemplate(
            headline="Get a local buy/no-buy recommendation before buying a cleanup pack",
            subheadline=(
                "A software-only add-on for SQLAlchemy or Pydantic scanner output: it summarizes supported findings, manual-review risk, and whether the repo is worth automating next."
            ),
            cta_heading="Buy this when the scan is promising but the purchase decision is still fuzzy.",
            cta_copy=(
                "Run the SQLAlchemy or Pydantic scanner first, then use the fit report add-on locally to turn the report into a manager-readable recommendation."
            ),
            what_this_fixes=(
                "Ambiguous scan output where supported and manual-review findings are mixed.",
                "Manager uncertainty about whether a cleanup pack is worth buying.",
                "The gap between a raw JSON scan report and a clear next-step recommendation.",
            ),
            what_you_get=(
                "Commercial ZIP with the local fit-report add-on.",
                "Buy/do-not-buy summary for SQLAlchemy or Pydantic scanner output.",
                "Supported finding counts, manual-review risk notes, and next-step recommendation.",
                "No human review, no report submission, and no source-code upload.",
            ),
            use_this_if=product.who_it_is_for,
            do_not_use_if=product.not_for,
            delivery_steps=(
                CHECKOUT_LANGUAGE,
                DELIVERY_LANGUAGE,
                LOCAL_NO_UPLOAD_LANGUAGE,
                "Run the add-on against scanner output you generated locally; keep the recommendation with your branch or manager notes.",
            ),
            support_note=(
                f"{REFUND_LANGUAGE} This add-on is not automatically credited toward a cleanup pack yet; treat it as a separate diagnostic purchase."
            ),
        )
    if product.slug == "sa20-pack":
        return ProductPageTemplate(
            headline="Clean up repeated SQLAlchemy 1.4 to 2.0 migration edits on a local branch",
            subheadline=(
                "A deterministic paid workflow for the SQLAlchemy cleanup that is repetitive, review-heavy, and safe to stage: Query.get, select([..]), simple string relationship paths, declarative imports, and legacy DML constructor syntax."
            ),
            cta_heading="Buy the apply workflow when the scan shows repeated supported cleanup.",
            cta_copy=(
                "The pack turns the supported scan buckets into a preview/apply migration run with a report your team can review before merge."
            ),
            what_this_fixes=(
                "session.query(Model).get(pk) to Session.get(Model, pk).",
                "select([columns]) legacy list syntax to direct select(columns).",
                "Simple string joins and loader options when the root mapped class is obvious.",
                "sqlalchemy.ext.declarative imports for declarative_base and declared_attr.",
                "Direct insert/update/delete constructor kwargs moved onto statement methods.",
            ),
            what_you_get=(
                "Commercial ZIP with the paid cleanup workflow and local CLI.",
                "Preview/apply commands, diff output, and JSON migration report.",
                "Supported rewrite table plus manual-review findings for unsupported SQLAlchemy patterns.",
                "Rollback checklist, manager summary, license/support terms, and buyer terms.",
            ),
            use_this_if=(
                "The free scan finds repeated supported SQLAlchemy cleanup across enough files to matter.",
                "You want a branch-local migration run with reviewable diffs and a structured report.",
                "Your team can run typecheck, tests, or build after the migration before merging.",
            ),
            do_not_use_if=product.not_for,
            delivery_steps=(
                CHECKOUT_LANGUAGE,
                DELIVERY_LANGUAGE,
                LOCAL_NO_UPLOAD_LANGUAGE,
                "Run the pack on a branch, inspect the diff/report, then use your normal validation commands before merge.",
            ),
            support_note=(
                f"{REFUND_LANGUAGE} Support is by email; include the scanner report and checkout email so the issue can be matched to the published scope."
            ),
        )
    if product.slug == "sa20-preset":
        return ProductPageTemplate(
            headline="Turn SQLAlchemy scan output into rollout docs your team can use",
            subheadline=(
                "A downloadable SQLAlchemy migration rollout kit: checklist, manager summary template, triage presets, review buckets, and handoff notes."
            ),
            cta_heading="Buy this when the team needs rollout structure, not code rewrites.",
            cta_copy=(
                "The preset bundle is a documentation product for teams that already know what the scan found and need a cleaner way to plan, report, and hand off the work."
            ),
            what_this_fixes=(
                "Unclear migration status after the scan runs.",
                "Managers asking for scope, risk, and next-step language.",
                "Reviewers needing supported/manual/unsupported buckets before cleanup starts.",
            ),
            what_you_get=(
                "Rollout checklist for staged SQLAlchemy 1.4-to-2.0 cleanup work.",
                "Manager summary template that turns scan findings into status language.",
                "Migration triage presets for common repo shapes.",
                "Review bucket template for supported, manual-review, and unsupported findings.",
                "Handoff note template for the engineers picking up the branch.",
            ),
            use_this_if=product.who_it_is_for,
            do_not_use_if=product.not_for,
            delivery_steps=(
                CHECKOUT_LANGUAGE,
                DELIVERY_LANGUAGE,
                "Downloadable docs and presets; no human service delivery.",
                "Use the templates with scanner output, branch notes, and your normal validation plan.",
            ),
            support_note=(
                f"{REFUND_LANGUAGE} This is a documentation/rollout kit, not the SQLAlchemy apply engine."
            ),
        )
    if product.slug == "pydantic-v2-porter":
        return ProductPageTemplate(
            headline="Move repetitive Pydantic v1 to v2 cleanup out of code review",
            subheadline=(
                "A deterministic paid workflow for direct imports, BaseSettings moves, simple validators, safe Config blocks, validate_arguments, and pre root validators in the documented Pydantic v2 subset."
            ),
            cta_heading="Buy the cleanup pack when direct v1 patterns are slowing the upgrade.",
            cta_copy=(
                f"The pack handles the mechanical Pydantic v2 edits locally and leaves alias-heavy or signature-heavy cases in manual review. The free scan link on this page opens the Pydantic scanner, not the SQLAlchemy scanner. The {FIT_REPORT_PRICE} {FIT_REPORT_LABEL} add-on covers SQLAlchemy and Pydantic scan output."
            ),
            what_this_fixes=(
                "Direct pydantic and pydantic.v1 imports when the imported symbols stay in the supported v2 subset.",
                "BaseSettings imports moved to pydantic-settings.",
                "Simple @validator decorators converted to @field_validator with classmethod handling.",
                "Supported class Config keys converted to model_config / ConfigDict with v2 key names.",
                "validate_arguments and root_validator(pre=True) cases in the safe subset.",
            ),
            what_you_get=(
                "Commercial ZIP with the paid Pydantic cleanup workflow and local CLI.",
                "Preview/apply commands for supported import, settings, validator, root-validator, and config rewrites.",
                "Supported rewrite table plus manual-review findings for alias-heavy imports, removed config keys, and signature-heavy validators.",
                "Demo report, public proof, rollback checklist, manager summary, and license/support terms.",
            ),
            use_this_if=(
                "The repo has repeated direct pydantic imports, BaseSettings usage, simple validators, or safe Config blocks.",
                "The migration pain is repetitive v1-to-v2 cleanup, not a custom semantic rewrite.",
                "Your team accepts explicit manual-review findings for validators that depend on values, field, config, each_item, or always.",
            ),
            do_not_use_if=product.not_for,
            delivery_steps=(
                CHECKOUT_LANGUAGE,
                DELIVERY_LANGUAGE,
                LOCAL_NO_UPLOAD_LANGUAGE,
                "Run the pack on a branch, inspect the diff/report, then use your normal validation commands before merge.",
            ),
            support_note=(
                f"{REFUND_LANGUAGE} Support is by email; include the scanner report and checkout email so the issue can be matched to the published scope."
            ),
        )
    return ProductPageTemplate(
        headline="Turn static legacy ESLint config into a flat-config starting point",
        subheadline=(
            "A proof-first workflow for the narrow static-config subset: .eslintrc JSON/YAML, package.json eslintConfig, and simple ignore migration. Dynamic JS config logic stays out of the automatic path."
        ),
        cta_heading="Use the proof page to qualify static-config fit before this is listed.",
        cta_copy=(
            "The public package identifies whether a repo belongs in the deterministic static-config subset; checkout is not listed for this product yet."
        ),
        what_this_fixes=(
            "Static .eslintrc JSON or YAML config discovery.",
            "package.json eslintConfig discovery for repos that have not moved to flat config.",
            "Simple ignore-pattern migration candidates.",
            "Manual-review findings for JS config logic, multiple config sources, existing flat config, and negated ignores.",
        ),
        what_you_get=(
            "Public scanner and proof page for static legacy ESLint config fit.",
            "Commercial-case notes for the FlatCompat bridge subset.",
            "Planned commercial deliverable: generated eslint.config.cjs and dependency guidance for supported static configs.",
            "Fail-closed reporting when the repo does not fit the static subset.",
        ),
        use_this_if=(
            "Your repo still uses a static .eslintrc JSON/YAML file or package.json eslintConfig.",
            "You want the first flat-config bridge pass before hand-tuning plugin behavior.",
            "You are comfortable treating JS-backed config and plugin-specific behavior as manual review.",
        ),
        do_not_use_if=product.not_for,
        delivery_steps=(
            "Use the public README and proof page today; no checkout is listed for this product.",
            "Run the scanner locally to decide whether the repo is in the static-config subset.",
            "When listed, delivery should follow the same local ZIP workflow as the paid cleanup packs.",
        ),
        support_note=(
            "No purchase is available from this page yet, so there is no paid refund path. Use the proof, README, and contact link for fit questions."
        ),
    )


def product_purchase_details(product: ProductPage) -> dict[str, tuple[str, ...]]:
    if product.slug == "fit-report":
        return {
            "buy_if": (
                "You already ran the SQLAlchemy or Pydantic scanner.",
                "The report has a meaningful mix of supported and manual-review findings.",
                "You need a local buy/do-not-buy recommendation before buying a full pack.",
            ),
            "includes": (
                "Local add-on workflow, not a hosted review.",
                "Supported finding summary, manual-review risk notes, and recommendation output.",
                "Checkout, delivery, refund, and support terms for the diagnostic ZIP.",
            ),
            "reassurance": (
                CHECKOUT_LANGUAGE,
                DELIVERY_LANGUAGE,
                LOCAL_NO_UPLOAD_LANGUAGE,
                "No source upload, report submission, or human service dependency.",
                REFUND_LANGUAGE,
            ),
        }
    if product.slug == "sa20-pack":
        return {
            "buy_if": (
                "The free scan shows repeated Query.get, select([..]), string join, string loader, declarative import, or DML constructor findings.",
                "The remaining supported cleanup is still expensive enough to justify a controlled local migration workflow.",
                "The team can run the migration on a branch and validate locally before merge.",
            ),
            "includes": (
                "Installable local CLI workflow, not a hosted black box.",
                "Preview/apply modes, diff output, and JSON migration report.",
                "Coverage notes, rollback checklist, manager summary, and buyer terms.",
            ),
            "reassurance": (
                CHECKOUT_LANGUAGE,
                DELIVERY_LANGUAGE,
                LOCAL_NO_UPLOAD_LANGUAGE,
                FIT_REPORT_ADDON_LANGUAGE,
                REFUND_LANGUAGE,
            ),
        }
    if product.slug == "pydantic-v2-porter":
        return {
            "buy_if": (
                "The repo has direct pydantic or pydantic.v1 imports, BaseSettings usage, safe Config blocks, or simple validators.",
                "The migration pain is repetitive v1-to-v2 cleanup, not a custom semantic rewrite.",
                "The team accepts manual-review findings for alias-heavy imports and signature-heavy validators.",
            ),
            "includes": (
                "Installable local CLI workflow, not a hosted black box.",
                "Supported validator, settings, import, and config rewrites.",
                "Demo report, public proof, coverage notes, rollback checklist, and buyer terms.",
            ),
            "reassurance": (
                CHECKOUT_LANGUAGE,
                DELIVERY_LANGUAGE,
                LOCAL_NO_UPLOAD_LANGUAGE,
                FIT_REPORT_ADDON_LANGUAGE,
                REFUND_LANGUAGE,
            ),
        }
    if product.slug == "sa20-preset":
        return {
            "buy_if": (
                "You already have scanner findings and need rollout structure.",
                "The buyer is an engineering lead or manager who needs a clearer migration note.",
                "You need templates and presets, not a code rewrite engine.",
            ),
            "includes": (
                "Rollout checklist, manager summary template, triage presets, and review buckets.",
                "Handoff note template for the team doing the branch work.",
                "License/support terms and Stripe-verified ZIP delivery.",
            ),
            "reassurance": (
                CHECKOUT_LANGUAGE,
                DELIVERY_LANGUAGE,
                "Downloadable documentation/presets; no human delivery dependency.",
                REFUND_LANGUAGE,
            ),
        }
    return {
        "buy_if": product.who_it_is_for,
        "includes": product.proof_points,
        "reassurance": (
            "Use proof and docs before treating this as a purchase candidate.",
        ),
    }


def render_purchase_panel(product: ProductPage, path: str, *, context: str) -> str:
    if not product.checkout_path or not product.price:
        return ""

    details = product_purchase_details(product)
    source = tracking_source(path, context)
    checkout_path = tracked_go_path(product.checkout_path, source)
    free_scan_path = free_scan_go_path(product, source)
    fit_report_action = (
        f'<a class="button secondary" href="{tracked_go_path(FIT_REPORT_ROUTE, source)}">{FIT_REPORT_CTA}</a>'
        if supports_fit_report(product)
        else ""
    )
    product_href = relative_href(path, product_page_path(product))
    proof_href = relative_href(path, product_proof_path(product))
    proof_action = f'<a class="button secondary" href="{proof_href}">Read proof</a>'
    pricing_href = pricing_section_href(path, product)
    pricing_action = (
        f'<a class="button secondary" href="{pricing_href}">See pricing</a>'
        if pricing_href
        else ""
    )

    heading = "Choose the lowest-risk next step."
    intro = (
        "Buy only after your local report shows repeated supported findings and a validation path the team can review."
        if context == "product"
        else "One matching page is not enough by itself. Run the local scan, then use the matching fit report add-on where listed or buy only when the same supported pattern appears often enough to matter."
    )
    if context != "product":
        primary_action = f'<a class="button" href="{free_scan_path}">{escape(free_scan_cta_label(product))}</a>'
        secondary_actions: tuple[str, ...] = (
            f'<a class="button secondary" href="{product_href}">Open product fit and price</a>',
            fit_report_action,
            proof_action,
            pricing_action,
            f'<a class="button secondary" href="{escape(checkout_path)}">{escape(product_buy_cta(product))}</a>',
        )
    else:
        primary_action = (
            fit_report_action.replace('class="button secondary"', 'class="button"', 1)
            if fit_report_action
            else f'<a class="button" href="{escape(checkout_path)}">Buy {escape(product.name)} - {escape(price_display(product.price))}</a>'
        )
        secondary_actions = (
            f'<a class="button secondary" href="{escape(checkout_path)}">Buy {escape(product.name)} - {escape(price_display(product.price))}</a>',
            proof_action,
            pricing_action,
        )
    secondary_actions_html = action_list_html(secondary_actions)

    return f"""      <section class="section">
        <article class="page-panel purchase-panel">
          <p class="kicker">Purchase fit</p>
          <h2>{escape(heading)}</h2>
          <p>{escape(intro)}</p>
          <div class="purchase-columns">
            <div>
              <h3>Buy if</h3>
              <ul class="clean">{"".join(f"<li>{escape(item)}</li>" for item in details["buy_if"])}</ul>
            </div>
            <div>
              <h3>What the workflow includes</h3>
              <ul class="clean">{"".join(f"<li>{escape(item)}</li>" for item in details["includes"])}</ul>
            </div>
            <div>
              <h3>Before checkout</h3>
              <ul class="clean">{"".join(f"<li>{escape(item)}</li>" for item in details["reassurance"])}</ul>
            </div>
          </div>
          <div class="page-actions purchase-actions">
            <div class="primary-cta">{primary_action}</div>
            <div class="secondary-cta-group">
              <p class="caption cta-group-label">Secondary options</p>
              {secondary_actions_html}
            </div>
          </div>
        </article>
      </section>"""


def guide_faq_items(
    guide: GuidePage,
    product: ProductPage | None,
) -> tuple[tuple[str, str], ...]:
    product_name = (
        product.name if product is not None else "the matching migration pack"
    )
    automation_answer = (
        "Automate only the supported subset: "
        + " ".join(guide.covers)
        + " Keep these cases in manual review: "
        + " ".join(guide.manual_review)
    )
    if supports_fit_report(product):
        buy_answer = (
            f"Use {product_name} only when this pattern repeats across enough files that manual cleanup is still costly. "
            f"Run the public scan or read the proof first. If the report shows ten or more supported findings, buy the pack or use the {FIT_REPORT_PRICE} {FIT_REPORT_LABEL} add-on; if unsupported findings dominate, keep the work manual."
        )
    else:
        buy_answer = (
            f"Use {product_name} only when this pattern repeats across enough files that manual cleanup is still costly. "
            "Run the public scan or read the proof first. The fit-report add-on is not listed for this proof-only product yet; if unsupported findings dominate, keep the work manual."
        )
    return (
        (f"What is the safest fix for {guide.search_term}?", guide.answer),
        (f"Can {guide.search_term} be automated?", automation_answer),
        (f"When should I buy {product_name}?", buy_answer),
    )


def render_faq_section(items: tuple[tuple[str, str], ...]) -> str:
    return f"""      <section class="section">
        <article class="page-panel">
          <p class="kicker">FAQ</p>
          <h2>Fast answers before you decide</h2>
          <div class="faq-list">
            {"".join(f"<div><h3>{escape(question)}</h3><p>{escape(answer)}</p></div>" for question, answer in items)}
          </div>
        </article>
      </section>"""


def render_direct_fix_section(guide: GuidePage) -> str:
    manual_boundary = " ".join(guide.manual_review[:2])
    return f"""      <section class="section">
        <article class="page-panel answer-panel">
          <p class="kicker">Start here</p>
          <div class="answer-grid">
            <div>
              <h2>The safe first move</h2>
              <p>{escape(guide.answer)}</p>
              <p class="caption">Stop before automation when: {escape(manual_boundary)}</p>
            </div>
            <div>
              <h3>Target shape</h3>
              {code_block(guide.after_code)}
            </div>
          </div>
        </article>
      </section>"""


def render_problem_scan_cta(
    guide: GuidePage,
    product: ProductPage | None,
    path: str,
) -> str:
    source = tracking_source(path, "guide-scan")
    free_scan_path = free_scan_go_path(product, source)
    product_href = (
        relative_href(path, product_page_path(product))
        if product is not None
        else relative_href(path, "products/index.html")
    )
    scan_intro = (
        f"Run the matching scanner locally first. If the report shows 10+ supported findings for this kind of cleanup, compare the paid workflow or use the {FIT_REPORT_PRICE} {FIT_REPORT_LABEL} add-on before buying the full pack."
        if supports_fit_report(product)
        else "Run the matching scanner locally first. The fit-report add-on is not listed for this proof-only product yet, so use the proof page and scanner output before treating it as a purchase candidate."
    )
    fit_report_action = (
        f'<a class="button secondary" href="{tracked_go_path(FIT_REPORT_ROUTE, source)}">{FIT_REPORT_CTA}</a>'
        if supports_fit_report(product)
        else ""
    )
    report_preview = (
        "Example scan summary\n"
        "supported_findings: 38\n"
        "manual_review_findings: 6\n"
        "files_uploaded: 0\n"
        "confidence: reviewable"
    )
    return f"""      <section class="section">
        <article class="conversion-panel">
          <div class="conversion-copy">
            <p class="kicker">Repo fit check</p>
            <h2>Want to know if your repo has this pattern?</h2>
            <p>{escape(scan_intro)}</p>
            <ul class="clean decision-list">
              <li>Local scan; no repository upload.</li>
              <li>Supported findings are separated from manual-review findings.</li>
              <li>Buy only when the repeated pattern is worth automating.</li>
            </ul>
          </div>
          <div class="conversion-actions">
            <a class="button" href="{free_scan_path}">{escape(free_scan_cta_label(product))}</a>
            <a class="button secondary" href="{relative_href(path, "demo.html")}">View example report</a>
            {fit_report_action}
            <a class="button secondary" href="{product_href}">See when to buy</a>
            {code_block(report_preview)}
          </div>
        </article>
      </section>"""


def render_evaluation_path_section(
    guide: GuidePage,
    product: ProductPage | None,
    path: str,
) -> str:
    if product is None:
        return ""

    details = product_purchase_details(product)
    product_href = relative_href(path, product_page_path(product))
    proof_href = relative_href(path, product_proof_path(product))
    pricing_href = pricing_section_href(path, product)
    fit_report_note = (
        f"If the scan output is ambiguous, use the {FIT_REPORT_PRICE} {FIT_REPORT_LABEL} add-on before buying the full pack."
        if supports_fit_report(product)
        else "The fit-report add-on is not listed for this proof-only product yet; use the proof page and scanner output before treating this as purchasable."
    )
    fit_report_action = (
        f'<a class="button secondary" href="{tracked_go_path(FIT_REPORT_ROUTE, tracking_source(path, "guide-fit"))}">{FIT_REPORT_CTA}</a>'
        if supports_fit_report(product)
        else ""
    )
    price_line = (
        f"Price: {price_detail(product.price)}."
        if product.price
        else "Current listed price is not published on the pricing page yet."
    )
    extra_action = ""
    if product.slug == "sa20-pack":
        extra_action = f'<a class="button secondary" href="{relative_href(path, "demo.html")}">See demo report</a>'
    actions_html = action_list_html(
        (
            f'<a class="button" href="{product_href}">Open product page</a>',
            fit_report_action,
            f'<a class="button secondary" href="{pricing_href}">See pricing</a>'
            if pricing_href
            else "",
            f'<a class="button secondary" href="{proof_href}">Read proof</a>',
            extra_action,
        )
    )
    return f"""      <section class="section">
        <div class="grid two">
          <article class="page-panel bridge-panel">
            <p class="kicker">Decision path</p>
            <h2>If this repeats across the repo, open the evaluation pages next.</h2>
            <p>{escape(product.summary)}</p>
            <ul class="clean">
              {"".join(f"<li>{escape(item)}</li>" for item in details["buy_if"][:2])}
              <li>{escape(fit_report_note)}</li>
            </ul>
          </article>
          <article class="page-panel bridge-panel">
            <p class="kicker">Before checkout</p>
            <h2>Product fit, proof, and price should all be one click away.</h2>
            <p>{escape(price_line)}</p>
            <div class="page-actions">
              {actions_html}
            </div>
          </article>
        </div>
      </section>"""


def layout(
    *,
    path: str,
    title: str,
    description: str,
    kicker: str,
    heading: str,
    body: str,
    crumbs: list[tuple[str, str]],
    schemas: Iterable[dict[str, object]],
) -> str:
    schema_json = json.dumps(
        [
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": SITE_NAME,
                "url": f"{SITE_URL}/",
            },
            webpage_schema(title, description, path),
            *schemas,
            breadcrumb_schema(crumbs),
        ],
        indent=2,
    )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{escape(title)} | {SITE_NAME}</title>
    <meta name="description" content="{escape(description)}" />
    <meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1" />
    <link rel="canonical" href="{canonical_url(path)}" />
    <meta property="og:title" content="{escape(title)}" />
    <meta property="og:description" content="{escape(description)}" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{canonical_url(path)}" />
    <meta property="og:image" content="{SITE_URL}/og-preview.svg" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{escape(title)}" />
    <meta name="twitter:description" content="{escape(description)}" />
    <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
    <link rel="stylesheet" href="{relative_href(path, "styles.css")}" />
    <script src="{relative_href(path, "config.js")}"></script>
    <script type="module" src="{relative_href(path, "app.js")}"></script>
    <script type="application/ld+json">
{schema_json}
    </script>
  </head>
  <body>
    {nav_html(path)}
    <main class="wrap">
      <section class="warning" id="launch-warning" aria-live="polite"></section>
      <section class="page-title">
        {breadcrumb_html(path, crumbs)}
        <p class="kicker">{escape(kicker)}</p>
        <h1>{escape(heading)}</h1>
        <p>{escape(description)}</p>
      </section>
      {body}
    </main>
    {footer_html(path)}
  </body>
</html>
"""


def clean_generated_text(value: str) -> str:
    return "\n".join(line.rstrip() for line in value.splitlines()) + "\n"


def render_guide(guide: GuidePage) -> tuple[str, str]:
    path = f"{guide.family}/{guide.slug}/index.html"
    product = product_by_slug(guide.product_slug)
    faq_items = guide_faq_items(guide, product)
    proof_cta = ""
    qualification_cta = ""
    if guide.product_slug == "sa20-pack":
        qualification_cta = (
            '<a class="button secondary" href="/scan">Run the free scan first</a>'
        )
        proof_cta = (
            f'<a class="button secondary" href="{relative_href(path, "proof/sqlalchemy-public-proof/index.html")}">'
            "Read public proof</a>"
        )
    narrow_actions = action_list_html(
        (
            f'<a class="button" href="{relative_href(path, f"products/{guide.product_slug}/index.html")}">Open the matching product page</a>',
            qualification_cta,
            proof_cta,
        )
    )
    # Get related guides from same family (top 3 as cards)
    related = [
        item
        for item in GUIDES
        if item.family == guide.family and item.slug != guide.slug
    ][:3]
    related_cards = "".join(
        f'<a class="topic-card" href="{relative_href(path, f"{item.family}/{item.slug}/index.html")}">'
        f"<strong>{escape(item.h1)}</strong><span>{escape(item.description)}</span></a>"
        for item in related
    )
    # Get all guides from same product for quick links
    product_guides = [
        item
        for item in GUIDES
        if item.product_slug == guide.product_slug and item.slug != guide.slug
    ]
    quick_links = ", ".join(
        f'<a href="{relative_href(path, f"{item.family}/{item.slug}/index.html")}">{escape(item.title.split(" in ")[0].split(" for ")[0])}</a>'
        for item in product_guides[:8]
    )
    more_fixes_html = ""
    if quick_links:
        product_label = product.name if product is not None else guide.product_slug
        more_fixes_html = f"""
      <section class="section">
        <article class="page-panel">
          <h3>More fixes in this product</h3>
          <p class="quick-links">{quick_links}</p>
          <p><a href="{relative_href(path, f"products/{guide.product_slug}/index.html")}">View all {escape(product_label)} guides</a></p>
        </article>
      </section>"""
    guide_purchase_html = (
        render_purchase_panel(product, path, context="guide")
        if product is not None
        else ""
    )
    extra_sections = (
        f"{render_faq_section(faq_items)}{guide_purchase_html}{more_fixes_html}"
    )
    body = f"""
{render_direct_fix_section(guide)}
{render_problem_scan_cta(guide, product, path)}
      <section class="section">
        <div class="grid two">
          <article class="page-panel">
            <p class="kicker">Why this page exists</p>
            <h2>{escape(guide.h1)}</h2>
            <p>{escape(guide.summary)}</p>
          </article>
          <article class="page-panel">
            <p class="kicker">Direct answer</p>
            <h2>What changes</h2>
            <p>{escape(guide.answer)}</p>
          </article>
        </div>
      </section>
      <section class="section">
        <div class="section-heading"><p class="kicker">Example</p><h2>Before and after</h2></div>
        <div class="grid two">
          <article class="page-panel"><h3>Before</h3>{code_block(guide.before_code)}</article>
          <article class="page-panel"><h3>After</h3>{code_block(guide.after_code)}</article>
        </div>
      </section>
{render_evaluation_path_section(guide, product, path)}
      <section class="section">
        <div class="grid three">
          <article class="page-panel"><h3>Typical symptoms</h3><ul class="clean">{"".join(f"<li>{escape(item)}</li>" for item in guide.symptoms)}</ul></article>
          <article class="page-panel"><h3>What the product covers</h3><ul class="clean">{"".join(f"<li>{escape(item)}</li>" for item in guide.covers)}</ul></article>
          <article class="page-panel"><h3>Manual-review boundary</h3><ul class="clean">{"".join(f"<li>{escape(item)}</li>" for item in guide.manual_review)}</ul></article>
        </div>
      </section>
      <section class="section">
        <div class="grid two">
          <article class="page-panel">
            <h3>Keep the migration narrow</h3>
            <p>Use the exact-problem guides as a triage layer, then decide whether the repo is inside the supported subset.</p>
            <div class="page-actions">
              {narrow_actions}
            </div>
          </article>
          <article class="page-panel">
            <h3>Related guides</h3>
            <div class="topic-list">{related_cards}</div>
          </article>
        </div>
      </section>
{extra_sections}
"""
    html = layout(
        path=path,
        title=guide.title,
        description=guide.description,
        kicker=FAMILY_TITLES[guide.family],
        heading=guide.h1,
        body=body,
        crumbs=[
            ("index.html", "Home"),
            ("guides/index.html", "Guides"),
            (f"{guide.family}/index.html", FAMILY_TITLES[guide.family]),
            (path, guide.h1),
        ],
        schemas=[faq_schema(faq_items)],
    )
    return path, html


def render_family_hub(family: str, guides: list[GuidePage]) -> tuple[str, str]:
    path = f"{family}/index.html"
    product_links = action_list_html(
        f'<a class="button secondary" href="{relative_href(path, f"products/{product.slug}/index.html")}">Open {escape(product.name)}</a>'
        for product in PRODUCTS
        if any(guide.product_slug == product.slug for guide in guides)
    )
    cards = "".join(
        f'<a class="topic-card" href="{relative_href(path, f"{guide.family}/{guide.slug}/index.html")}">'
        f"<strong>{escape(guide.h1)}</strong><span>{escape(guide.description)}</span></a>"
        for guide in guides
    )
    body = f"""
      <section class="section">
        <div class="section-heading"><p class="kicker">Problem pages</p><h2>{escape(FAMILY_DESCRIPTIONS[family])}</h2></div>
        <div class="page-actions">{product_links}</div>
        <div class="topic-list">{cards}</div>
      </section>
"""
    html = layout(
        path=path,
        title=FAMILY_TITLES[family],
        description=FAMILY_DESCRIPTIONS[family],
        kicker="Guides",
        heading=FAMILY_TITLES[family],
        body=body,
        crumbs=[
            ("index.html", "Home"),
            ("guides/index.html", "Guides"),
            (path, FAMILY_TITLES[family]),
        ],
        schemas=[],
    )
    return path, html


def render_guides_hub(grouped: dict[str, list[GuidePage]]) -> tuple[str, str]:
    path = "guides/index.html"
    cards = "".join(
        f'<a class="topic-card" href="{relative_href(path, f"{family}/index.html")}">'
        f"<strong>{escape(FAMILY_TITLES[family])}</strong><span>{escape(FAMILY_DESCRIPTIONS[family])} {len(guides)} pages.</span></a>"
        for family, guides in grouped.items()
    )
    body = f"""
      <section class="section">
        <div class="section-heading"><p class="kicker">Categories</p><h2>Exact-problem entry pages built for discovery</h2></div>
        <div class="topic-list">{cards}</div>
      </section>
"""
    html = layout(
        path=path,
        title="Migration Guides",
        description="Exact-problem migration guides for SQLAlchemy, Pydantic, and ESLint upgrade pain queries.",
        kicker="Guides",
        heading="Exact-problem migration guides",
        body=body,
        crumbs=[("index.html", "Home"), (path, "Guides")],
        schemas=[],
    )
    return path, html


def render_product_workflow_section(product: ProductPage, path: str) -> str:
    command_note = ""
    if product.slug == "actions-upgrade-guard":
        command = (
            f"git clone {REPO_URL}\n"
            "python -m pip install -e sqlalchemy-14-to-20-codemod/products/actions-upgrade-guard\n"
            "python -m actions_upgrade_guard.cli path/to/repo "
            "--report actions-upgrade-report.json "
            "--html-report actions-upgrade-report.html"
        )
        command_note = '<p class="caption">Use a local checkout. No GitHub token, hosted scan, or source upload is required.</p>'
        report = (
            "Actions Upgrade Guard Report\n"
            "status: manual_review_required\n"
            "rule_pack_version: 2026.09.26\n"
            "scanned_files: .github/workflows/build.yml\n"
            "blocking_findings: 3\n"
            "patches: 0"
        )
        diff = action_guard_patch_preview()
        rows = (
            ("artifact/cache action deprecations", "manual compatibility review"),
            ("runner label drift", "finding with deadline/source"),
            ("permissions risk", "manual review"),
            ("invalid YAML", "blocked/fail closed"),
        )
    elif product.slug == "fit-report":
        command = (
            f'python -m pip install "{SA20_INSTALL_URL}"\n'
            "python -m sa20_pack.cli . --report migration-report.json\n"
            "# Then run the purchased fit-report add-on against that scanner output."
        )
        command_note = (
            '<p class="caption">Use SQLAlchemy or Pydantic scanner output. '
            "Do not send private source code through support.</p>"
        )
        report = (
            "Fit report complete\n"
            "supported_findings: 38\n"
            "manual_review_findings: 6\n"
            "recommendation: good_fit (heuristic; review supported scope)\n"
            "next_step: preview deterministic rewrites"
        )
        diff = (
            "Manager summary\n"
            "Repo fit: yes, for the documented SQLAlchemy subset\n"
            "Why: repeated Query.get and select([..]) findings\n"
            "Risk: engine.execute remains manual review\n"
            "Manual alternative: use the free report and linked migration guidance"
        )
        rows = (
            ("SQLAlchemy scanner report", "supported input"),
            ("Pydantic scanner report", "supported input"),
            ("ESLint proof-only report", "out of scope"),
            ("Private source upload", "not required"),
        )
    elif product.slug == "sa20-preset":
        command = (
            f'python -m pip install "{SA20_INSTALL_URL}"\n'
            "python -m sa20_pack.cli . --report migration-report.json\n"
            "# Then fill the purchased rollout templates from the local report."
        )
        command_note = (
            '<p class="caption">This product is rollout documentation and presets, '
            "not the code rewrite engine.</p>"
        )
        report = (
            "Manager summary excerpt\n"
            "Supported cleanup findings: 38\n"
            "Manual-review findings: 6\n"
            "Rollout bucket: safe mechanical rewrites first\n"
            "Next step: run branch validation before merge"
        )
        diff = (
            "Handoff note preview\n"
            "1. Run scanner on migration branch\n"
            "2. Bucket supported/manual/unsupported findings\n"
            "3. Assign owner for manual-review SQLAlchemy execution cases\n"
            "4. Attach validation commands and merge criteria"
        )
        rows = (
            ("Rollout checklist", "included"),
            ("Manager summary template", "included"),
            ("Triage presets and review buckets", "included"),
            ("Code rewrite engine", "not included"),
        )
    elif product.slug == "pydantic-v2-porter":
        command = (
            f'python -m pip install "{PYDANTIC_INSTALL_URL}"\n'
            "python -m pydantic_v2_porter.cli path/to/repo --report migration-report.json"
        )
        command_note = (
            '<p class="caption">If installation fails, retry from the GitHub '
            f"quickstart or contact support at {SUPPORT_EMAIL}.</p>"
        )
        report = (
            "Scan complete\n"
            "supported_findings: 24\n"
            "manual_review_findings: 5\n"
            "files_uploaded: 0\n"
            "next_step: review diff preview"
        )
        diff = (
            "- from pydantic import BaseSettings, validator\n"
            "+ from pydantic import field_validator\n"
            "+ from pydantic_settings import BaseSettings\n"
            "\n"
            '-     @validator("email")\n'
            '+     @field_validator("email")\n'
            "+     @classmethod"
        )
        rows = (
            ("BaseSettings imports", "rewrite"),
            ("simple @validator", "rewrite"),
            ("safe class Config keys", "rewrite"),
            ("signature-heavy validators", "manual review"),
        )
    elif product.slug == "flatconfig-lift":
        command = (
            f'python -m pip install "{FLATCONFIG_INSTALL_URL}"\n'
            "python -m flatconfig_lift.cli path/to/repo --report migration-report.json"
        )
        command_note = (
            '<p class="caption">If installation fails, retry from the GitHub '
            f"quickstart or contact support at {SUPPORT_EMAIL}.</p>"
        )
        report = (
            "Scan complete\n"
            "supported_static_configs: 1\n"
            "manual_review_findings: 2\n"
            "files_uploaded: 0\n"
            "next_step: generate FlatCompat bridge in paid pack"
        )
        diff = (
            "- .eslintrc.json\n"
            "+ eslint.config.cjs\n"
            "\n"
            '+ const { FlatCompat } = require("@eslint/eslintrc");\n'
            '+ const legacyConfig = require("./.eslintrc.json");\n'
            "+ const compat = new FlatCompat({ baseDirectory: __dirname });\n"
            "+ module.exports = [...compat.config(legacyConfig)];"
        )
        rows = (
            ("static .eslintrc JSON/YAML", "rewrite"),
            ("package.json eslintConfig", "rewrite"),
            (".eslintignore", "migrate when simple"),
            (".eslintrc.js logic", "manual review"),
        )
    else:
        command = (
            f'python -m pip install "{SA20_INSTALL_URL}"\n'
            "python -m sa20_pack.cli . --report migration-report.json"
        )
        command_note = (
            '<p class="caption">If installation fails, retry from the GitHub '
            f"quickstart or contact support at {SUPPORT_EMAIL}.</p>"
        )
        report = (
            "Scan complete\n"
            "supported_findings: 38\n"
            "manual_review_findings: 6\n"
            "files_uploaded: 0\n"
            "next_step: preview deterministic rewrites"
        )
        diff = (
            "- user = session.query(User).get(user_id)\n"
            "+ user = session.get(User, user_id)\n"
            "\n"
            "- stmt = select([User.id, User.email])\n"
            "+ stmt = select(User.id, User.email)"
        )
        rows = (
            ("Query.get primary-key lookups", "rewrite"),
            ("select([..]) list syntax", "rewrite"),
            ("simple string joins/loaders", "rewrite"),
            ("engine.execute transaction choices", "manual review"),
        )

    if product.slug == "actions-upgrade-guard":
        apply_output = (
            "preview output\n"
            "files_changed: 0\n"
            "patches_generated: 0\n"
            "autofix_findings: none\n"
            "manual_review_findings: AUG001, AUG002"
        )
        validation_summary = (
            "validation summary\n"
            "pytest products/actions-upgrade-guard ... passed\n"
            "ruff check products/actions-upgrade-guard ... passed\n"
            "mypy src tests ... passed\n"
            "wheel build ... passed"
        )
        manager_summary = (
            "final manager summary\n"
            "Blocking workflow findings: 3\n"
            "No safe automatic patches; review upstream migration guidance.\n"
            "Manual review: runner labels and GITHUB_TOKEN permissions"
        )
    elif product.slug == "fit-report":
        apply_output = (
            "fit-report add-on complete\n"
            "input_report: migration-report.json\n"
            "supported_ratio: strong enough for paid cleanup consideration\n"
            "manual_review_risk: medium\n"
            "recommendation_written: manager-fit-summary.md"
        )
        validation_summary = (
            "validation summary\n"
            "scanner_report_loaded: passed\n"
            "unsupported_product_family_check: passed\n"
            "source_upload_required: false\n"
            "overall: recommendation ready for review"
        )
        manager_summary = (
            "final manager summary\n"
            "Decision: buy the cleanup pack if validation time is available.\n"
            "Why: repeated supported findings dominate the migration noise.\n"
            "Risk: manual-review findings remain visible and should be assigned."
        )
    elif product.slug == "sa20-preset":
        apply_output = (
            "preset bundle populated\n"
            "scanner_report: migration-report.json\n"
            "rollout_checklist: generated\n"
            "review_buckets: supported/manual-review/unsupported\n"
            "handoff_note: generated"
        )
        validation_summary = (
            "validation summary\n"
            "required_fields_present: passed\n"
            "checkout_artifact_scope: documentation only\n"
            "source_upload_required: false\n"
            "overall: rollout packet ready"
        )
        manager_summary = (
            "final manager summary\n"
            "Status: mechanical cleanup can start after branch setup.\n"
            "Scope: supported SQLAlchemy findings first.\n"
            "Risk: unsupported findings stay out of the rollout checklist."
        )
    elif product.slug == "pydantic-v2-porter":
        apply_output = (
            "apply output\n"
            "files_changed: 3\n"
            "transforms_applied: import_paths, basesettings, validators, config\n"
            "manual_review_findings: 5\n"
            "report_written: migration-report.json"
        )
        validation_summary = (
            "validation summary\n"
            "python -m compileall target_repo ... passed\n"
            "pytest selected_fixture_suite ... passed\n"
            "manual_review_export ... passed\n"
            "overall: branch validation still required"
        )
        manager_summary = (
            "final manager summary\n"
            "Supported cleanup findings: 24\n"
            "Manual-review findings: 5\n"
            "Next step: inspect diff, then run the buyer repo's own tests."
        )
    elif product.slug == "flatconfig-lift":
        apply_output = (
            "proof output\n"
            "static_configs_detected: 1\n"
            "generated_preview: eslint.config.cjs\n"
            "manual_review_findings: 2\n"
            "checkout_status: not listed"
        )
        validation_summary = (
            "validation summary\n"
            "json_yaml_parse: passed\n"
            "js_config_guard: passed\n"
            "existing_flat_config_guard: passed\n"
            "overall: proof-only fit signal"
        )
        manager_summary = (
            "final manager summary\n"
            "Decision: proof-only today, no checkout listed.\n"
            "Use when static config dominates.\n"
            "Do not use for JS config logic."
        )
    else:
        apply_output = (
            "apply output\n"
            "files_changed: 4\n"
            "transforms_applied: query_get, select_list_syntax, declarative_imports\n"
            "manual_review_findings: 6\n"
            "report_written: migration-report.json"
        )
        validation_summary = (
            "validation summary\n"
            "python -m compileall target_repo ... passed\n"
            "pytest selected_fixture_suite ... passed\n"
            "manual_review_export ... passed\n"
            "overall: branch validation still required"
        )
        manager_summary = (
            "final manager summary\n"
            "Supported cleanup findings: 38\n"
            "Manual-review findings: 6\n"
            "Next step: inspect diff, then run the buyer repo's own tests."
        )

    workflow_heading = (
        "See the migration deliverable before checkout."
        if product.checkout_path
        else "See the deliverable shape before it is listed."
    )
    workflow_caption = (
        "The value is the controlled workflow: scan, preview, apply supported rewrites, review manual findings, and validate on your branch."
        if product.checkout_path
        else "The free local tool produces findings and manual alternatives for the documented subset; no upgrades are auto-applied. No paid Action Guard package is currently offered."
        if product.slug == "actions-upgrade-guard"
        else "The public page is proof-first today; the commercial shape is a generated FlatCompat bridge for supported static configs."
    )
    table_rows = "".join(
        f"<tr><td>{escape(pattern)}</td><td>{escape(status)}</td></tr>"
        for pattern, status in rows
    )
    return f"""      <section class="section" id="example-workflow">
        <div class="section-heading">
          <p class="kicker">Example before/after</p>
          <h2>{escape(workflow_heading)}</h2>
          <p>Illustrative output format: sample counts and validation results below are not a run on your repository. Use the linked proof artifacts for recorded evidence. You can also make changes manually using the free report and migration guides.</p>
        </div>
        <div class="grid two">
          <article class="page-panel">
            <h3>{"Free scan commands" if product.slug in ("sa20-pack", "pydantic-v2-porter") else "Local command"}</h3>
            {code_block(command)}
            {command_note}
            <h3>Sample report</h3>
            {code_block(report)}
          </article>
          <article class="page-panel">
            <h3>Before/after diff preview</h3>
            {code_block(diff)}
            <p class="caption">{escape(workflow_caption)}</p>
          </article>
        </div>
        <div class="table-wrap">
          <table class="table">
            <thead><tr><th>Pattern</th><th>Behavior</th></tr></thead>
            <tbody>{table_rows}</tbody>
          </table>
        </div>
        <div class="grid three artifact-grid">
          <article class="page-panel">
            <h3>Apply output</h3>
            {code_block(apply_output)}
          </article>
          <article class="page-panel">
            <h3>Validation summary</h3>
            {code_block(validation_summary)}
          </article>
          <article class="page-panel">
            <h3>Final manager summary</h3>
            {code_block(manager_summary)}
          </article>
        </div>
      </section>"""


def render_product(product: ProductPage) -> tuple[str, str]:
    path = f"products/{product.slug}/index.html"
    template = product_page_template(product)
    product_source = tracking_source(path, "product")
    checkout_path = tracked_go_path(product.checkout_path, product_source)
    free_scan_path = free_scan_go_path(product, product_source)
    proof_link = (
        f'<a class="button secondary" href="{relative_href(path, product_proof_path(product))}">Read public proof</a>'
        if has_product_proof(product)
        else ""
    )
    release_button = ""
    if product.slug == "sa20-pack":
        release_button = f'<a class="button secondary" href="/go/github-release">Read {PUBLIC_RELEASE_TAG} release</a>'
    pricing_href = pricing_section_href(path, product)
    pricing_button = (
        f'<a class="button secondary" href="{pricing_href}">See pricing</a>'
        if pricing_href
        else ""
    )
    guides = [guide for guide in GUIDES if guide.slug in product.guide_slugs]
    guide_cards = "".join(
        f'<a class="topic-card" href="{relative_href(path, f"{guide.family}/{guide.slug}/index.html")}">'
        f"<strong>{escape(guide.h1)}</strong><span>{escape(guide.description)}</span></a>"
        for guide in guides
    )
    supporting_docs = tuple(
        (label, doc_path)
        for label, doc_path in product.docs
        if label != "Public proof" and not (label == "Pricing" and pricing_href)
    )
    docs_buttons = tuple(
        f'<a class="button secondary" href="{escape(repo_doc_href(doc_path))}" data-doc-path="{escape(doc_path)}">{escape(label)}</a>'
        for label, doc_path in supporting_docs
    )
    if product.checkout_path:
        price_suffix = (
            f" - {escape(price_display(product.price))}" if product.price else ""
        )
        checkout_label = checkout_cta_label(product)
        checkout_button = (
            f'<a class="button" href="{escape(checkout_path)}">'
            f"{escape(checkout_label)}{price_suffix}</a>"
        )
        if product.slug == "fit-report":
            free_scan_button = f'<a class="button secondary" href="{free_scan_path}">Run SQLAlchemy scan first</a>'
            pydantic_scan_button = (
                f'<a class="button secondary" href="{tracked_go_path("/go/pydantic-free-scan", product_source)}">'
                "Run Pydantic scan first</a>"
            )
        else:
            free_scan_button = (
                f'<a class="button secondary" href="{free_scan_path}">'
                f"{escape(free_scan_cta_label(product))}</a>"
            )
            pydantic_scan_button = ""
        fit_report_button = (
            f'<a class="button secondary" href="{tracked_go_path(FIT_REPORT_ROUTE, product_source)}">'
            f"{FIT_REPORT_CTA}</a>"
            if supports_fit_report(product)
            else ""
        )
        top_primary_action = checkout_button
        top_secondary_actions: tuple[str, ...] = (
            free_scan_button,
            pydantic_scan_button,
            fit_report_button,
        )
        checkout_heading = (
            "Buy the fit report"
            if product.slug == "fit-report"
            else "Buy the preset bundle"
            if product.slug == "sa20-preset"
            else "Buy the cleanup pack"
        )
        checkout_copy = (
            "Use checkout after you have scanner output and want a local recommendation before buying a larger pack."
            if product.slug == "fit-report"
            else "Use checkout when you need rollout templates and manager-ready notes, not code rewrites."
            if product.slug == "sa20-preset"
            else "Use checkout when the repo matches the supported subset and the cleanup is expensive enough to justify an apply workflow."
        )
        checkout_secondary_actions: tuple[str, ...] = (
            free_scan_button,
            pydantic_scan_button,
            fit_report_button,
        )
    else:
        checkout_button = '<span class="button disabled">Checkout not listed yet</span>'
        free_scan_button = (
            f'<a class="button secondary" href="{free_scan_path}">'
            f"{escape(free_scan_cta_label(product))}</a>"
        )
        fit_report_button = ""
        if product.slug == "actions-upgrade-guard":
            top_primary_action = free_scan_button.replace(
                'class="button secondary"', 'class="button"', 1
            )
            top_secondary_actions = (proof_link, *docs_buttons)
            checkout_heading = "Action Guard is free"
            checkout_copy = (
                "Use the free scanner and inspect the reproducible examples. "
                "No paid Action Guard package is currently offered."
            )
            checkout_secondary_actions = (proof_link, *docs_buttons)
        else:
            top_primary_action = proof_link
            top_secondary_actions = (free_scan_button, *docs_buttons)
            checkout_heading = "Checkout is not listed yet"
            checkout_copy = "Use the public proof and scanner to qualify the static-config subset before treating this as a purchase candidate."
            checkout_secondary_actions = (proof_link, free_scan_button, *docs_buttons)

    top_secondary_actions = (
        *top_secondary_actions,
        '<a class="button secondary" href="#example-workflow">View example before/after</a>',
    )
    top_secondary_actions_html = action_list_html(top_secondary_actions)
    secondary_actions_note = (
        '<p class="caption cta-group-label">Secondary options</p>'
        if top_secondary_actions_html
        else ""
    )
    checkout_secondary_actions_html = action_list_html(checkout_secondary_actions)
    checkout_secondary_note = (
        '<p class="caption cta-group-label">Secondary options</p>'
        if checkout_secondary_actions_html
        else ""
    )

    price_line = (
        f'<p class="price-line">Price: <strong>{escape(price_display(product.price))}</strong> per team.</p>'
        if product.price
        else '<p class="price-line">Checkout is not listed yet.</p>'
    )
    decision_bullets = (
        (
            "Local workflow with no repo upload.",
            "Recommendation output from scanner data you generated locally.",
            "Manual-review risk stays visible before a larger purchase.",
        )
        if product.slug == "fit-report"
        else (
            "Downloadable docs and presets; no repo upload.",
            "Templates turn scanner output into manager and reviewer notes.",
            "Manual-review findings stay visible instead of hidden.",
        )
        if product.slug == "sa20-preset"
        else (
            "Local workflow with no repo upload.",
            "Previewable changes and a structured report.",
            "Manual-review findings stay visible instead of hidden.",
        )
    )
    proof_actions = action_list_html(
        (proof_link, pricing_button, release_button, *docs_buttons)
    )
    workflow_section = render_product_workflow_section(product, path)
    deliverables_heading = (
        "After purchase, you receive"
        if product.checkout_path
        else "What this proof includes"
    )

    body = f"""
      <section class="section">
        <article class="conversion-panel product-hero-panel">
          <div class="conversion-copy">
            <p class="kicker">Primary CTA</p>
            <h2>{escape(template.cta_heading)}</h2>
            <p>{escape(template.cta_copy)}</p>
            <ul class="clean decision-list">{"".join(f"<li>{escape(item)}</li>" for item in decision_bullets)}</ul>
            {price_line}
          </div>
          <div class="conversion-actions">
            <div class="primary-cta">{top_primary_action}</div>
            <div class="secondary-cta-group">
              {secondary_actions_note}
              {top_secondary_actions_html}
            </div>
            {f'<p class="small">{escape(SECURE_CHECKOUT_NOTE)}</p>' if product.checkout_path else ""}
          </div>
        </article>
      </section>
{trust_boundary_section()}
      <section class="section">
        <div class="grid two">
          <article class="page-panel">
            <h2>What this fixes</h2>
            {clean_list_html(template.what_this_fixes)}
          </article>
          <article class="page-panel deliverables-box">
            <h2>{escape(deliverables_heading)}</h2>
            {clean_list_html(template.what_you_get)}
          </article>
        </div>
      </section>
{workflow_section}
      <section class="section">
        <div class="grid two">
          <article class="page-panel use-fit-box">
            <h2>Use this if</h2>
            {clean_list_html(template.use_this_if)}
          </article>
          <article class="page-panel">
            <h2>{"Public proof and fit signals" if has_product_proof(product) else "Fit signals and docs"}</h2>
            {clean_list_html(product.proof_points)}
            <div class="page-actions">{proof_actions}</div>
          </article>
        </div>
      </section>
      <section class="section">
        <article class="page-panel">
          <h2>Do not use this if</h2>
          {clean_list_html(template.do_not_use_if)}
        </article>
      </section>
      <section class="section">
        <div class="grid two">
          <article class="page-panel">
            <h2>How delivery works</h2>
            {clean_list_html(template.delivery_steps)}
          </article>
          <article class="page-panel">
            <h2>Refund/support note</h2>
            <p>{escape(template.support_note)}</p>
            <p class="caption">Support: <a href="mailto:{SUPPORT_EMAIL}" data-contact-link><span data-contact-email>{SUPPORT_EMAIL}</span></a></p>
          </article>
        </div>
      </section>
      <section class="section">
        <article class="conversion-panel checkout-panel">
          <div class="conversion-copy">
            <p class="kicker">Checkout CTA</p>
            <h2>{escape(checkout_heading)}</h2>
            <p>{escape(checkout_copy)}</p>
          </div>
          <div class="conversion-actions">
            <div class="primary-cta">{checkout_button}</div>
            <div class="secondary-cta-group">
              {checkout_secondary_note}
              {checkout_secondary_actions_html}
            </div>
            <p class="small">{escape(SECURE_CHECKOUT_NOTE if product.checkout_path else PROOF_ONLY_CHECKOUT_NOTE)}</p>
          </div>
        </article>
      </section>
      <section class="section">
        <div class="section-heading"><p class="kicker">Related fixes</p><h2>Exact-problem guides for this product</h2></div>
        <div class="topic-list">{guide_cards}</div>
      </section>
"""
    html = layout(
        path=path,
        title=product.name,
        description=template.subheadline,
        kicker="Product",
        heading=template.headline,
        body=body,
        crumbs=[
            ("index.html", "Home"),
            ("products/index.html", "Library"),
            (path, product.name),
        ],
        schemas=[
            product_schema(product, path),
            software_application_schema(product, path),
        ],
    )
    return path, html


def render_products_hub() -> tuple[str, str]:
    path = "products/index.html"
    catalog_source = tracking_source(path, "catalog-card")
    product_lookup = {product.slug: product for product in PRODUCTS}
    action_guard = product_lookup["actions-upgrade-guard"]
    action_guard_section = f"""
      <section class="section">
        <article class="conversion-panel product-hero-panel">
          <div class="conversion-copy">
            <p class="kicker">Free local scanner</p>
            <h2>{escape(action_guard.name)} is available as a free local scanner.</h2>
            <p>{escape(action_guard.summary)}</p>
          </div>
          <div class="conversion-actions">
            <a class="button" href="{tracked_go_path(ACTION_GUARD_FREE_SCAN_ROUTE, catalog_source)}">Run free Action Guard scanner</a>
            <a class="button secondary" href="{relative_href(path, "products/actions-upgrade-guard/index.html")}">Open product page</a>
            <a class="button secondary" href="{relative_href(path, "proof/actions-upgrade-guard/index.html")}">Read proof</a>
          </div>
        </article>
      </section>"""
    available_cards = (
        {
            "name": product_lookup["fit-report"].name,
            "status": STATUS_AVAILABLE,
            "status_class": "available",
            "outcome": "Turn SQLAlchemy or Pydantic scanner output into a local buy/do-not-buy recommendation before a larger purchase.",
            "price": product_price_line(product_lookup["fit-report"]),
            "href": relative_href(
                path, product_page_path(product_lookup["fit-report"])
            ),
            "cta": "View fit report details",
            "buy_href": tracked_go_path(
                product_lookup["fit-report"].checkout_path, catalog_source
            ),
            "buy_cta": product_buy_cta(product_lookup["fit-report"]),
            "checkout_note": SECURE_CHECKOUT_NOTE,
        },
        {
            "name": product_lookup["sa20-pack"].name,
            "status": STATUS_AVAILABLE,
            "status_class": "available",
            "outcome": "Apply repeated safe SQLAlchemy 1.4 to 2.0 cleanup patterns locally after the free scan proves fit.",
            "price": product_price_line(product_lookup["sa20-pack"]),
            "href": relative_href(path, product_page_path(product_lookup["sa20-pack"])),
            "cta": "View SQLAlchemy pack details",
            "buy_href": tracked_go_path(
                product_lookup["sa20-pack"].checkout_path, catalog_source
            ),
            "buy_cta": product_buy_cta(product_lookup["sa20-pack"]),
            "checkout_note": SECURE_CHECKOUT_NOTE,
        },
        {
            "name": product_lookup["pydantic-v2-porter"].name,
            "status": STATUS_AVAILABLE,
            "status_class": "available",
            "outcome": "Clean up supported Pydantic v1 to v2 imports, validators, config, and BaseSettings moves.",
            "price": product_price_line(product_lookup["pydantic-v2-porter"]),
            "href": relative_href(
                path, product_page_path(product_lookup["pydantic-v2-porter"])
            ),
            "cta": "View Pydantic pack details",
            "buy_href": tracked_go_path(
                product_lookup["pydantic-v2-porter"].checkout_path, catalog_source
            ),
            "buy_cta": product_buy_cta(product_lookup["pydantic-v2-porter"]),
            "checkout_note": SECURE_CHECKOUT_NOTE,
        },
        {
            "name": SA20_PRESET_NAME,
            "status": STATUS_AVAILABLE,
            "status_class": "available",
            "outcome": "Add reusable SQLAlchemy rollout presets, richer report templates, and manager-ready migration notes.",
            "price": price_detail(SA20_PRESET_PRICE),
            "href": relative_href(
                path, product_page_path(product_lookup["sa20-preset"])
            ),
            "cta": "View rollout kit details",
            "buy_href": tracked_go_path(SA20_PRESET_CHECKOUT_PATH, catalog_source),
            "buy_cta": f"Buy preset bundle - {price_display(SA20_PRESET_PRICE)}",
            "checkout_note": SECURE_CHECKOUT_NOTE,
        },
    )
    proof_cards = (
        {
            "name": product_lookup["flatconfig-lift"].name,
            "status": STATUS_PROOF_ONLY,
            "status_class": "proof-only",
            "outcome": "Review the static ESLint config migration proof and fit boundaries before this becomes a listed checkout product.",
            "price": product_price_line(product_lookup["flatconfig-lift"]),
            "href": relative_href(path, "proof/flatconfig-lift/index.html"),
            "cta": "Read proof page",
            "note": "Proof only - checkout not live yet.",
        },
    )
    coming_soon_cards: tuple[dict[str, str], ...] = ()

    def render_catalog_card(card: dict[str, str]) -> str:
        checkout_note = (
            f'<p class="small">{escape(card["checkout_note"])}</p>'
            if card.get("checkout_note")
            else ""
        )
        status_note = (
            f'<p class="small status-note">{escape(card["note"])}</p>'
            if card.get("note")
            else ""
        )
        return f"""
          <article class="catalog-card">
            <div class="catalog-card-top">
              <span class="status-label {escape(card["status_class"])}">{escape(card["status"])}</span>
              <span class="catalog-price">{escape(card["price"])}</span>
            </div>
            <h3><a href="{escape(card["href"])}">{escape(card["name"])}</a></h3>
            <p>{escape(card["outcome"])}</p>
            {status_note}
            <div class="page-actions">
              <a class="button secondary" href="{escape(card["href"])}">{escape(card["cta"])}</a>
              {f'<a class="button" href="{escape(card["buy_href"])}">{escape(card["buy_cta"])}</a>' if card.get("buy_href") else ""}
            </div>
            {checkout_note}
          </article>"""

    available_html = "".join(render_catalog_card(card) for card in available_cards)
    coming_soon_html = "".join(render_catalog_card(card) for card in coming_soon_cards)
    proof_html = "".join(render_catalog_card(card) for card in proof_cards)
    coming_soon_section = (
        f"""
      <section class="section">
        <div class="section-heading"><p class="kicker">Coming soon</p><h2>Future products stay separate until checkout is ready.</h2></div>
        <div class="catalog-grid">{coming_soon_html}</div>
      </section>"""
        if coming_soon_html
        else ""
    )
    preset_deliverables = (
        '<section class="section">'
        '<article class="page-panel deliverables-box">'
        '<p class="kicker">Migration Preset Bundle</p>'
        "<h2>After purchase, you receive</h2>"
        '<ul class="clean">'
        "<li>Rollout checklist for staged SQLAlchemy 1.4-to-2.0 cleanup work.</li>"
        "<li>Manager summary template that turns scan findings into a status update.</li>"
        "<li>Migration-triage presets for common repo shapes.</li>"
        "<li>Review buckets for supported / manual / unsupported findings.</li>"
        "<li>Handoff notes for engineering teams picking up the cleanup.</li>"
        "<li>License and support terms; no human delivery dependency.</li>"
        "</ul>"
        "<h3>Sample preview</h3>"
        '<pre class="code-block"><code>Manager summary excerpt\n'
        "Supported cleanup findings: 38\n"
        "Manual-review findings: 6\n"
        "Rollout bucket: safe mechanical rewrites first\n"
        "Review buckets: supported / manual-review / unsupported\n"
        "Next step: run branch validation before merge</code></pre>"
        f'<p class="caption">Support: '
        f'<a href="mailto:{SUPPORT_EMAIL}" data-contact-link>'
        f"<span data-contact-email>{SUPPORT_EMAIL}</span></a></p>"
        "</article>"
        "</section>"
    )
    body = f"""
{action_guard_section}
      <section class="section">
        <article class="page-panel">
          <p class="kicker">Migration Library</p>
          <h2>Existing packages stay live as proof and buyer-fit assets.</h2>
          <p>Compare supported migration patterns, inspect examples, and run a local scan before choosing a tool.</p>
        </article>
      </section>
      <section class="section">
        <div class="section-heading"><p class="kicker">{escape(STATUS_AVAILABLE)}</p><h2>Migration Library packages, each with a real detail page.</h2></div>
        <div class="catalog-grid">{available_html}</div>
      </section>
{preset_deliverables}
{coming_soon_section}
      <section class="section">
        <div class="section-heading"><p class="kicker">Labs and proofs</p><h2>Useful proof, separate from purchasable products.</h2></div>
        <div class="catalog-grid proof-grid">{proof_html}</div>
      </section>
"""
    html = layout(
        path=path,
        title="Product Library",
        description="Local scanners and migration tools for GitHub Actions, SQLAlchemy, Pydantic, and static ESLint configurations.",
        kicker="Library",
        heading="Local scanners and migration tools",
        body=body,
        crumbs=[("index.html", "Home"), (path, "Library")],
        schemas=[],
    )
    return path, html


def render_home() -> tuple[str, str]:
    path = "index.html"
    product = product_by_slug("actions-upgrade-guard")
    if product is None:
        raise RuntimeError("actions-upgrade-guard product is missing")
    source = tracking_source(path, "home-well")
    action_cards = "".join(
        f"""
          <article class="page-panel">
            <h3>{escape(title)}</h3>
            <p>{escape(copy)}</p>
          </article>"""
        for title, copy in (
            (
                "Supported workflow checks",
                "Check workflow references against the documented artifact, cache, runner, runtime, and permission rules.",
            ),
            (
                "Local evidence first",
                "The free scanner reads workflow YAML locally and writes JSON/HTML findings with source links and fixability labels.",
            ),
            (
                "Free scanner available",
                "Action Guard is available as a free local tool. No paid Action Guard package is currently offered.",
            ),
        )
    )
    library_cards = "".join(
        f"""
          <a class="topic-card" href="{href}">
            <strong>{escape(label)}</strong>
            <span>{escape(copy)}</span>
          </a>"""
        for label, href, copy in (
            (
                "SQLAlchemy cleanup pack",
                "/products/sa20-pack/",
                "Scan and inspect supported SQLAlchemy 1.4 to 2.0 cleanup patterns.",
            ),
            (
                "Pydantic v2 porter",
                "/products/pydantic-v2-porter/",
                "Check supported direct Pydantic v1 to v2 migration patterns.",
            ),
            (
                "Flatconfig Lift",
                "/proof/flatconfig-lift/",
                "Inspect examples and limitations for static ESLint configuration migration.",
            ),
        )
    )
    body = f"""
      <section class="section">
        <article class="conversion-panel product-hero-panel">
          <div class="conversion-copy">
            <p class="kicker">Featured tool</p>
            <h2>GitHub Actions Upgrade Guard</h2>
            <p>Scan GitHub Actions workflows for supported maintenance findings and emit source-linked findings, manual migration guidance, and a manager-readable report without hosted services or source upload.</p>
            <div class="badge-row">
              <span class="badge">Runs locally</span>
              <span class="badge">No GitHub token</span>
              <span class="badge">Patch preview</span>
              <span class="badge">Fail closed</span>
            </div>
          </div>
          <div class="conversion-actions">
            <div class="primary-cta">
              <a class="button" href="{tracked_go_path(ACTION_GUARD_FREE_SCAN_ROUTE, source)}">Run free Action Guard scanner</a>
            </div>
            <div class="secondary-cta-group">
              <p class="caption cta-group-label">Secondary options</p>
              <a class="button secondary" href="/proof/actions-upgrade-guard/">Read proof and artifacts</a>
              <a class="button secondary" href="/products/actions-upgrade-guard/">Open product page</a>
            </div>
          </div>
        </article>
      </section>
{trust_boundary_section()}
      <section class="section">
        <div class="section-heading">
          <p class="kicker">Workflow checks</p>
          <h2>What the scanner provides</h2>
        </div>
        <div class="grid three">{action_cards}</div>
      </section>
      <section class="section">
        <div class="grid two">
          <article class="page-panel">
            <p class="kicker">Free scanner</p>
            <h2>What the public path proves</h2>
            <ul class="clean">
              <li>Which workflow files were scanned.</li>
              <li>Which rules fired, with source URLs and deadlines where available.</li>
              <li>Which findings are autofix, manual review, blocked, or informational.</li>
              <li>Why a finding requires manual review and which source explains the migration.</li>
            </ul>
          </article>
          <article class="page-panel">
            <p class="kicker">Interpret your results</p>
            <h2>Know what was checked</h2>
            <ul class="clean">
              <li>No supported findings detected means only that the current rules found no matching patterns.</li>
              <li>Review source-linked guidance to address findings manually.</li>
              <li>Inspect every patch and run your own CI checks before merging.</li>
            </ul>
          </article>
        </div>
      </section>
      <section class="section">
        <div class="section-heading">
          <p class="kicker">Migration Library</p>
          <h2>Tools for SQLAlchemy, Pydantic, and ESLint migrations.</h2>
        </div>
        <div class="topic-list">{library_cards}</div>
        <div class="page-actions">
          <a class="button secondary" href="/products/">Open the full library</a>
        </div>
      </section>
"""
    html = layout(
        path=path,
        title="Autonomous Deadline-Readiness Tools",
        description="Find supported upgrade issues locally, inspect source-linked reports, and review manual alternatives. Start with GitHub Actions Upgrade Guard; your source stays on your machine.",
        kicker="Local developer tools",
        heading="Autonomous deadline-readiness tools for software teams.",
        body=body,
        crumbs=[(path, "Home")],
        schemas=[],
    )
    return path, html


def render_wells_hub() -> tuple[str, str]:
    path = "wells/index.html"
    cards = "".join(
        f"""
          <article class="catalog-card">
            <div class="catalog-card-top">
              <span class="status-label {escape(status_class)}">{escape(status)}</span>
              <span class="catalog-price">{escape(period)}</span>
            </div>
            <h3>{heading}</h3>
            <p>{escape(copy)}</p>
            <div class="page-actions">{actions}</div>
          </article>"""
        for status_class, status, period, heading, copy, actions in (
            (
                "available",
                "Active",
                "May 2026",
                '<a href="/wells/github-actions-upgrade-guard/">GitHub Actions Upgrade Guard</a>',
                "Current Featured tool and first front-page demand test.",
                '<a class="button secondary" href="/proof/actions-upgrade-guard/">Read proof</a>',
            ),
            (
                "proof-only",
                "Next candidate",
                "Paused",
                "Python 3.14 Readiness Pack",
                "Built as a product package, but checkout and front-page promotion wait for Action Guard evidence.",
                "",
            ),
            (
                "proof-only",
                "MVP built",
                "Paused",
                "Apple, CRA, ESLint v10, and Publisher Hardening",
                "Rank 3-6 wells exist as local MVPs and stay paused until each has proof pages and exact-fit demand tests.",
                "",
            ),
        )
    )
    body = f"""
      <section class="section">
        <div class="section-heading">
          <p class="kicker">Monthly wells</p>
          <h2>Promote by demand evidence, not build enthusiasm.</h2>
          <p>Each well starts as a narrow local scanner/report artifact around a deadline, deprecation, policy shift, compliance need, or recurring operational breakage.</p>
        </div>
        <div class="catalog-grid">{cards}</div>
      </section>
      <section class="section">
        <article class="page-panel">
          <h2>Promotion and pause rules</h2>
          <ul class="clean">
            <li>Promote when serious users run the scanner, ask scope/pricing questions, or move repeatedly from exact-source pages into proof/product pages.</li>
            <li>Pause when traffic arrives but no one runs the artifact or checkout intent stays near zero after targeted outreach.</li>
            <li>Keep paid checkout hidden until the free/proof boundary is clear.</li>
          </ul>
        </article>
      </section>
"""
    html = layout(
        path=path,
        title="Product Wells Archive",
        description="Archive of Zipper Tools Product Wells, starting with GitHub Actions Upgrade Guard as the current Featured tool.",
        kicker="Wells",
        heading="Product Wells archive",
        body=body,
        crumbs=[("index.html", "Home"), (path, "Wells")],
        schemas=[],
    )
    return path, html


def render_action_guard_well() -> tuple[str, str]:
    path = "wells/github-actions-upgrade-guard/index.html"
    product = product_by_slug("actions-upgrade-guard")
    if product is None:
        raise RuntimeError("actions-upgrade-guard product is missing")
    source = tracking_source(path, "well")
    body = f"""
      <section class="section">
        <article class="conversion-panel product-hero-panel">
          <div class="conversion-copy">
            <p class="kicker">Free local scanner</p>
            <h2>GitHub Actions workflow upgrades have deadline-shaped pain.</h2>
            <p>Action Guard turns artifact/cache deprecations, runner-image drift, runtime pressure, token-permission risk, and invalid YAML into a local report plus manual migration guidance.</p>
          </div>
          <div class="conversion-actions">
            <a class="button" href="{tracked_go_path(ACTION_GUARD_FREE_SCAN_ROUTE, source)}">Run free Action Guard scanner</a>
            <a class="button secondary" href="/proof/actions-upgrade-guard/">Read proof</a>
            <a class="button secondary" href="/products/actions-upgrade-guard/">Open product page</a>
          </div>
        </article>
      </section>
      <section class="section">
        <div class="grid two">
          <article class="page-panel">
            <h2>Why this well exists</h2>
            <ul class="clean">
              <li>Workflow deprecations and runner changes are deadline-sensitive but scattered across repos.</li>
              <li>Teams need source-linked findings and explicit unsupported cases.</li>
              <li>The scanner can work from local workflow YAML without GitHub credentials.</li>
            </ul>
          </article>
          <article class="page-panel">
            <h2>Current launch boundary</h2>
            <ul class="clean">
              <li>Free scanner/report path is live in the public repo.</li>
              <li>Proof artifacts are public and source-linked.</li>
              <li>Paid checkout is paused until the SKU and demand signal are clear.</li>
            </ul>
          </article>
        </div>
      </section>
      <section class="section">
        <article class="page-panel">
          <h2>Rules in the first pack</h2>
          <ul class="clean">{"".join(f"<li>{escape(item)}</li>" for item in product.proof_points)}</ul>
        </article>
      </section>
"""
    html = layout(
        path=path,
        title="GitHub Actions Upgrade Guard Well",
        description="A local GitHub Actions scanner for supported deprecations, runner drift, and permissions review. No automatic workflow changes.",
        kicker="Featured tool",
        heading="GitHub Actions Upgrade Guard",
        body=body,
        crumbs=[
            ("index.html", "Home"),
            ("wells/index.html", "Wells"),
            (path, "GitHub Actions Upgrade Guard"),
        ],
        schemas=[],
    )
    return path, html


def render_framework_page() -> tuple[str, str]:
    path = "framework/index.html"
    filters = (
        "Runs locally from repo-native inputs.",
        "Uses deterministic parsing, rules, patch synthesis, and confidence scoring first.",
        "Produces an autonomous artifact: patch set, report, CI gate, dossier, or risk summary.",
        "Avoids source upload, production credentials, paid APIs, and human delivery.",
        "Fails closed when a safe fix is uncertain.",
    )
    cycle = (
        "Collect current official pressure.",
        "Score candidates by urgency, willingness to pay, feasibility, distribution, gap, repeatability, and trust burden.",
        "Publish one Featured tool.",
        "Build the smallest local proof artifact.",
        "Promote, pause, or kill by measured demand.",
    )
    body = f"""
      <section class="section">
        <div class="grid two">
          <article class="page-panel">
            <h2>Hard filters</h2>
            <ul class="clean">{"".join(f"<li>{escape(item)}</li>" for item in filters)}</ul>
          </article>
          <article class="page-panel">
            <h2>Monthly cycle</h2>
            <ol class="workflow-list">{"".join(f"<li>{escape(item)}</li>" for item in cycle)}</ol>
          </article>
        </div>
      </section>
      <section class="section">
        <article class="page-panel">
          <h2>Current application</h2>
          <p>GitHub Actions Upgrade Guard is the first live test of this framework. SQLAlchemy, Pydantic, and flat-config assets remain in the Migration Library as proof that the same pattern can produce local scanners, reports, and cautious apply workflows.</p>
          <div class="page-actions">
            <a class="button" href="/wells/github-actions-upgrade-guard/">Open the current well</a>
            <a class="button secondary" href="/products/">Open the Migration Library</a>
          </div>
        </article>
      </section>
"""
    html = layout(
        path=path,
        title="Product Wells Framework",
        description="The Zipper Tools Product Wells method for building local-first autonomous deadline-readiness tools.",
        kicker="Framework",
        heading="The Product Wells method",
        body=body,
        crumbs=[("index.html", "Home"), (path, "Framework")],
        schemas=[],
    )
    return path, html


def render_sqlalchemy_public_proof() -> tuple[str, str]:
    path = "proof/sqlalchemy-public-proof/index.html"
    proof_actions = action_list_html(
        (
            f'<a class="button" href="{relative_href(path, "products/sa20-pack/index.html")}">Open SQLAlchemy cleanup pack</a>',
            '<a class="button secondary" href="/scan">Run the free scan first</a>',
        )
    )
    proof_rows = (
        (
            "Bogdanp/flask_dramatiq_example",
            "Query.get plus declarative import cleanup",
            "supported static rewrite on copied public input; application validation not established",
            "https://github.com/Bogdanp/flask_dramatiq_example/blob/a2f2c2baf7bdd7e1044ec6d241556f6333a6e397/app.py",
        ),
        (
            "dunossauro/live-de-python",
            "select([table]) list syntax cleanup",
            "supported static rewrite on copied public input; application validation not established",
            "https://github.com/dunossauro/live-de-python/blob/c0c83d3cb1271b0e55de2f83ad3a2aa4a57b53a8/codigo/Live011/core_select.py",
        ),
        (
            "nylas/sync-engine",
            "Query.get plus string loader cleanup",
            "supported static rewrite on copied public input; application validation not established",
            "https://github.com/nylas/sync-engine/blob/b91b94b9a0033be4199006eb234d270779a04443/inbox/transactions/search.py",
        ),
    )
    blocked_rows = (
        (
            "nylas/sync-engine",
            "engine.execute(...)",
            "manual_review_required",
            "https://github.com/nylas/sync-engine/blob/b91b94b9a0033be4199006eb234d270779a04443/inbox/ignition.py",
        ),
        (
            "teamclairvoyant/airflow-maintenance-dags",
            "Query.from_self()",
            "manual_review_required",
            "https://github.com/teamclairvoyant/airflow-maintenance-dags/blob/fe592a5cb90508804b589652ef7fedc624bff595/db-cleanup/airflow-db-cleanup.py",
        ),
    )
    proof_cards = "".join(
        '<article class="page-panel">'
        f'<h3><a href="{escape(source_url)}">{escape(repo)}</a></h3>'
        f"<p>{escape(pattern)}</p>"
        f'<p class="caption">{escape(result)}</p>'
        "</article>"
        for repo, pattern, result, source_url in proof_rows
    )
    blocked_cards = "".join(
        '<article class="page-panel">'
        f'<h3><a href="{escape(source_url)}">{escape(repo)}</a></h3>'
        f"<p>{escape(pattern)}</p>"
        f'<p class="caption">{escape(result)}</p>'
        "</article>"
        for repo, pattern, result, source_url in blocked_rows
    )
    sample_before = (
        "from sqlalchemy.ext.declarative import declarative_base\n"
        "\n"
        "Base = declarative_base()\n"
        "job = session.query(Job).get(job_id)\n"
        "stmt = select([Job.id, Job.name])"
    )
    sample_report = (
        "{\n"
        '  "status": "preview_only",\n'
        '  "transform_count": 3,\n'
        '  "supported_candidates": {\n'
        '    "declarative_imports": 1,\n'
        '    "query_get": 1,\n'
        '    "select_list_syntax": 1\n'
        "  },\n"
        '  "manual_todos": []\n'
        "}"
    )
    sample_diff = (
        "-from sqlalchemy.ext.declarative import declarative_base\n"
        "+from sqlalchemy.orm import declarative_base\n"
        "-job = session.query(Job).get(job_id)\n"
        "+job = session.get(Job, job_id)\n"
        "-stmt = select([Job.id, Job.name])\n"
        "+stmt = select(Job.id, Job.name)"
    )
    sample_validation = (
        "validation:\n"
        "  python -m compileall copied_public_input ... passed\n"
        "  scanner report generated ... passed\n"
        "  unsupported findings ... 0"
    )
    sample_apply_output = (
        "apply output:\n"
        "  files changed: 1\n"
        "  transforms applied: 3\n"
        "  report written: migration-report.json\n"
        "  mode: preview/apply branch workflow"
    )
    sample_final_report = (
        "final report:\n"
        "  files scanned: 1\n"
        "  files changed: 1\n"
        "  transforms applied: declarative_imports, query_get, select_list_syntax\n"
        "  confidence: supported subset, validation required before merge"
    )
    sample_manager_summary = (
        "manager summary:\n"
        "  supported cleanup findings: 3\n"
        "  manual-review findings: 0\n"
        "  next step: run the same workflow on a branch, then validate with repo tests\n"
        "  boundary: no broad SQLAlchemy migration guarantee"
    )
    body = f"""
      <section class="section">
        <div class="grid three">
          <article class="page-panel">
            <h2>3 supported public-file passes</h2>
            <p>Copied public inputs landed inside the documented SQLAlchemy automation subset.</p>
          </article>
          <article class="page-panel">
            <h2>2 blocked manual-review cases</h2>
            <p>Risky execution and query-shape patterns were reported instead of guessed through.</p>
          </article>
          <article class="page-panel">
            <h2>0 broad migration promises</h2>
            <p>The proof covers the narrow legacy query and syntax subset, not every SQLAlchemy 2.0 change.</p>
          </article>
        </div>
      </section>
{trust_boundary_section()}
      <section class="section">
        <div class="section-heading"><p class="kicker">Supported examples</p><h2>Public files that matched the automation subset</h2></div>
        <div class="grid three">{proof_cards}</div>
      </section>
      <section class="section">
        <div class="section-heading"><p class="kicker">Fail-closed examples</p><h2>Public files that stayed in manual review</h2></div>
        <div class="grid two">{blocked_cards}</div>
      </section>
      <section class="section">
        <div class="section-heading"><p class="kicker">Artifact trail</p><h2>One public-proof run, shown end to end</h2></div>
        <div class="grid two">
          <article class="page-panel">
            <h3>Sample repo before</h3>
            {code_block(sample_before)}
          </article>
          <article class="page-panel">
            <h3>Scan JSON</h3>
            {code_block(sample_report)}
          </article>
          <article class="page-panel">
            <h3>Preview diff</h3>
            {code_block(sample_diff)}
          </article>
          <article class="page-panel">
            <h3>Validation result</h3>
            {code_block(sample_validation)}
          </article>
          <article class="page-panel">
            <h3>Apply output</h3>
            {code_block(sample_apply_output)}
          </article>
          <article class="page-panel">
            <h3>Final manager summary</h3>
            {code_block(sample_manager_summary)}
          </article>
        </div>
        <article class="page-panel">
          <h3>Final report shape</h3>
          {code_block(sample_final_report)}
          <p class="caption">This is the visible evidence shape buyers should expect: before input, scanner JSON, preview diff, apply output, validation status, and final manager summary. The paid pack still has to be run on a branch and validated in the buyer's repo.</p>
        </article>
      </section>
      <section class="section">
        <div class="grid two">
          <article class="page-panel">
            <h2>What this proves</h2>
            <ul class="clean">
              <li>Direct Query.get, select list, declarative import, and simple loader cleanup can be classified on real public input.</li>
              <li>Unsafe execution and query-shape patterns stay visible as manual-review findings.</li>
              <li>The free scanner is the qualification step before any paid cleanup workflow.</li>
            </ul>
          </article>
          <article class="page-panel">
            <h2>What it does not prove</h2>
            <ul class="clean">
              <li>Full engine.execute(...) automation.</li>
              <li>Full Query API migration to select().</li>
              <li>Package, test, or database integration success for every repo with one supported snippet.</li>
            </ul>
            <div class="page-actions">
              {proof_actions}
            </div>
          </article>
        </div>
      </section>
"""
    html = layout(
        path=path,
        title="SQLAlchemy public proof",
        description="Public SQLAlchemy migration proof for the supported cleanup subset, including supported static rewrites and fail-closed manual-review examples.",
        kicker="Public proof",
        heading="SQLAlchemy migration proof on public files",
        body=body,
        crumbs=[
            ("index.html", "Home"),
            ("products/sa20-pack/index.html", "SQLAlchemy cleanup pack"),
            (path, "Public proof"),
        ],
        schemas=[],
    )
    return path, html


def action_guard_proof_report() -> dict[str, Any]:
    proof = (
        Path(__file__).resolve().parents[1]
        / "products/actions-upgrade-guard/proof-report.json"
    )
    return dict(json.loads(proof.read_text(encoding="utf-8")))


def action_guard_patch_preview() -> str:
    return "No safe patch generated. Review platform, runner, shared artifact names, hidden files, and download compatibility using each finding's source."


def write_action_guard_proof_assets(output_dir: Path) -> None:
    proof_dir = output_dir / "proof" / "actions-upgrade-guard"
    proof_dir.mkdir(parents=True, exist_ok=True)
    report_json = json.dumps(action_guard_proof_report(), indent=2)
    write_generated_text(
        (proof_dir / "actions-upgrade-report.json"),
        report_json + "\n",
        encoding="utf-8",
    )
    write_generated_text(
        (proof_dir / "patch-preview.diff"),
        action_guard_patch_preview(),
        encoding="utf-8",
    )
    report_html = f"""<!doctype html>
<html lang="en">
  <head><meta charset="utf-8" /><title>Actions Upgrade Guard Report</title></head>
  <body>
    <h1>Actions Upgrade Guard Report</h1>
    <p>Status: manual_review_required. Blocking findings: 3. No automatic patches.</p>
    <h2>Patch preview</h2>
    {code_block(action_guard_patch_preview())}
  </body>
</html>
"""
    write_generated_text(
        (proof_dir / "actions-upgrade-report.html"),
        clean_generated_text(report_html),
        encoding="utf-8",
    )


def render_action_guard_proof() -> tuple[str, str]:
    path = "proof/actions-upgrade-guard/index.html"
    product = product_by_slug("actions-upgrade-guard")
    if product is None:
        raise RuntimeError("actions-upgrade-guard product is missing")
    source = tracking_source(path, "proof")
    report = action_guard_proof_report()
    report_excerpt = (
        f"status: {report['status']}\n"
        f"rule_pack_version: {report['rule_pack_version']}\n"
        "scanned_files: .github/workflows/build.yml\n"
        "blocking_findings: 3\n"
        "autofix_findings: none\n"
        "manual_review: AUG001, AUG002; informational: AUG006, AUG008"
    )
    before_file = (
        "jobs:\n"
        "  test:\n"
        "    runs-on: ubuntu-latest\n"
        "    steps:\n"
        "      - uses: actions/checkout@v4\n"
        "      - uses: actions/cache@v2\n"
        "      - uses: actions/upload-artifact@v3\n"
        "      - uses: actions/download-artifact@v3\n"
    )
    command = (
        f"git clone {REPO_URL}\n"
        "python -m pip install -e sqlalchemy-14-to-20-codemod/products/actions-upgrade-guard\n"
        "python -m actions_upgrade_guard.cli . "
        "--report actions-upgrade-report.json "
        "--html-report actions-upgrade-report.html"
    )
    artifact_actions = action_list_html(
        (
            f'<a class="button" href="{free_scan_go_path(product, source)}">Run free Action Guard scanner</a>',
            f'<a class="button secondary" href="{relative_href(path, "products/actions-upgrade-guard/index.html")}">Open product page</a>',
            f'<a class="button secondary" href="{relative_href(path, "proof/actions-upgrade-guard/actions-upgrade-report.json")}">Open JSON artifact</a>',
            f'<a class="button secondary" href="{relative_href(path, "proof/actions-upgrade-guard/actions-upgrade-report.html")}">Open HTML artifact</a>',
            f'<a class="button secondary" href="{relative_href(path, "proof/actions-upgrade-guard/patch-preview.diff")}">Read no-safe-patch explanation</a>',
        )
    )
    body = f"""
      <section class="section">
        <article class="conversion-panel product-hero-panel">
          <div class="conversion-copy">
            <p class="kicker">Proof artifact</p>
            <h2>One fixture run, shown as files a buyer can inspect.</h2>
            <p>The proof page publishes the before workflow, command, JSON report excerpt, HTML report artifact, no-safe-patch explanation, and fail-closed findings for GitHub Actions Upgrade Guard.</p>
          </div>
          <div class="conversion-actions">
            {artifact_actions}
          </div>
        </article>
      </section>
{trust_boundary_section()}
      <section class="section">
        <div class="grid two">
          <article class="page-panel">
            <h2>Before workflow</h2>
            {code_block(before_file)}
          </article>
          <article class="page-panel">
            <h2>Command</h2>
            {code_block(command)}
            <p class="caption">The scanner runs locally and writes JSON plus HTML reports without a GitHub token.</p>
          </article>
          <article class="page-panel">
            <h2>Buyer-readable report excerpt</h2>
            {code_block(report_excerpt)}
          </article>
          <article class="page-panel">
            <h2>Patch preview</h2>
            {code_block(action_guard_patch_preview())}
          </article>
        </div>
      </section>
      <section class="section">
        <div class="grid two">
          <article class="page-panel">
            <h2>Fail-closed findings</h2>
            <ul class="clean">
              <li>Missing or broad permissions are reported for review instead of rewritten blindly.</li>
              <li>Floating runner labels are source-linked findings, not automatic edits.</li>
              <li>Invalid YAML exits as a blocked finding instead of crashing or guessing.</li>
            </ul>
          </article>
          <article class="page-panel">
            <h2>Do not buy this if</h2>
            <ul class="clean">{"".join(f"<li>{escape(item)}</li>" for item in product.not_for)}</ul>
          </article>
        </div>
      </section>
      <section class="section">
        <article class="page-panel">
          <h2>Why this is not just actionlint</h2>
          <p>Action Guard is not trying to replace syntax linting. It is a deadline-readiness report: source-backed deprecation rules, fixability classification, manual migration guidance, and a manager-readable risk surface for workflow changes that can break releases.</p>
        </article>
      </section>
"""
    html = layout(
        path=path,
        title="GitHub Actions Upgrade Guard proof",
        description="Public proof artifacts for GitHub Actions Upgrade Guard, including before workflow, command, generated report, manual alternatives, and fail-closed findings.",
        kicker="Public proof",
        heading="GitHub Actions Upgrade Guard proof artifacts",
        body=body,
        crumbs=[
            ("index.html", "Home"),
            ("wells/index.html", "Wells"),
            ("wells/github-actions-upgrade-guard/index.html", "Action Guard"),
            (path, "Proof"),
        ],
        schemas=[],
    )
    return path, html


def render_generic_product_proof(product: ProductPage) -> tuple[str, str]:
    path = product_proof_path(product)
    guides = [guide for guide in GUIDES if guide.slug in product.guide_slugs][:8]
    guide_cards = "".join(
        f'<a class="topic-card" href="{relative_href(path, f"{guide.family}/{guide.slug}/index.html")}">'
        f"<strong>{escape(guide.h1)}</strong><span>{escape(guide.description)}</span></a>"
        for guide in guides
    )
    docs_buttons = tuple(
        f'<a class="button secondary" href="{escape(repo_doc_href(doc_path))}" data-doc-path="{escape(doc_path)}">{escape(label)}</a>'
        for label, doc_path in product.docs
    )
    pricing_button = (
        f'<a class="button secondary" href="{pricing_section_href(path, product)}">See pricing</a>'
        if pricing_section_href(path, product)
        else ""
    )
    product_button = f'<a class="button" href="{relative_href(path, product_page_path(product))}">Open {escape(product.name)}</a>'
    decision_actions = action_list_html((product_button, pricing_button, *docs_buttons))
    if product.slug == "pydantic-v2-porter":
        artifact_scan = (
            "scan report\n"
            "supported_findings: 24\n"
            "manual_review_findings: 5\n"
            "files_uploaded: 0\n"
            "next_step: preview supported rewrites"
        )
        artifact_diff = (
            "- from pydantic import BaseSettings, validator\n"
            "+ from pydantic import field_validator\n"
            "+ from pydantic_settings import BaseSettings\n"
            '-     @validator("email")\n'
            '+     @field_validator("email")\n'
            "+     @classmethod"
        )
        artifact_apply = (
            "apply output\n"
            "files_changed: 3\n"
            "transforms_applied: imports, BaseSettings, validators, Config\n"
            "manual_review_findings: alias/signature-heavy validators"
        )
        artifact_validation = (
            "validation summary\n"
            "compileall fixture_repo ... passed\n"
            "fixture tests ... passed\n"
            "buyer repo tests ... required before merge"
        )
        artifact_manager = (
            "final manager summary\n"
            "Use the cleanup pack when direct Pydantic v1 patterns repeat.\n"
            "Keep alias-heavy imports and signature-heavy validators in manual review.\n"
            "No source upload is needed."
        )
    else:
        artifact_scan = (
            "scan report\n"
            "supported_static_configs: 1\n"
            "manual_review_findings: 2\n"
            "files_uploaded: 0\n"
            "checkout_status: proof only"
        )
        artifact_diff = (
            "- .eslintrc.json\n"
            "+ eslint.config.cjs\n"
            '+ const { FlatCompat } = require("@eslint/eslintrc");\n'
            "+ module.exports = [...compat.config(legacyConfig)];"
        )
        artifact_apply = (
            "proof output\n"
            "generated_preview: eslint.config.cjs\n"
            "manual_review_findings: JS config logic, existing flat config\n"
            "checkout_status: not listed"
        )
        artifact_validation = (
            "validation summary\n"
            "static config parse ... passed\n"
            "unsupported guards ... passed\n"
            "buyer repo lint ... required before merge"
        )
        artifact_manager = (
            "final manager summary\n"
            "Use as proof for static JSON/YAML config only.\n"
            "Do not buy from this page; checkout is not listed.\n"
            "Keep JS config behavior manual."
        )
    body = f"""
      <section class="section">
        <div class="grid three">
          <article class="page-panel">
            <h2>{len(guides)} exact-problem pages</h2>
            <p>The proof page is tied to specific migration error pages, not a generic refactor promise.</p>
          </article>
          <article class="page-panel">
            <h2>{len(product.proof_points)} fit signals</h2>
            <p>The product stays inside the supported subset and keeps fail-closed boundaries visible.</p>
          </article>
          <article class="page-panel">
            <h2>{len(product.not_for)} stop signals</h2>
            <p>The proof is also a way to say no before a buyer spends money on the wrong repo.</p>
          </article>
        </div>
      </section>
{trust_boundary_section()}
      <section class="section">
        <div class="section-heading"><p class="kicker">Artifact trail</p><h2>Visible report, diff, output, validation, and manager summary</h2></div>
        <div class="grid two">
          <article class="page-panel">
            <h3>Scan report</h3>
            {code_block(artifact_scan)}
          </article>
          <article class="page-panel">
            <h3>Preview diff</h3>
            {code_block(artifact_diff)}
          </article>
          <article class="page-panel">
            <h3>Apply output</h3>
            {code_block(artifact_apply)}
          </article>
          <article class="page-panel">
            <h3>Validation summary</h3>
            {code_block(artifact_validation)}
          </article>
        </div>
        <article class="page-panel">
          <h3>Final manager summary</h3>
          {code_block(artifact_manager)}
        </article>
      </section>
      <section class="section">
        <div class="grid two">
          <article class="page-panel">
            <h2>What this proof covers</h2>
            <ul class="clean">{"".join(f"<li>{escape(item)}</li>" for item in product.proof_points)}</ul>
          </article>
          <article class="page-panel">
            <h2>What stays out of scope</h2>
            <ul class="clean">{"".join(f"<li>{escape(item)}</li>" for item in product.not_for)}</ul>
          </article>
        </div>
      </section>
      <section class="section">
        <div class="grid two">
          <article class="page-panel">
            <h2>Start from the live problem pages</h2>
            <div class="topic-list">{guide_cards}</div>
          </article>
          <article class="page-panel">
            <h2>Decision path</h2>
            <p>{escape(product.summary)}</p>
            <div class="page-actions">
              {decision_actions}
            </div>
          </article>
        </div>
      </section>
"""
    html = layout(
        path=path,
        title=f"{product.name} proof and fit",
        description=f"Public proof and fit boundaries for {product.name}, including supported scope and exact-problem entry pages.",
        kicker="Public proof",
        heading=f"{product.name} proof and fit",
        body=body,
        crumbs=[
            ("index.html", "Home"),
            (product_page_path(product), product.name),
            (path, "Public proof"),
        ],
        schemas=[],
    )
    return path, html


def write_sitemap(
    output_dir: Path, filename: str, urls: Iterable[str], lastmod: str
) -> None:
    items = "".join(
        f"<url><loc>{escape(url)}</loc><lastmod>{lastmod}</lastmod></url>"
        for url in urls
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + items
        + "</urlset>"
    )
    write_generated_text((output_dir / filename), xml, encoding="utf-8")


def write_sitemap_index(
    output_dir: Path, filenames: Iterable[str], lastmod: str
) -> None:
    items = "".join(
        f"<sitemap><loc>{SITE_URL}/{name}</loc><lastmod>{lastmod}</lastmod></sitemap>"
        for name in filenames
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        + '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + items
        + "</sitemapindex>"
    )
    write_generated_text((output_dir / "sitemap.xml"), xml, encoding="utf-8")


def clean_page_redirects(page_paths: Iterable[str]) -> list[tuple[str, str, int]]:
    redirects: list[tuple[str, str, int]] = []
    seen: set[tuple[str, str, int]] = set()
    for path in page_paths:
        if not is_page_path(path):
            continue
        source = f"/{path.strip('/')}"
        target = public_path(path)
        if source == target:
            continue
        item = (source, target, 301)
        if item not in seen:
            seen.add(item)
            redirects.append(item)
    return sorted(redirects)


def write_redirects(
    output_dir: Path, redirects: Iterable[tuple[str, str, int]]
) -> None:
    lines = [f"{source} {target} {status}" for source, target, status in redirects]
    write_generated_text(
        (output_dir / "_redirects"), "\n".join(lines) + "\n", encoding="utf-8"
    )


def build_site(output_dir: Path) -> dict[str, Any]:
    grouped: dict[str, list[GuidePage]] = defaultdict(list)
    for guide in GUIDES:
        grouped[guide.family].append(guide)

    proof_pages = [
        render_sqlalchemy_public_proof(),
        *[
            render_action_guard_proof()
            if product.slug == "actions-upgrade-guard"
            else render_generic_product_proof(product)
            for product in PRODUCTS
            if product.slug != "sa20-pack" and has_product_proof(product)
        ],
    ]
    pages = [
        render_home(),
        render_wells_hub(),
        render_action_guard_well(),
        render_framework_page(),
        render_guides_hub(grouped),
        render_products_hub(),
        *[render_family_hub(family, guides) for family, guides in grouped.items()],
        *[render_guide(guide) for guide in GUIDES],
        *[render_product(product) for product in PRODUCTS],
        *proof_pages,
    ]
    for rel_path, html in pages:
        path = output_dir / PurePosixPath(rel_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        write_generated_text(path, clean_generated_text(html), encoding="utf-8")
    write_action_guard_proof_assets(output_dir)

    lastmod = date.today().isoformat()
    proof_urls = [canonical_url(path) for path, _html in proof_pages]
    static_urls = [
        canonical_url(path) for path, _label in INDEXABLE_STATIC_PAGES
    ] + proof_urls
    hub_urls = [
        canonical_url("wells/index.html"),
        canonical_url("wells/github-actions-upgrade-guard/index.html"),
        canonical_url("framework/index.html"),
        canonical_url("guides/index.html"),
        canonical_url("products/index.html"),
        *[canonical_url(f"{family}/index.html") for family in grouped],
    ]
    guide_urls = [
        canonical_url(f"{guide.family}/{guide.slug}/index.html") for guide in GUIDES
    ]
    product_urls = [
        canonical_url(f"products/{product.slug}/index.html") for product in PRODUCTS
    ]

    write_sitemap(output_dir, "sitemap-pages.xml", static_urls, lastmod)
    write_sitemap(output_dir, "sitemap-hubs.xml", hub_urls, lastmod)
    write_sitemap(output_dir, "sitemap-problem-pages.xml", guide_urls, lastmod)
    write_sitemap(output_dir, "sitemap-products.xml", product_urls, lastmod)
    write_sitemap_index(
        output_dir,
        (
            "sitemap-pages.xml",
            "sitemap-hubs.xml",
            "sitemap-problem-pages.xml",
            "sitemap-products.xml",
        ),
        lastmod,
    )

    write_generated_text(
        (output_dir / "robots.txt"),
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )
    write_generated_text(
        (output_dir / f"{INDEXNOW_KEY}.txt"), INDEXNOW_KEY, encoding="utf-8"
    )
    page_paths = [
        "index.html",
        *STATIC_PAGE_PATHS,
        *(path for path, _label in INDEXABLE_STATIC_PAGES if path),
        *(path for path, _html in pages),
    ]
    all_redirects = [*REDIRECTS, *clean_page_redirects(page_paths)]
    write_redirects(output_dir, all_redirects)

    manifest = {
        "site_url": SITE_URL,
        "indexnow_key": INDEXNOW_KEY,
        "indexnow_key_location": canonical_url(f"{INDEXNOW_KEY}.txt"),
        "redirects": [
            {"source": source, "target": target, "status": status}
            for source, target, status in all_redirects
        ],
        "generated_on": lastmod,
        "urls": {
            "static": static_urls,
            "hubs": hub_urls,
            "guides": guide_urls,
            "products": product_urls,
            "proof": proof_urls,
        },
        "products": [asdict(product) for product in PRODUCTS],
        "guides": [asdict(guide) for guide in GUIDES],
    }
    write_generated_text(
        (output_dir / "_site_manifest.json"),
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    return manifest


def write_generated_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    # Repeated builds should not truncate identical files while indexers read them.
    if path.exists() and path.read_text(encoding=encoding) == text:
        return
    path.write_text(text, encoding=encoding)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build static discovery pages for the site."
    )
    parser.add_argument(
        "--output-dir", default="site", help="Directory to write generated pages into."
    )
    args = parser.parse_args()
    build_site(Path(args.output_dir))


if __name__ == "__main__":
    main()
