from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.build_site import build_site
from scripts.submit_indexnow import build_payload

# ruff: noqa: E501


def _build_output(name: str) -> Path:
    return Path.cwd() / "test_runs" / "site_builder" / name


def _assert_primary_nav_order(html: str) -> None:
    nav_html = html.split('<nav class="nav-links" aria-label="Primary">', 1)[1].split(
        "</nav>", 1
    )[0]
    labels = (
        "Scan",
        "Library",
        "Guides",
        "Pricing",
        "Policies",
        "Repo",
    )
    positions = [nav_html.index(f">{label}<") for label in labels]
    assert positions == sorted(positions)


def _assert_footer_nav_order(html: str) -> None:
    footer_html = html.split('<div class="footer-links">', 1)[1].split("</div>", 1)[0]
    labels = (
        "Scan",
        "Library",
        "Guides",
        "Pricing",
        "Demo",
        "Policies",
        "Repo",
    )
    positions = [footer_html.index(f">{label}<") for label in labels]
    assert positions == sorted(positions)


def test_build_site_generates_sitemaps_and_indexnow_key() -> None:
    site_dir = _build_output("sitemaps")
    manifest = build_site(site_dir)

    assert (site_dir / "guides" / "index.html").exists()
    assert (site_dir / "products" / "index.html").exists()
    assert (site_dir / "wells" / "index.html").exists()
    assert (site_dir / "wells" / "github-actions-upgrade-guard" / "index.html").exists()
    assert (site_dir / "products" / "actions-upgrade-guard" / "index.html").exists()
    assert (site_dir / "framework" / "index.html").exists()
    assert (site_dir / "proof" / "sqlalchemy-public-proof" / "index.html").exists()
    assert (site_dir / "proof" / "actions-upgrade-guard" / "index.html").exists()
    assert (
        site_dir / "proof" / "actions-upgrade-guard" / "actions-upgrade-report.json"
    ).exists()
    assert (
        site_dir / "proof" / "actions-upgrade-guard" / "actions-upgrade-report.html"
    ).exists()
    assert (
        site_dir / "proof" / "actions-upgrade-guard" / "patch-preview.diff"
    ).exists()
    assert (site_dir / "proof" / "pydantic-v2-porter" / "index.html").exists()
    assert (site_dir / "proof" / "flatconfig-lift" / "index.html").exists()
    proof_text = (
        site_dir / "proof" / "sqlalchemy-public-proof" / "index.html"
    ).read_text(encoding="utf-8")
    pydantic_proof_text = (
        site_dir / "proof" / "pydantic-v2-porter" / "index.html"
    ).read_text(encoding="utf-8")
    assert "Artifact trail" in proof_text
    assert "Sample repo before" in proof_text
    assert "Preview diff" in proof_text
    assert "Apply output" in proof_text
    assert "Final manager summary" in proof_text
    assert "Final report shape" in proof_text
    assert "Scan report" in pydantic_proof_text
    assert "Preview diff" in pydantic_proof_text
    assert "Apply output" in pydantic_proof_text
    assert "Validation summary" in pydantic_proof_text
    assert "Final manager summary" in pydantic_proof_text
    assert (site_dir / "sitemap.xml").exists()
    assert (site_dir / "sitemap-problem-pages.xml").exists()
    assert len(manifest["guides"]) >= 50
    assert len(manifest["urls"]["guides"]) >= 50
    assert (
        "https://zippertools.org/proof/sqlalchemy-public-proof/"
        in manifest["urls"]["proof"]
    )
    assert (
        "https://zippertools.org/proof/actions-upgrade-guard/"
        in manifest["urls"]["proof"]
    )
    assert (
        "https://zippertools.org/products/actions-upgrade-guard/"
        in manifest["urls"]["products"]
    )
    assert "https://zippertools.org/wells/" in manifest["urls"]["hubs"]
    assert "https://zippertools.org/framework/" in manifest["urls"]["hubs"]
    assert (
        "https://zippertools.org/proof/pydantic-v2-porter/" in manifest["urls"]["proof"]
    )
    assert (site_dir / f"{manifest['indexnow_key']}.txt").read_text(
        encoding="utf-8"
    ) == manifest["indexnow_key"]


