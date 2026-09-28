"""Focused, evidence-led storefront pages. No price or policy overrides."""

from __future__ import annotations

import json
from collections.abc import Callable
from html import escape
from pathlib import Path
from typing import Any

from scripts.site_catalog import (
    PRODUCTS,
    PYDANTIC_INSTALL_URL,
    REFUND_LANGUAGE,
    SA20_INSTALL_URL,
)

# ruff: noqa: E501
PROOF = "/proof/pydantic-v2-porter/"
PRODUCT = "/products/pydantic-v2-porter/"
REPO = "https://github.com/zippertools/sqlalchemy-14-to-20-codemod"
FREE_GUIDE = "https://docs.pydantic.dev/latest/migration/"


def panel(title: str, body: str, id: str = "") -> str:
    return f'<section class="section"{f" id={id}" if id else ""}><article class="page-panel"><h2>{escape(title)}</h2>{body}</article></section>'


def button(href: str, text: str, secondary: bool = False) -> str:
    return f'<a class="button{" secondary" if secondary else ""}" href="{href}">{escape(text)}</a>'


def buy(slug: str, source: str, price: str) -> str:
    return f'<form method="post" action="/go/{slug}/{source}"><button class="button" type="submit">Buy cleanup pack — {price}</button></form>'


def commands(url: str, module: str) -> str:
    return (
        '<pre class="code-block">'
        + escape(
            f'python -m venv .zipper-venv\n# Windows PowerShell:\n.\\.zipper-venv\\Scripts\\Activate.ps1\n# macOS / Linux: source .zipper-venv/bin/activate\npython -m pip install "{url}"\npython -m {module}.cli path/to/your/repo --report migration-report.json'
        )
        + "</pre>"
    )


