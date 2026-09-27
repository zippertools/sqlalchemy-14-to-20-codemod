"""Verify the deployed Zipper Tools public funnel.

This script intentionally fetches the public site the way a critic, crawler, or
buyer might see it: normal requests, no-cache requests, cache-busting query
strings, slash/non-slash page variants, runtime assets, and actual /go/ route
redirect targets.

Usage:

    python scripts/verify_live_funnel.py [--base-url https://zippertools.org]

Exits non-zero if any checked surface contains retired funnel copy or misses a
required trust/install/checkout string.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable
from dataclasses import dataclass, field

DEFAULT_BASE_URL = "https://zippertools.org"
REPO_URL = "https://github.com/zippertools/sqlalchemy-14-to-20-codemod"
PYDANTIC_REPO_URL = REPO_URL
RAW_REPO_URL = (
    "https://raw.githubusercontent.com/zippertools/sqlalchemy-14-to-20-codemod/main"
)
PYDANTIC_RAW_REPO_URL = "https://raw.githubusercontent.com/zippertools/sqlalchemy-14-to-20-codemod/main/products/pydantic-v2-porter"
GITHUB_API_CONTENTS_URL = (
    "https://api.github.com/repos/zippertools/sqlalchemy-14-to-20-codemod/contents"
)

SQLALCHEMY_INSTALL = (
    'python -m pip install "https://github.com/zippertools/'
    'sqlalchemy-14-to-20-codemod/archive/refs/tags/v0.1.2.zip"'
)
SQLALCHEMY_RUN = "python -m sa20_pack.cli . --report migration-report.json"
PYDANTIC_INSTALL = (
    'python -m pip install "https://github.com/zippertools/'
    'sqlalchemy-14-to-20-codemod/archive/refs/tags/v0.1.2.zip#subdirectory=products/pydantic-v2-porter"'
)
PYDANTIC_RUN = (
    "python -m pydantic_v2_porter.cli path/to/repo --report migration-report.json"
)
ACTION_GUARD_README_PATH = (
    "/zippertools/sqlalchemy-14-to-20-codemod/blob/main/"
    "products/actions-upgrade-guard/README.md"
)

FORBIDDEN_STRINGS: tuple[str, ...] = (
    "python -m pip install sa20-pack",
    "Planned checkout price",
    "Open fit report details",
    "Open fit report checkout",
    "Open checkout",
    "Questions: email",
    "Powered by Payhip",
    "pay.zippertools.org",
    "payhip",
)

FORBIDDEN_PROOF_ONLY_STRINGS: tuple[str, ...] = (
    "Secure checkout is handled by Stripe.",
)

BASE_PAGE_PATHS: tuple[str, ...] = (
    "/",
    "/wells/",
    "/wells/github-actions-upgrade-guard/",
    "/products/actions-upgrade-guard/",
    "/proof/actions-upgrade-guard/",
    "/framework/",
    "/scan",
    "/pricing",
    "/products/",
    "/products/sa20-pack/",
    "/products/pydantic-v2-porter/",
    "/products/flatconfig-lift/",
    "/proof/flatconfig-lift/",
    "/policies",
)

REQUIRED_BY_PATH: dict[str, tuple[str, ...]] = {
    "/": (
        "Autonomous deadline-readiness tools for software teams.",
        "GitHub Actions Upgrade Guard",
        "Run free Action Guard scanner",
        "Read proof and artifacts",
        "Free scanner available",
        "Support: support@zippertools.org",
    ),
    "/wells/": (
        "Product Wells archive",
        "GitHub Actions Upgrade Guard",
        "Promote by demand evidence",
    ),
    "/wells/github-actions-upgrade-guard/": (
        "GitHub Actions Upgrade Guard",
        "Run free Action Guard scanner",
        "Paid checkout is paused",
    ),
    "/products/actions-upgrade-guard/": (
        "Run the free scanner and review its findings.",
        "No checkout is listed for this proof page yet.",
        "Support: support@zippertools.org",
    ),
    "/proof/actions-upgrade-guard/": (
        "GitHub Actions Upgrade Guard proof artifacts",
        "Buyer-readable report excerpt",
        "Why this is not just actionlint",
        "Do not buy this if",
    ),
    "/framework/": (
        "The Product Wells method",
        "Hard filters",
        "Monthly cycle",
    ),
    "/scan": (
        SQLALCHEMY_INSTALL,
        SQLALCHEMY_RUN,
        "Support: support@zippertools.org",
    ),
    "/pricing": (
        "Price: $99 per team",
        "Price: $299.99 per team",
        "Price: $149.99 per team",
        "Price: $249.99 per team",
        "Buy automated fit report - $99",
        "Buy cleanup pack - $299.99",
        "Buy preset bundle - $149.99",
        "Buy Pydantic cleanup pack - $249.99",
        "Secure checkout is handled by Stripe.",
        "Support: support@zippertools.org",
    ),
    "/products/": (
        "Available now",
        "Example/proof page only",
        "Proof only - checkout not live yet",
        "Rollout checklist",
        "Manager summary template",
    ),
    "/products/sa20-pack/": (
        "After purchase, you receive",
        "Secure checkout is handled by Stripe.",
        "Support: support@zippertools.org",
    ),
    "/products/pydantic-v2-porter/": (
        PYDANTIC_INSTALL,
        (
            "The free scan link on this page opens the Pydantic scanner, "
            "not the SQLAlchemy scanner."
        ),
        "Secure checkout is handled by Stripe.",
        "Support: support@zippertools.org",
    ),
    "/products/flatconfig-lift/": ("No checkout is listed for this proof page yet.",),
    "/policies": (
        "Support:",
        "support@zippertools.org",
    ),
}

RUNTIME_ASSETS: dict[str, tuple[str, ...]] = {
    "/app.js": (
        "Sale price",
        "ctaLabelWithPrice",
        "commerce.secureCheckoutNote",
    ),
    "/product_catalog.mjs": (
        "GitHub Actions Upgrade Guard",
        "/go/actions-upgrade-guard-free",
        "SQLAlchemy/Pydantic Fit Report Add-on",
        "Migration Sprint Sale",
        "Buy automated fit report - ${saleCtaPrice(prices.fitReport)}",
        'secureCheckoutNote: "Secure checkout is handled by Stripe."',
    ),
}

KNOWN_FREE_SCAN_ROUTES: tuple[str, ...] = (
    "/go/actions-upgrade-guard-free/live-verify",
    "/go/free-scan/scan-install",
    "/go/free-scan/live-verify",
    "/go/pydantic-free-scan/product-products-pydantic-v2-porter",
    "/go/pydantic-free-scan/live-verify",
)

PAID_GO_ROUTES: tuple[str, ...] = (
    "/go/fit-report/live-verify",
    "/go/sa20-pack/live-verify",
    "/go/sa20-preset/live-verify",
    "/go/pydantic-v2-porter/live-verify",
)

RETIRED_PATHS: tuple[str, ...] = (
    "/payhip",
    "/payhip/old-product",
)


@dataclass
class FetchResult:
    url: str
    status: int
    final_url: str
    body: str
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def decoded_body(self) -> str:
        return html.unescape(self.body)

    @property
    def visible_text(self) -> str:
        without_scripts = re.sub(
            r"<(script|style)\b[^>]*>.*?</\1>",
            " ",
            self.body,
            flags=re.IGNORECASE | re.DOTALL,
        )
        without_tags = re.sub(r"<[^>]+>", " ", without_scripts)
        return normalize_text(html.unescape(without_tags))

    @property
    def searchable(self) -> str:
        return "\n".join(
            (
                self.decoded_body,
                self.visible_text,
                normalize_text(self.decoded_body),
            )
        )


@dataclass
class CheckResult:
    label: str
    url: str
    ok: bool
    failures: list[str] = field(default_factory=list)
    status: int | None = None
    final_url: str = ""


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def normalize_text(value: str) -> str:
    return " ".join(value.split())


def request_headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "User-Agent": "ZipperToolsLiveVerify/2.0 (+https://zippertools.org)",
    }
    if extra:
        headers.update(extra)
    return headers


def fetch(
    url: str,
    *,
    method: str = "GET",
    follow_redirects: bool = True,
    accept: str | None = None,
    timeout: float = 25.0,
    attempts: int = 3,
) -> FetchResult:
    last_error: BaseException | None = None
    opener = (
        urllib.request.build_opener()
        if follow_redirects
        else urllib.request.build_opener(NoRedirectHandler())
    )
    extra = {"Accept": accept} if accept else None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(
                url,
                method=method,
                headers=request_headers(extra),
            )
            with opener.open(req, timeout=timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
                return FetchResult(
                    url=url,
                    status=response.status,
                    final_url=response.geturl(),
                    body=body,
                    headers=dict(response.headers),
                )
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            return FetchResult(
                url=url,
                status=exc.code,
                final_url=exc.geturl(),
                body=body,
                headers=dict(exc.headers),
            )
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def with_query(path: str, params: dict[str, str]) -> str:
    parsed = urllib.parse.urlsplit(path)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query.extend(params.items())
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(query), "")
    )


def absolute_url(base_url: str, path_or_url: str) -> str:
    if path_or_url.startswith(("http://", "https://")):
        return path_or_url
    return urllib.parse.urljoin(f"{base_url.rstrip('/')}/", path_or_url.lstrip("/"))


def page_variants(path: str) -> list[str]:
    variants: list[str] = []
    candidates = [path]
    if path != "/":
        if path.endswith("/"):
            candidates.append(path.rstrip("/"))
        else:
            candidates.append(f"{path}/")
    for candidate in candidates:
        variants.append(candidate)
        variants.append(with_query(candidate, {"v": "manual-audit"}))
        variants.append(with_query(candidate, {"_cb": str(int(time.time()))}))
    return list(dict.fromkeys(variants))


def canonical_required_path(path: str) -> str:
    parsed = urllib.parse.urlsplit(path)
    clean = parsed.path or "/"
    if clean in {"", "/"}:
        return "/"
    if clean in {"/scan", "/scan/"}:
        return "/scan"
    if clean in {"/pricing", "/pricing/"}:
        return "/pricing"
    if clean in {"/policies", "/policies/"}:
        return "/policies"
    if clean.rstrip("/") == "/wells":
        return "/wells/"
    if clean.rstrip("/") == "/wells/github-actions-upgrade-guard":
        return "/wells/github-actions-upgrade-guard/"
    if clean.rstrip("/") == "/products/actions-upgrade-guard":
        return "/products/actions-upgrade-guard/"
    if clean.rstrip("/") == "/proof/actions-upgrade-guard":
        return "/proof/actions-upgrade-guard/"
    if clean.rstrip("/") == "/framework":
        return "/framework/"
    if clean.rstrip("/") == "/products":
        return "/products/"
    if clean.rstrip("/") == "/products/sa20-pack":
        return "/products/sa20-pack/"
    if clean.rstrip("/") == "/products/pydantic-v2-porter":
        return "/products/pydantic-v2-porter/"
    if clean.rstrip("/") == "/products/flatconfig-lift":
        return "/products/flatconfig-lift/"
    if clean.rstrip("/") == "/proof/flatconfig-lift":
        return "/proof/flatconfig-lift/"
    return clean


def assert_forbidden_absent(result: FetchResult) -> list[str]:
    failures: list[str] = []
    haystack = result.searchable.lower()
    if (
        "text/html" in result.headers.get("content-type", "")
        and "Migration Sprint Sale" in result.visible_text
    ):
        failures.append("Expired sale is visible")
    for forbidden in FORBIDDEN_STRINGS:
        if forbidden.lower() in haystack:
            failures.append(f'forbidden string present: "{forbidden}"')
    return failures


def assert_required_present(result: FetchResult, required: Iterable[str]) -> list[str]:
    failures: list[str] = []
    haystacks = (
        result.decoded_body,
        normalize_text(result.decoded_body),
        result.visible_text,
    )
    for required_text in required:
        if not any(required_text in haystack for haystack in haystacks):
            failures.append(f'required string missing: "{required_text}"')
    return failures


def check_page(base_url: str, path: str) -> CheckResult:
    url = absolute_url(base_url, path)
    try:
        result = fetch(url)
    except Exception as exc:
        return CheckResult(path, url, False, [str(exc)])

    failures = assert_forbidden_absent(result)
    required_path = canonical_required_path(path)
    required = REQUIRED_BY_PATH.get(required_path, ())
    failures.extend(assert_required_present(result, required))
    if result.status != 200:
        failures.append(f"expected HTTP 200 after redirects, got {result.status}")
    return CheckResult(
        label=path,
        url=url,
        ok=not failures,
        failures=failures,
        status=result.status,
        final_url=result.final_url,
    )


def hrefs_from_pages(base_url: str) -> set[str]:
    hrefs: set[str] = set()
    for path in BASE_PAGE_PATHS:
        try:
            result = fetch(absolute_url(base_url, path))
        except Exception:
            continue
        for href in re.findall(r'href=["\']([^"\']+)["\']', result.body):
            if href.startswith(
                (
                    "/go/actions-upgrade-guard-free",
                    "/go/free-scan",
                    "/go/pydantic-free-scan",
                )
            ):
                hrefs.add(href)
    return hrefs


def check_runtime_assets(base_url: str) -> list[CheckResult]:
    results: list[CheckResult] = []
    for path, required in RUNTIME_ASSETS.items():
        url = absolute_url(base_url, with_query(path, {"_cb": str(int(time.time()))}))
        try:
            result = fetch(url)
        except Exception as exc:
            results.append(CheckResult(path, url, False, [str(exc)]))
            continue
        failures = assert_forbidden_absent(result)
        failures.extend(assert_required_present(result, required))
        results.append(
            CheckResult(
                label=path,
                url=url,
                ok=not failures,
                failures=failures,
                status=result.status,
                final_url=result.final_url,
            )
        )
    return results


def no_redirect(base_url: str, path: str) -> FetchResult:
    return fetch(absolute_url(base_url, path), follow_redirects=False)


def check_free_scan_route(base_url: str, path: str) -> CheckResult:
    url = absolute_url(base_url, path)
    failures: list[str] = []
    try:
        redirect = no_redirect(base_url, path)
    except Exception as exc:
        return CheckResult(path, url, False, [str(exc)])

    location = redirect.headers.get("Location", "")
    if redirect.status not in {301, 302, 303, 307, 308} or not location:
        failures.append(f"expected redirect with Location, got HTTP {redirect.status}")
        return CheckResult(
            path,
            url,
            False,
            failures,
            redirect.status,
            redirect.final_url,
        )

    target = urllib.parse.urljoin(url, location)
    parsed = urllib.parse.urlsplit(target)
    required: tuple[str, ...]
    same_host = parsed.netloc == urllib.parse.urlsplit(base_url).netloc
    if same_host and parsed.path.rstrip("/") == "/scan":
        required = (SQLALCHEMY_INSTALL, SQLALCHEMY_RUN)
    elif parsed.netloc == "github.com" and parsed.path.endswith("/docs/quickstart.md"):
        required = (SQLALCHEMY_INSTALL, SQLALCHEMY_RUN)
    elif parsed.netloc == "github.com" and parsed.path == ACTION_GUARD_README_PATH:
        required = ("GitHub Actions Upgrade Guard", "actions_upgrade_guard.cli")
    elif parsed.netloc == "github.com" and parsed.path.endswith(
        "/sqlalchemy-14-to-20-codemod/blob/main/products/pydantic-v2-porter/README.md"
    ):
        required = (PYDANTIC_INSTALL, PYDANTIC_RUN)
    else:
        required = ()
        failures.append(f"unexpected free-scan target: {target}")

    try:
        target_result = fetch(target)
    except Exception as exc:
        failures.append(f"target fetch failed: {exc}")
        return CheckResult(path, url, False, failures, redirect.status, target)

    failures.extend(assert_forbidden_absent(target_result))
    failures.extend(assert_required_present(target_result, required))
    return CheckResult(
        label=path,
        url=url,
        ok=not failures,
        failures=failures,
        status=redirect.status,
        final_url=target,
    )


def check_github_docs() -> list[CheckResult]:
    checks = (
        (
            "GitHub raw SQLAlchemy quickstart",
            f"{RAW_REPO_URL}/docs/quickstart.md?_cb={int(time.time())}",
            (SQLALCHEMY_INSTALL, SQLALCHEMY_RUN),
            None,
        ),
        (
            "GitHub API SQLAlchemy quickstart",
            f"{GITHUB_API_CONTENTS_URL}/docs/quickstart.md?ref=main",
            (SQLALCHEMY_INSTALL, SQLALCHEMY_RUN),
            "application/vnd.github.raw",
        ),
        (
            "GitHub rendered SQLAlchemy quickstart",
            f"{REPO_URL}/blob/main/docs/quickstart.md?plain=1",
            (SQLALCHEMY_INSTALL, SQLALCHEMY_RUN),
            None,
        ),
        (
            "GitHub raw Pydantic README",
            f"{PYDANTIC_RAW_REPO_URL}/README.md?_cb={int(time.time())}",
            (PYDANTIC_INSTALL, PYDANTIC_RUN),
            None,
        ),
        (
            "GitHub rendered Pydantic README",
            f"{PYDANTIC_REPO_URL}/blob/main/products/pydantic-v2-porter/README.md?plain=1",
            (PYDANTIC_INSTALL, PYDANTIC_RUN),
            None,
        ),
    )
    results: list[CheckResult] = []
    for label, url, required, accept in checks:
        try:
            result = fetch(url, accept=accept)
        except Exception as exc:
            results.append(CheckResult(label, url, False, [str(exc)]))
            continue
        failures = assert_forbidden_absent(result)
        failures.extend(assert_required_present(result, required))
        results.append(
            CheckResult(
                label=label,
                url=url,
                ok=not failures,
                failures=failures,
                status=result.status,
                final_url=result.final_url,
            )
        )
    return results


def check_paid_routes(base_url: str) -> list[CheckResult]:
    results: list[CheckResult] = []
    for path in PAID_GO_ROUTES:
        url = absolute_url(base_url, path)
        failures: list[str] = []
        try:
            result = no_redirect(base_url, path)
        except Exception as exc:
            results.append(CheckResult(path, url, False, [str(exc)]))
            continue
        location = result.headers.get("Location", "")
        if result.status not in {301, 302, 303, 307, 308}:
            failures.append(f"expected Stripe redirect, got HTTP {result.status}")
            failures.extend(assert_forbidden_absent(result))
        elif not (
            location.startswith("https://checkout.stripe.com/")
            or location.startswith("https://buy.stripe.com/")
        ):
            failures.append(f"redirect did not point to Stripe checkout: {location}")
        results.append(
            CheckResult(
                label=path,
                url=url,
                ok=not failures,
                failures=failures,
                status=result.status,
                final_url=location,
            )
        )
    return results


def check_retired_paths(base_url: str) -> list[CheckResult]:
    results: list[CheckResult] = []
    for path in RETIRED_PATHS:
        url = absolute_url(base_url, path)
        failures: list[str] = []
        try:
            result = fetch(url, follow_redirects=False)
        except Exception as exc:
            results.append(CheckResult(path, url, False, [str(exc)]))
            continue
        if result.status == 404:
            pass
        elif result.status in {301, 302, 303, 307, 308}:
            location = result.headers.get("Location", "")
            parsed = urllib.parse.urlsplit(location)
            if parsed.netloc and parsed.netloc not in {
                "zippertools.org",
                "www.zippertools.org",
            }:
                failures.append(f"unsafe retired-path redirect: {location}")
        else:
            failures.append(f"expected 404 or safe redirect, got HTTP {result.status}")
        failures.extend(assert_forbidden_absent(result))
        results.append(
            CheckResult(
                label=path,
                url=url,
                ok=not failures,
                failures=failures,
                status=result.status,
                final_url=result.headers.get("Location", result.final_url),
            )
        )
    return results


def render_results(title: str, results: Iterable[CheckResult]) -> bool:
    print(f"\n[{title}]")
    overall_ok = True
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        http = "" if result.status is None else f" HTTP {result.status}"
        final = (
            f" -> {result.final_url}"
            if result.final_url and result.final_url != result.url
            else ""
        )
        print(f"  {status:4} {result.label}{http}{final}")
        if not result.ok:
            overall_ok = False
            for failure in result.failures:
                print(f"       - {failure}")
    return overall_ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Base URL to verify (default: %(default)s)",
    )
    parser.add_argument(
        "--skip-paid-routes",
        action="store_true",
        help="Skip live Stripe checkout route creation checks.",
    )
    parser.add_argument(
        "--skip-github",
        action="store_true",
        help="Skip GitHub raw/API/rendered quickstart checks.",
    )
    args = parser.parse_args(argv)

    page_paths: list[str] = []
    for path in BASE_PAGE_PATHS:
        page_paths.extend(page_variants(path))
    page_results = [check_page(args.base_url, path) for path in page_paths]

    runtime_results = check_runtime_assets(args.base_url)

    linked_free_routes = hrefs_from_pages(args.base_url)
    free_routes = sorted(set(KNOWN_FREE_SCAN_ROUTES) | linked_free_routes)
    free_route_results = [
        check_free_scan_route(args.base_url, path) for path in free_routes
    ]

    github_results: list[CheckResult] = []
    if not args.skip_github:
        github_results = check_github_docs()

    paid_results: list[CheckResult] = []
    if not args.skip_paid_routes:
        paid_results = check_paid_routes(args.base_url)

    retired_results = check_retired_paths(args.base_url)

    print(f"Verifying live funnel: {args.base_url}")
    pages_ok = render_results("public pages", page_results)
    runtime_ok = render_results("runtime assets", runtime_results)
    free_ok = render_results("free-scan redirects", free_route_results)
    github_ok = render_results("GitHub quickstarts", github_results)
    paid_ok = render_results("paid Stripe redirects", paid_results)
    retired_ok = render_results("retired checkout paths", retired_results)

    overall_ok = all((pages_ok, runtime_ok, free_ok, github_ok, paid_ok, retired_ok))
    print(f"\nOVERALL: {'PASS' if overall_ok else 'FAIL'}")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