def test_generated_guide_has_canonical_and_breadcrumb_schema() -> None:
    site_dir = _build_output("guide")
    build_site(site_dir)
    guide_text = (
        site_dir / "sqlalchemy" / "engine-execute-removed" / "index.html"
    ).read_text(encoding="utf-8")

    assert (
        'rel="canonical" href="https://zippertools.org/sqlalchemy/engine-execute-removed/"'
        in guide_text
    )
    assert '"@type": "BreadcrumbList"' in guide_text
    assert "How to fix engine.execute(...) removal in SQLAlchemy 2.0" in guide_text
    assert 'href="/products/sa20-pack/"' in guide_text
    assert 'href="/pricing#sa20-pack"' in guide_text
    assert 'href="/favicon.svg" type="image/svg+xml"' in guide_text


def test_error_message_pages_are_generated_and_linked() -> None:
    site_dir = _build_output("error_pages")
    build_site(site_dir)

    optionengine_text = (
        site_dir / "sqlalchemy" / "optionengine-execute-error" / "index.html"
    ).read_text(encoding="utf-8")
    checklist_text = (
        site_dir / "sqlalchemy" / "sqlalchemy-20-triage-checklist" / "index.html"
    ).read_text(encoding="utf-8")
    product_text = (site_dir / "products" / "sa20-pack" / "index.html").read_text(
        encoding="utf-8"
    )

    assert "'OptionEngine' object has no attribute 'execute'" in optionengine_text
    assert "SQLAlchemy 2.0 migration triage checklist" in checklist_text
    assert 'href="/sqlalchemy/optionengine-execute-error/"' in product_text
    assert 'href="/sqlalchemy/sqlalchemy-manual-vs-codemod/"' in product_text


def test_generated_redirects_preserve_legacy_paths_and_track_checkout() -> None:
    site_dir = _build_output("redirects")
    build_site(site_dir)
    redirects_text = (site_dir / "_redirects").read_text(encoding="utf-8")

    assert "/sqlalchemy-migration-tool /products/sa20-pack/ 301" in redirects_text
    assert (
        "/sqlalchemy-query-get-migration /sqlalchemy/session-query-get/ 301"
        in redirects_text
    )
    assert "/favicon.ico /favicon.svg 301" in redirects_text
    assert "/pricing /pricing.html 301" not in redirects_text
    assert "/pricing.html /pricing 301" in redirects_text
    assert "/policies.html /policies 301" in redirects_text
    assert (
        "/sqlalchemy-14-to-20-migration-pack.html /products/sa20-pack/ 301"
        in redirects_text
    )
    assert "/sqlalchemy-preset-bundle.html /pricing 301" in redirects_text
    assert (
        "/pydantic-basesettings-migration.html /pydantic/basesettings-moved/ 301"
        in redirects_text
    )
    assert "/products/sa20-pack/index.html /products/sa20-pack/ 301" in redirects_text
    assert (
        "/go/free-scan https://github.com/zippertools/sqlalchemy-14-to-20-codemod/blob/main/docs/quickstart.md"
        in redirects_text
    )
    assert (
        "/go/pydantic-free-scan https://github.com/zippertools/sqlalchemy-14-to-20-codemod/blob/main/products/pydantic-v2-porter/README.md"
        in redirects_text
    )
    assert (
        "/go/flatconfig-free-scan https://github.com/zippertools/sqlalchemy-14-to-20-codemod/blob/main/products/flatconfig-lift/README.md"
        in redirects_text
    )
    assert "utm_campaign=free_scan" in redirects_text
    assert (
        "/go/github-release https://github.com/zippertools/sqlalchemy-14-to-20-codemod/releases/tag/v0.1.2"
        in redirects_text
    )
    assert "/go/pydantic-free-scan/*" not in redirects_text
    assert "/go/pydantic-v2-porter/*" not in redirects_text
    assert "/scan.html /scan 301" in redirects_text
    assert "/sqlalchemy-2-migration-scan /scan 301" in redirects_text
    assert "/go/fit-report /pricing#fit-report 302" not in redirects_text
    assert "/go/fit-review /pricing#fit-report 301" not in redirects_text
    assert "/go/sa20-pack /pricing#sa20-pack 302" not in redirects_text
    assert "/go/sa20-preset /pricing#sa20-preset 302" not in redirects_text
    assert (
        "/go/pydantic-v2-porter /pricing#pydantic-v2-porter 302" not in redirects_text
    )
    assert "pay.zippertools.org" not in redirects_text
    assert (
        "/optionengine-object-has-no-attribute-execute /sqlalchemy/optionengine-execute-error/ 301"
        in redirects_text
    )
    assert (
        "/optionengine-object-has-no-attribute-execute.html /sqlalchemy/optionengine-execute-error/ 301"
        in redirects_text
    )
    assert (
        "/sqlalchemy-2-migration-checklist /sqlalchemy/sqlalchemy-20-triage-checklist/ 301"
        in redirects_text
    )