def render_sales_pages(layout: Callable[..., str]) -> list[tuple[str, str]]:
    pages: list[tuple[str, str]] = []

    def add(
        path: str,
        title: str,
        description: str,
        body: str,
        kicker: str = "Local migration tools",
    ) -> None:
        schemas = []
        if path == "products/pydantic-v2-porter/index.html":
            product = next(p for p in PRODUCTS if p.slug == "pydantic-v2-porter")
            schemas.append(
                {
                    "@context": "https://schema.org",
                    "@type": "SoftwareApplication",
                    "name": product.name,
                    "applicationCategory": "DeveloperApplication",
                    "operatingSystem": "Windows, macOS, Linux",
                    "offers": {
                        "@type": "Offer",
                        "price": product.price,
                        "priceCurrency": "USD",
                        "url": "https://zippertools.org" + PRODUCT,
                    },
                }
            )
        pages.append(
            (
                path,
                layout(
                    path=path,
                    title=title,
                    description=description,
                    kicker=kicker,
                    heading=title,
                    body=body,
                    crumbs=[("index.html", "Home"), (path, title)]
                    if path != "index.html"
                    else [("index.html", "Home")],
                    schemas=schemas,
                ),
            )
        )

    actions = (
        '<div class="page-actions">'
        + button("/scan#pydantic", "Run the free Pydantic scan")
        + button(PROOF, "See the tested example", True)
        + "</div>"
    )
    fit = "<p>Best fit: an existing Python application with repeated direct Pydantic v1 imports, simple validators, settings imports or Config classes, and tests you can run. For a few edits, use the free report and migrate manually.</p><p>Not a complete FastAPI upgrade. Complex validators, aliases and unsupported configuration remain manual work.</p>"
    manual = f'<p>The free report is enough to evaluate supported patterns. No paid fit report is required. You can use the <a href="{FREE_GUIDE}">official migration guide</a> or the free <a href="https://github.com/pydantic/bump-pydantic">bump-pydantic codemod</a>. Compare both on a branch before paying.</p>'
    scope = '<ul class="clean"><li>Supported direct imports and BaseSettings moves.</li><li>Simple two-parameter validators and pre root validators.</li><li>Safe literal Config blocks and bare validate_arguments.</li><li>Alias-heavy imports, validators using values/field/config, each_item/always, post root validators and removed config keys require manual review.</li><li>Files containing unsupported patterns stay unchanged. Review all diffs and run your application tests.</li></ul>'
    assurance = f'<p>One-time purchase, $249.99 per team. Download the commercial ZIP after payment. No source upload, account with Zipper Tools or paid API required.</p><p>{REFUND_LANGUAGE} Read the <a href="/policies">license, refund and support terms</a>. Questions: <a href="mailto:support@zippertools.org">support@zippertools.org</a>.</p>'

    add(
        "index.html",
        "Upgrading an older FastAPI app? Start with a local Pydantic scan.",
        "Find supported Pydantic v1 patterns, see what needs manual work, and decide whether repetitive cleanup is worth automating.",
        actions
        + panel(
            "Free diagnosis. Optional paid cleanup.",
            fit
            + manual
            + "<p>The Pydantic Cleanup Pack adds the supported preview/apply workflow for <strong>$249.99 per team</strong>.</p>"
            + button(PRODUCT, "Review scope, proof and price", True),
        )
        + panel(
            "Working on a different upgrade?",
            '<div class="topic-list"><a class="topic-card" href="/products/sa20-pack/"><strong>SQLAlchemy 1.4 → 2.0</strong><span>Free diagnosis and optional paid cleanup for a narrow syntax subset.</span></a><a class="topic-card" href="/products/actions-upgrade-guard/"><strong>GitHub Actions maintenance</strong><span>Free workflow diagnosis with source-linked manual guidance. No automatic edits.</span></a><a class="topic-card" href="/products/flatconfig-lift/"><strong>ESLint configuration</strong><span>Free static-config examples and documented limits.</span></a></div>',
        ),
    )

    scan_body = panel(
        "1. Run the Pydantic scanner",
        "<p>Python 3.10+ and pip are required. Replace path/to/your/repo with your local checkout. The public scanner does not edit files or send your code anywhere.</p>"
        + commands(PYDANTIC_INSTALL_URL, "pydantic_v2_porter")
        + '<p>Exit 0 means the scan completed without reported manual-review findings; it does not prove compatibility. Exit 2 means review the reported findings. If installation fails, check Python and network access, then use the <a href="'
        + REPO
        + '/blob/main/products/pydantic-v2-porter/README.md">quickstart</a>. On PowerShell, you can use .\\.zipper-venv\\Scripts\\python.exe directly if activation is disabled.</p>',
        "pydantic",
    )
    scan_body += panel(
        "2. Interpret the report for free",
        '<p>Open migration-report.json locally. The file_results section lists patterns and findings by file. transforms_applied names candidate categories in a community scan; it does not mean files were changed. A file with blocking findings needs manual review even when it also has supported candidates.</p><p><strong>No supported findings detected</strong> means only that the scanner found no matching supported patterns. It is not a clean bill of health.</p><ul class="clean"><li>Few simple candidates: follow the upstream guide and fix them manually.</li><li>Repeated candidates in unblocked files: compare the tested example and decide whether paid automation saves enough work.</li><li>Mostly blocked files: do not buy expecting a complete migration.</li></ul>'
        + manual,
    )
    scan_body += panel(
        "3. Compare the work before buying",
        fit
        + '<div class="page-actions">'
        + button(PROOF, "Inspect real output from the example")
        + button(PRODUCT, "Paid scope and price", True)
        + "</div>",
    )
    scan_body += panel(
        "Other scanners",
        '<h3 id="sqlalchemy">SQLAlchemy</h3>'
        + commands(SA20_INSTALL_URL, "sa20_pack")
        + '<div class="page-actions">'
        + button(
            "/go/actions-upgrade-guard-free/scan-selector",
            "Free Action Guard scanner",
            True,
        )
        + button(
            "/go/flatconfig-free-scan/scan-selector", "ESLint proof and scanner", True
        )
        + "</div>",
    )
    add(
        "scan.html",
        "Scan locally. Understand the report for free.",
        "Choose your matching scanner. No repository upload and no paid assessment required.",
        scan_body,
        "Free diagnosis",
    )

    product_body = actions + panel(
        "What the $249.99 pack adds",
        "<p>A downloadable CLI that previews and applies the documented mechanical rewrites on your branch, with diffs and a JSON report. It leaves unsupported files unchanged. Dependency upgrades and application-level validation remain your responsibility.</p>"
        + fit
        + buy("pydantic-v2-porter", "pydantic-focused-offer", "$249.99")
        + assurance,
    )
    product_body += panel("Supported scope and limitations", scope)
    product_body += panel(
        "Planning a Python or FastAPI upgrade?",
        '<p><a href="https://fastapi.tiangolo.com/how-to/migrate-from-pydantic-v1-to-pydantic-v2/">FastAPI documents the Pydantic v2 requirement in recent releases</a>, while <a href="https://pydantic.dev/docs/validation/latest/get-started/changelog/#v2130-2026-04-13">Pydantic 2.13 added Python 3.14 support to its v1 namespace</a>. A warning alone does not establish a need to migrate. Check your actual dependency versions and migration plan. This pack automates only the patterns listed above.</p><p>Start with the guide that matches your code: <a href="/pydantic/basesettings-moved/">BaseSettings imports</a> · <a href="/pydantic/config-to-model-config/">Config classes</a> · <a href="/pydantic/validator-to-field-validator/">simple validators</a>.</p>',
    )
    product_body += panel(
        "Evidence you can inspect",
        "<p>Our order-API example exercises request validation, normalization, settings and response serialization. A separate unsupported validator checks that the tool leaves uncertain code alone. This is a small synthetic application, not a customer migration or a time-savings benchmark.</p>"
        + button(PROOF, "Read the reproducible comparison"),
    )
    product_body += panel(
        "Why not use the free alternative?",
        manual
        + "<p>Our offer is the documented local workflow, explicit manual-review findings and packaged guidance. The comparison reports observed results, not a claim that Zipper Tools is universally better. If the free tool does the work you need, use it.</p>",
    )
    product_body += panel(
        "After payment",
        '<ol><li>Download and extract your ZIP from the payment success page.</li><li>In a separate Python environment, run <code>python -m pip install .</code> from the extracted pack directory.</li><li>Preview against a clean branch, inspect the report, then apply supported edits.</li><li>Install the target project dependencies, run your tests and review before merging.</li></ol><pre class="code-block">python -m pydantic_v2_porter.cli path/to/repo --diff --report preview.json\npython -m pydantic_v2_porter.cli path/to/repo --apply --diff --report applied.json</pre><p>If BaseSettings is migrated, add pydantic-settings to the application dependencies. The tool does not promise to resolve dependency or behavior changes.</p>'
        + assurance,
    )
    add(
        "products/pydantic-v2-porter/index.html",
        "Reviewable Pydantic v1 → v2 cleanup for existing Python apps",
        "Automate supported repeated edits locally. Keep complex validators and application behavior changes in manual review.",
        product_body,
    )

    pricing = panel("Start with the free report", manual + actions, "free-scan")
    for slug, name, price, text in (
        (
            "pydantic-v2-porter",
            "Pydantic Cleanup Pack",
            "$249.99",
            "Supported imports, settings, simple validators and Config rewrites. Best for repeated mechanical changes in an existing Python app.",
        ),
        (
            "sa20-pack",
            "SQLAlchemy Cleanup Pack",
            "$299.99",
            "Supported Query.get, select-list syntax, declarative imports and narrow relationship/DML rewrites. Broad Query-to-select and engine.execute migration remain manual.",
        ),
    ):
        pricing += panel(
            name,
            f'<p class="price-line">{price} per team · One-time purchase</p><p>{text}</p><div class="page-actions">'
            + button(f"/products/{slug}/", "Review scope and proof", True)
            + buy(slug, "pricing-focused", price)
            + "</div>",
            slug,
        )
    pricing += panel(
        "Optional add-ons — not prerequisites",
        '<p>You do not need either add-on to understand the free scanner or purchase a cleanup pack.</p><h3 id="fit-report">SQLAlchemy/Pydantic Fit Report Add-on — $99 per team</h3><p>Optional local summary software for existing scanner output. No human review.</p><a href="/products/fit-report/">View fit report details</a><h3 id="sa20-preset">Migration Preset Bundle — $149.99 per team</h3><p>Optional rollout templates and manager notes. Does not rewrite code.</p><a href="/products/sa20-preset/">View preset bundle details</a>',
    )
    pricing += panel(
        "Delivery and terms",
        "<p>Download your purchased ZIP after payment. Run locally without source upload.</p>"
        + f'<p>{REFUND_LANGUAGE} See <a href="/policies">license and buyer terms</a> before checkout.</p><p>Action Guard and ESLint proof resources remain free; no paid package is listed for either.</p>',
    )
    add(
        "pricing.html",
        "Free diagnosis. Pay only for useful automation.",
        "Choose the pack for your current migration. No subscription or required paid fit report.",
        pricing,
    )

    evidence = (
        Path(__file__).resolve().parents[1]
        / "site/proof/pydantic-v2-porter/case-study/results.json"
    )
    proof_body = panel(
        "One reproducible application, not a customer claim",
        "<p>The original MIT-licensed FastAPI order API tests normalization, invalid inputs, extra-field rejection, response serialization and environment settings. An unsupported validator is scanned but not imported by the application tests.</p><p>No measured time savings or universal migration success is claimed. Dependency installation is performed by the test harness, not the codemod.</p>",
    )
    if evidence.exists():
        data: dict[str, Any] = json.loads(evidence.read_text(encoding="utf-8"))
        rows = ""
        for key, label in (
            ("paid", "Zipper Tools paid pack 0.1.2"),
            ("free", "bump-pydantic 0.8.0"),
        ):
            result = data["outcomes"][key]
            rows += f'<tr><th scope="row">{label}</th><td>{len(result["files_changed"])}</td><td>{"Passed" if result["tests_passed"] else "Failed — inspect output"}</td><td>{"Unchanged; JSON finding" if result["unsupported_file_unchanged"] else "Manual-review TODO added; validator not rewritten"}</td></tr>'
        proof_body += panel(
            "Recorded comparison",
            f'<p>Recorded {escape(data["recorded_at"][:10])}, Python {escape(data["python"])}. Baseline: FastAPI 0.119.0 / Pydantic 1.10.24. Target: FastAPI 0.119.0 / Pydantic 2.12.0. This deliberately isolates Pydantic changes; it does not prove compatibility with the latest FastAPI release.</p><div class="table-wrap"><table><thead><tr><th>Tool</th><th>Changed files</th><th>Application tests</th><th>Unsupported module</th></tr></thead><tbody>{rows}</tbody></table></div><p>Same original application and six assertions for each tool. The free tool is archived upstream but remains a valid alternative to evaluate. No claim of superior speed or coverage follows from this small example.</p>',
        )
        proof_body += panel(
            "Download the evidence",
            '<ul class="clean">'
            + "".join(
                f'<li><a href="case-study/{file}">{label}</a></li>'
                for file, label in (
                    ("results.json", "Versions, input hashes and command results"),
                    ("scan.json", "Public scan report"),
                    ("preview.json", "Non-mutating paid preview report"),
                    ("baseline-tests.txt", "Baseline validation summary"),
                    ("example-source.zip", "MIT-licensed example source ZIP"),
                    ("paid.json", "Paid apply report"),
                    ("paid.diff", "Paid preview diff / applied changes"),
                    ("free.diff", "Free tool diff"),
                    ("paid-tests.txt", "Paid validation summary"),
                    ("free-tests.txt", "Free validation summary"),
                )
            )
            + "</ul>",
        )
    else:
        proof_body += panel(
            "Verification pending",
            "<p>The comparison has not been recorded yet. Do not treat this example as verified.</p>",
        )
    proof_body += panel(
        "Reproduce and inspect",
        f'<p><a href="{REPO}/tree/main/proof/fastapi-orders">Application source and MIT license</a> · <a href="{REPO}/blob/main/scripts/verify_pydantic_case_study.py">Reproduction script</a></p><pre class="code-block">python scripts/verify_pydantic_case_study.py --pack path/to/extracted-paid-pack</pre><p>The script installs the public scanner from release v0.1.2, runs the unchanged baseline assertions, applies both tools to separate copies and reruns those assertions. Paid reproduction requires the purchased ZIP. All environments are isolated under test_runs.</p><p><a href="https://github.com/pydantic/bump-pydantic">Inspect the free alternative</a> · <a href="{FREE_GUIDE}">Official migration guidance</a></p>'
        + button("/scan#pydantic", "Try the free scan on your repo")
        + button(PRODUCT, "Compare the paid scope", True),
    )
    add(
        "proof/pydantic-v2-porter/index.html",
        "Pydantic migration: a tested FastAPI example",
        "Inspect the input, actual diffs, manual-review boundary and application test results before considering a purchase.",
        proof_body,
        "Reproducible proof",
    )
    return pages