def test_product_pages_link_to_trackable_checkout_routes() -> None:
    site_dir = _build_output("product_pages")
    build_site(site_dir)

    sa20_text = (site_dir / "products" / "sa20-pack" / "index.html").read_text(
        encoding="utf-8"
    )
    pydantic_text = (
        site_dir / "products" / "pydantic-v2-porter" / "index.html"
    ).read_text(encoding="utf-8")

    assert 'href="/go/sa20-pack/product-products-sa20-pack"' in sa20_text
    assert (
        'href="/go/pydantic-v2-porter/product-products-pydantic-v2-porter"'
        in pydantic_text
    )
    assert (
        'href="/go/pydantic-free-scan/product-products-pydantic-v2-porter"'
        in pydantic_text
    )
    # SQLAlchemy buyer-path scan CTA routes to the controlled /scan page
    # rather than jumping straight to the GitHub quickstart redirect, so
    # buyers stay on-site for the first step. /scan still links out to the
    # GitHub quickstart as a secondary trust path.
    assert 'href="/scan"' in sa20_text
    assert 'href="/scan?source=product-products-sa20-pack"' not in sa20_text
    assert "/go/free-scan/product-products-sa20-pack" not in sa20_text
    assert "Run the SQLAlchemy scan first" in sa20_text
    assert "Run the Pydantic scan first" in pydantic_text
    assert "not the SQLAlchemy scanner" in pydantic_text
    assert "Buy cleanup pack - $299.99" in sa20_text
    assert "Buy Pydantic cleanup pack - $249.99" in pydantic_text
    assert 'href="/go/fit-report/product-products-sa20-pack"' in sa20_text
    assert 'href="/go/fit-report/product-products-pydantic-v2-porter"' in pydantic_text
    assert "Stripe Checkout handles secure payment and receipts." in sa20_text
    assert (
        "14-day refund review for published-scope or delivery mismatches."
        in pydantic_text
    )
    assert "SQLAlchemy 1.4 to 2.0 Migration Cleanup Pack" in sa20_text
    assert "Pydantic v1 to v2 Migration Cleanup Pack" in pydantic_text
    assert "After purchase, you receive" in sa20_text
    assert "After purchase, you receive" in pydantic_text
    assert "Preview/apply commands" in sa20_text
    assert "Supported rewrite table" in pydantic_text
    for product_text in (sa20_text, pydantic_text):
        assert "Apply output" in product_text
        assert "Validation summary" in product_text
        assert "Final manager summary" in product_text
    assert "license/support terms" in sa20_text
    assert sa20_text.index("After purchase, you receive") < sa20_text.index(
        "Do not use this if"
    )
    assert 'href="/proof/sqlalchemy-public-proof/"' in sa20_text
    assert 'href="/proof/pydantic-v2-porter/"' in pydantic_text
    assert 'href="/pricing#pydantic-v2-porter"' in pydantic_text


def test_fit_report_scope_is_not_offered_on_proof_only_eslint_pages() -> None:
    site_dir = _build_output("fit_report_scope")
    build_site(site_dir)

    pydantic_text = (
        site_dir / "products" / "pydantic-v2-porter" / "index.html"
    ).read_text(encoding="utf-8")
    eslint_text = (
        site_dir / "eslint" / "eslintrc-to-flat-config" / "index.html"
    ).read_text(encoding="utf-8")
    pricing_text = Path("docs/pricing.md").read_text(encoding="utf-8")
    store_text = Path("docs/store-products.md").read_text(encoding="utf-8")

    assert "SQLAlchemy/Pydantic Fit Report Add-on" in pricing_text
    assert "SQLAlchemy/Pydantic Fit Report Add-on" in store_text
    assert "separate Pydantic scanner" in pricing_text
    assert "/go/fit-report" in pydantic_text
    assert "/go/fit-report" not in eslint_text
    assert (
        "fit-report add-on is not listed for this proof-only product yet" in eslint_text
    )


def test_generated_links_and_sitemaps_use_clean_public_urls() -> None:
    site_dir = _build_output("clean_urls")
    build_site(site_dir)

    pricing_text = (site_dir / "sitemap-pages.xml").read_text(encoding="utf-8")
    product_text = (site_dir / "products" / "sa20-pack" / "index.html").read_text(
        encoding="utf-8"
    )
    proof_text = (
        site_dir / "proof" / "sqlalchemy-public-proof" / "index.html"
    ).read_text(encoding="utf-8")

    assert "https://zippertools.org/pricing.html" not in pricing_text
    assert "https://zippertools.org/pricing" in pricing_text
    assert "https://zippertools.org/scan" in pricing_text
    assert "index.html" not in product_text
    assert 'href="/products/"' in product_text
    for html in (product_text, proof_text):
        assert "Do not trust this blindly with your project" in html
        assert "does not expose the full paid apply engine" in html
        assert "Public proof is intentionally narrow" in html


def test_static_indexable_pages_use_clean_canonicals_and_links() -> None:
    pricing_text = Path("site/pricing.html").read_text(encoding="utf-8")
    demo_text = Path("site/demo.html").read_text(encoding="utf-8")
    index_text = Path("site/index.html").read_text(encoding="utf-8")
    scan_text = Path("site/scan.html").read_text(encoding="utf-8")
    policies_text = Path("site/policies.html").read_text(encoding="utf-8")
    config_text = Path("site/config.js").read_text(encoding="utf-8")

    assert 'href="https://zippertools.org/pricing"' in pricing_text
    assert 'content="https://zippertools.org/pricing"' in pricing_text
    assert 'href="https://zippertools.org/demo"' in demo_text
    assert 'content="https://zippertools.org/demo"' in demo_text
    assert 'href="pricing.html"' not in index_text
    assert 'href="sqlalchemy-migration-tool.html"' not in index_text
    assert 'freeStartUrl: "/go/free-scan"' in config_text
    assert 'paidPackUrl: "/go/sa20-pack"' in config_text
    assert 'actionGuardFreeScanUrl: "/go/actions-upgrade-guard-free"' in config_text
    assert 'presetBundleUrl: "/go/sa20-preset"' in config_text
    assert 'pydanticPackUrl: "/go/pydantic-v2-porter"' in config_text
    assert 'fitReportUrl: "/go/fit-report"' in config_text
    assert 'contactEmail: "support@zippertools.org"' in config_text
    assert "/go/actions-upgrade-guard-free/home-well-index" in index_text
    assert "/proof/actions-upgrade-guard/" in index_text
    assert "/wells/github-actions-upgrade-guard/" not in index_text
    assert "Autonomous deadline-readiness tools for software teams." in index_text
    assert "GitHub Actions Upgrade Guard" in index_text
    assert "Free scanner available" in index_text
    assert "Migration Sprint Sale" not in pricing_text
    assert "Price: $99 per team" in pricing_text
    assert "Buy automated fit report - $99" in pricing_text
    assert "Do not trust this blindly with your project" in index_text
    assert "does not expose the full paid apply engine" in index_text
    assert "Public proof is intentionally narrow" in index_text
    assert "Migration Sprint Sale" not in index_text
    for page_text in (scan_text, pricing_text, demo_text):
        assert "Migration Sprint Sale" not in page_text
        assert "90% off" not in page_text
    assert "Migration Sprint Sale" not in policies_text
    assert "Product Wells" in policies_text
    assert (
        "GitHub Actions Upgrade Guard is currently published as a free scanner"
        in policies_text
    )
    assert "Secure checkout is handled by Stripe." in pricing_text
    current_well_pos = index_text.index('<p class="kicker">Workflow checks</p>')
    free_scanner_pos = index_text.index('<p class="kicker">Free scanner</p>')
    library_pos = index_text.index('<p class="kicker">Migration Library</p>')
    assert current_well_pos < free_scanner_pos < library_pos
    assert "/products/sa20-pack/" in index_text
    assert "/products/pydantic-v2-porter/" in index_text
    assert "What deadline or migration are you checking?" in scan_text
    assert "/go/actions-upgrade-guard-free/scan-chooser" in scan_text
    assert "/go/pydantic-free-scan/scan-chooser" in scan_text
    assert "/go/flatconfig-free-scan/scan-chooser" in scan_text
    assert "Run a Product Well Scanner" in scan_text
    assert (
        "python -m pydantic_v2_porter.cli . --report migration-report.json" in scan_text
    )
    assert "not the SQLAlchemy scanner" in scan_text
    assert "Run a SQLAlchemy 2.0 Migration Scan" not in scan_text
    assert "Paid-pack artifact trail" in demo_text
    assert "Preview diff" in demo_text
    assert "Apply output" in demo_text
    assert "Validation result" in demo_text
    assert "Final manager report" in demo_text
    assert "Exact ZIP contents" in demo_text
    assert "sa20-pack-edge-case-pack.zip" in demo_text
    assert "/sample-deliverables/sa20-paid-sample/" in demo_text
    assert "/sample-deliverables/sa20-paid-sample.zip" in demo_text
    sample_dir = Path("site/sample-deliverables/sa20-paid-sample")
    assert (sample_dir / "preview-report.json").exists()
    assert (sample_dir / "apply-report.json").exists()
    assert (sample_dir / "validation-summary.txt").exists()
    assert (sample_dir / "manager-summary.md").exists()
    assert (sample_dir / "preview.diff").exists()
    assert (sample_dir / "ZIP-CONTENTS.txt").exists()
    assert '"mode": "preview"' in (sample_dir / "preview-report.json").read_text(
        encoding="utf-8"
    )
    assert '"mode": "apply"' in (sample_dir / "apply-report.json").read_text(
        encoding="utf-8"
    )
    for html in (index_text, scan_text, pricing_text, demo_text, policies_text):
        _assert_primary_nav_order(html)
        _assert_footer_nav_order(html)
        assert 'href="#" data-repo-link' not in html
        assert 'href="#" data-contact-link' not in html
        assert "support@zippertools.org" in html
        assert 'href="/policies#contact"' in html or 'href="policies#contact"' in html


def test_free_scan_install_path_uses_verified_archive_command() -> None:
    install_url = (
        "https://github.com/zippertools/"
        "sqlalchemy-14-to-20-codemod/archive/refs/tags/v0.1.2.zip"
    )
    pydantic_install_url = (
        "https://github.com/zippertools/"
        "sqlalchemy-14-to-20-codemod/archive/refs/tags/v0.1.2.zip#subdirectory=products/pydantic-v2-porter"
    )
    scan_text = Path("site/scan.html").read_text(encoding="utf-8")
    product_text = Path("site/products/sa20-pack/index.html").read_text(
        encoding="utf-8"
    )
    quickstart_text = Path("docs/quickstart.md").read_text(encoding="utf-8")
    pydantic_text = Path("products/pydantic-v2-porter/README.md").read_text(
        encoding="utf-8"
    )
    flatconfig_text = Path("products/flatconfig-lift/README.md").read_text(
        encoding="utf-8"
    )

    scan_command = "python -m sa20_pack.cli . --report migration-report.json"
    fallback_note = (
        "If installation fails, retry from the GitHub quickstart or contact "
        "support at support@zippertools.org."
    )
    normalized_fallback = " ".join(fallback_note.split())

    for text in (scan_text, quickstart_text):
        assert install_url in text
        assert "pip install sa20-pack" not in text
        assert scan_command in text
        assert normalized_fallback in " ".join(text.split())
        assert "python -m sa20_pack.cli path/to/repo" not in text

    for text in (product_text,):
        assert install_url in text
        assert scan_command in text
        assert normalized_fallback in " ".join(text.split())

    assert pydantic_install_url in pydantic_text
    assert (
        "sqlalchemy-14-to-20-codemod/archive/refs/heads/main.zip" not in pydantic_text
    )
    assert (
        "python -m pydantic_v2_porter.cli path/to/repo --report migration-report.json"
        in pydantic_text
    )
    assert f"{install_url}#subdirectory=products/flatconfig-lift" in flatconfig_text


def test_site_ctas_do_not_point_to_stale_or_cache_miss_prone_routes() -> None:
    site_dir = Path.cwd() / "site"
    build_site(site_dir)

    html_files = list(site_dir.rglob("*.html"))
    html_text = "\n".join(path.read_text(encoding="utf-8") for path in html_files)
    hrefs = set(re.findall(r'href="([^"]+)"', html_text))

    assert "derekmartin3737-coder" not in html_text
    assert "gmail.com" not in html_text
    assert "archive/refs/heads/main.zip" not in html_text
    assert 'href="/scan?source=' not in html_text
    assert "Cache miss" not in html_text

    go_hrefs = {href for href in hrefs if href.startswith("/go/")}
    assert go_hrefs
    for href in go_hrefs:
        assert href.startswith(
            (
                "/go/actions-upgrade-guard-free",
                "/go/free-scan",
                "/go/pydantic-free-scan",
                "/go/flatconfig-free-scan",
                "/go/fit-report",
                "/go/fit-review",
                "/go/sa20-pack",
                "/go/sa20-preset",
                "/go/pydantic-v2-porter",
                "/go/github-release",
            )
        )

    redirects_text = (site_dir / "_redirects").read_text(encoding="utf-8")
    assert "/go/pydantic-free-scan" in redirects_text
    assert (
        "github.com/zippertools/sqlalchemy-14-to-20-codemod/blob/main/products/pydantic-v2-porter"
        in redirects_text
    )


def test_indexnow_payload_uses_generated_manifest_groups() -> None:
    site_dir = _build_output("indexnow")
    build_site(site_dir)
    manifest = json.loads(
        (site_dir / "_site_manifest.json").read_text(encoding="utf-8")
    )

    payload = build_payload(manifest, ["static", "guides"])

    assert payload["host"] == "zippertools.org"
    assert payload["keyLocation"].endswith(".txt")
    assert "https://zippertools.org/" in payload["urlList"]
    assert any("/sqlalchemy/" in url for url in payload["urlList"])

    proof_payload = build_payload(manifest, ["proof"])

    assert (
        "https://zippertools.org/proof/sqlalchemy-public-proof/"
        in proof_payload["urlList"]
    )
    assert (
        "https://zippertools.org/proof/pydantic-v2-porter/" in proof_payload["urlList"]
    )
    assert "https://zippertools.org/proof/flatconfig-lift/" in proof_payload["urlList"]
