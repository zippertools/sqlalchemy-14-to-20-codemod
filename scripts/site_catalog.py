from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

# ruff: noqa: E501

SITE_NAME = "Zipper Tools"
SITE_URL = "https://zippertools.org"
INDEXNOW_KEY = "66d2924ff8a74b898f29b91e27b2fce8"
REPO_URL = "https://github.com/zippertools/sqlalchemy-14-to-20-codemod"
PYDANTIC_REPO_URL = "https://github.com/zippertools/pydantic-v1-to-v2-codemod"
PUBLIC_RELEASE_TAG = "v0.1.2"
PYDANTIC_RELEASE_TAG = "v0.1.2"
SUPPORT_EMAIL = "support@zippertools.org"
SA20_INSTALL_URL = f"{REPO_URL}/archive/refs/tags/{PUBLIC_RELEASE_TAG}.zip"
# pip's `#subdirectory=` fragment works on both git+ URLs and archive zip URLs.
# Use the archive form so users do not need a local git binary.
PYDANTIC_INSTALL_URL = (
    f"{REPO_URL}/archive/refs/tags/{PUBLIC_RELEASE_TAG}.zip"
    "#subdirectory=products/pydantic-v2-porter"
)
FLATCONFIG_INSTALL_URL = (
    f"{REPO_URL}/archive/refs/tags/{PUBLIC_RELEASE_TAG}.zip"
    "#subdirectory=products/flatconfig-lift"
)
ACTION_GUARD_FREE_SCAN_ROUTE = "/go/actions-upgrade-guard-free"
ACTION_GUARD_README_PATH = "products/actions-upgrade-guard/README.md"
PROOF_ONLY_CHECKOUT_NOTE = "No checkout is listed for this proof page yet."

CHECKOUT_PROVIDER = "Stripe"
SECURE_CHECKOUT_NOTE = f"Secure checkout is handled by {CHECKOUT_PROVIDER}."
CHECKOUT_LANGUAGE = f"{CHECKOUT_PROVIDER} Checkout handles secure payment and receipts."
DELIVERY_LANGUAGE = (
    "After payment, /stripe/delivery verifies the Stripe session and streams the "
    "purchased ZIP."
)
LOCAL_NO_UPLOAD_LANGUAGE = (
    "Runs locally; no hosted API, repo upload, or production credentials needed."
)
REFUND_LANGUAGE = "14-day refund review for published-scope or delivery mismatches."

FIT_REPORT_ROUTE = "/go/fit-report"
FIT_REPORT_REGULAR_PRICE = "$99"
FIT_REPORT_PRICE = FIT_REPORT_REGULAR_PRICE
FIT_REPORT_NAME = "SQLAlchemy/Pydantic Fit Report Add-on"
FIT_REPORT_LABEL = "SQLAlchemy/Pydantic fit report"
FIT_REPORT_PRODUCT_SLUGS = frozenset(("sa20-pack", "pydantic-v2-porter"))
FIT_REPORT_CTA = f"Buy automated fit report - {FIT_REPORT_PRICE}"
FIT_REPORT_SCOPE_NOTE = (
    "Use this only with SQLAlchemy or Pydantic scanner output. It is not listed "
    "for ESLint proof-only pages."
)

SA20_PRESET_NAME = "Migration Preset Bundle"
SA20_PRESET_PRICE = "149.99"
SA20_PRESET_CHECKOUT_PATH = "/go/sa20-preset"

STATUS_AVAILABLE = "Available now"
STATUS_PROOF_ONLY = "Example/proof page only"
STATUS_NOT_PURCHASABLE = "Not currently purchasable"


def price_to_cents(price: str) -> int:
    cents = (Decimal(price) * Decimal("100")).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    return int(cents)


def format_cents(cents: int) -> str:
    dollars = Decimal(cents) / Decimal("100")
    if cents % 100 == 0:
        return f"${dollars.quantize(Decimal('1'))}"
    return f"${dollars.quantize(Decimal('0.01'))}"


def price_display(price: str) -> str:
    return format_cents(price_to_cents(price))


def price_detail(price: str) -> str:
    return f"{price_display(price)} per team"


@dataclass(frozen=True)
class GuidePage:
    family: str
    slug: str
    title: str
    h1: str
    description: str
    search_term: str
    summary: str
    answer: str
    before_code: str
    after_code: str
    symptoms: tuple[str, ...]
    covers: tuple[str, ...]
    manual_review: tuple[str, ...]
    product_slug: str


@dataclass(frozen=True)
class ProductPage:
    slug: str
    name: str
    family: str
    description: str
    summary: str
    who_it_is_for: tuple[str, ...]
    proof_points: tuple[str, ...]
    not_for: tuple[str, ...]
    guide_slugs: tuple[str, ...]
    docs: tuple[tuple[str, str], ...]
    price: str = ""  # e.g., "299.00"
    currency: str = "USD"
    availability: str = "InStock"
    checkout_path: str = ""


FAMILY_TITLES = {
    "sqlalchemy": "SQLAlchemy Migration Guides",
    "pydantic": "Pydantic Migration Guides",
    "eslint": "ESLint Migration Guides",
}

FAMILY_DESCRIPTIONS = {
    "sqlalchemy": "Exact-problem pages for SQLAlchemy 1.4 to 2.0 breakages.",
    "pydantic": "Exact-problem pages for the safe Pydantic v1 to v2 subset.",
    "eslint": "Exact-problem pages for static ESLint config migration.",
}


GUIDES: tuple[GuidePage, ...] = (
    GuidePage(
        family="sqlalchemy",
        slug="session-query-get",
        title="Replace session.query(...).get(...) in SQLAlchemy 2.0",
        h1="How to replace session.query(...).get(...) in SQLAlchemy 2.0",
        description="Fix Query.get migrations and move identity lookups onto Session.get(...).",
        search_term="session.query get sqlalchemy 2.0",
        summary="This is one of the clearest SQLAlchemy 2.0 migrations and a strong codemod target.",
        answer=(
            "If the call is a direct primary-key lookup, the mechanical replacement is "
            "Session.get(Model, primary_key)."
        ),
        before_code="user = session.query(User).get(user_id)\njob = db_session.query(Job).get(job_id)\n",
        after_code="user = session.get(User, user_id)\njob = db_session.get(Job, job_id)\n",
        symptoms=(
            "Legacy Query.get(...) calls still show up in real repos.",
            "Teams want the easy 2.0 fixes first.",
            "Reviewers do not want to hand-edit dozens of lookup calls.",
        ),
        covers=(
            "Direct session.query(Model).get(pk) rewrites.",
            "Repo reporting for where the pattern appears.",
            "A scanner-first qualification path.",
        ),
        manual_review=(
            "Non-trivial Query chains before .get(...).",
            "Helper wrappers that hide the session object.",
            "Calls that are not direct primary-key lookups.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="session-query-migration",
        title="Session.query migration guide for SQLAlchemy 2.0",
        h1="What to do with session.query(...) during a SQLAlchemy 2.0 migration",
        description="Separate the easy Query cleanup from the broader Query-to-select refactor work.",
        search_term="session.query sqlalchemy 2.0 migration",
        summary="Query still exists in 2.0, but legacy breakages should be split from the bigger refactor bucket.",
        answer=(
            "Start with deterministic fixes like Query.get(...), string joins, string "
            "loader paths, and select([..]) list syntax. Treat broad Query-to-select "
            "rewrites as manual review."
        ),
        before_code=(
            "query = session.query(User)\n"
            "user = session.query(User).get(user_id)\n"
            'rows = session.query(User).join("addresses").all()\n'
        ),
        after_code=(
            "query = session.query(User)  # still legacy, not the first rewrite target\n"
            "user = session.get(User, user_id)\n"
            "rows = session.query(User).join(User.addresses).all()\n"
        ),
        symptoms=(
            "Teams think every Query call must be rewritten at once.",
            "A few safe fixes are buried inside broader churn.",
            "Reviewers need a clean staging plan.",
        ),
        covers=(
            "Repo-fit guidance for the safe Query cleanup subset.",
            "Internal links to the exact issue pages.",
            "A scanner-first path before paid tooling.",
        ),
        manual_review=(
            "Broad Query-to-select rewrites.",
            "Result-shape changes.",
            "App-specific loader strategy decisions.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="engine-execute-removed",
        title="Fix engine.execute(...) removal in SQLAlchemy 2.0",
        h1="How to fix engine.execute(...) removal in SQLAlchemy 2.0",
        description="Fix engine.execute removals and OptionEngine errors without pretending the replacement is always trivial.",
        search_term="engine.execute removed sqlalchemy 2.0",
        summary="This is a real migration pain point because there is not one safe automatic replacement.",
        answer=(
            "Move execution onto a Connection or Session and make transaction boundaries "
            "explicit. That is why honest tooling buckets engine.execute(...) as manual review."
        ),
        before_code='result = engine.execute("SELECT id FROM users")\nrows = engine.execute(stmt).fetchall()\n',
        after_code=(
            "from sqlalchemy import text\n\n"
            "with engine.connect() as conn:\n"
            '    result = conn.execute(text("SELECT id FROM users"))\n'
            "    rows = conn.execute(stmt).fetchall()\n"
        ),
        symptoms=(
            "OptionEngine and execute errors after the 2.0 bump.",
            "Old helpers still call engine.execute(...).",
            "Teams need a clear manual-review signal.",
        ),
        covers=(
            "Detection and classification of engine.execute(...) usage.",
            "Repo reporting for the manual bucket.",
            "Links to related SQLAlchemy guides.",
        ),
        manual_review=(
            "Choosing Connection versus Session.",
            "Raw SQL that needs text(...).",
            "Pandas and helper wrappers around execution.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="joinedload-all-removed",
        title="Clean up joinedload_all(...) in SQLAlchemy 2.0",
        h1="How to clean up joinedload_all(...) during a SQLAlchemy 2.0 migration",
        description="Replace joinedload_all(...) with mapped-attribute loader options and bucket the hard cases honestly.",
        search_term="joinedload_all removed sqlalchemy 2.0",
        summary="joinedload_all(...) is gone. Simple paths are fixable. Ambiguous paths should stay manual.",
        answer=(
            "Use joinedload(...) with mapped attributes when the relationship path is "
            "obvious. Stop when aliasing or dotted paths make the replacement unclear."
        ),
        before_code=(
            'query = session.query(User).options(joinedload_all("orders.items"))\n'
            'query = query.options(joinedload_all("addresses"))\n'
        ),
        after_code=(
            "query = session.query(User).options(\n"
            "    joinedload(User.orders).joinedload(Order.items)\n"
            ")\n"
            "query = query.options(joinedload(User.addresses))\n"
        ),
        symptoms=(
            "Loader options still use string paths.",
            "Teams want to know which paths are easy cleanup.",
            "Reviewers do not want a guessed loader strategy rewrite.",
        ),
        covers=(
            "Simple joinedload_all(...) replacements.",
            "Cross-links to string loader cleanup pages.",
            "Fail-closed reporting when the path is not straightforward.",
        ),
        manual_review=(
            "Alias-heavy loading.",
            "Dotted paths tied to query shape.",
            "contains_eager and custom join interactions.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="select-list-syntax",
        title="Fix select([..]) list syntax in SQLAlchemy 2.0",
        h1="How to replace select([..]) list syntax in SQLAlchemy 2.0",
        description="Drop the legacy select([..]) wrapper and move to direct select(...) calls.",
        search_term="select([ ]) sqlalchemy 2.0",
        summary="This is exactly the kind of syntax change that good codemods should automate first.",
        answer="Drop the wrapper list and pass the columns or table directly into select(...).",
        before_code="stmt = select([user_table])\nstmt = select([User.name, User.email])\n",
        after_code="stmt = select(user_table)\nstmt = select(User.name, User.email)\n",
        symptoms=(
            "Legacy list wrapper syntax still appears across multiple files.",
            "The fix is obvious but repetitive.",
            "Teams want proof that the easy cleanup is worth automating.",
        ),
        covers=(
            "Deterministic select([..]) to select(..) rewrites.",
            "Repo reporting for the syntax bucket.",
            "Links to the broader SQLAlchemy guide set.",
        ),
        manual_review=(
            "Calls already mixed with broader query redesign.",
            "Generated code that obscures the argument list.",
            "Files that also contain unsupported execution-path changes.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="string-join-paths",
        title="Replace string join paths in SQLAlchemy 2.0 migrations",
        h1="How to replace string join paths during a SQLAlchemy 2.0 migration",
        description='Replace simple join("addresses") and outerjoin("orders") calls with mapped attributes when the root entity is obvious.',
        search_term="sqlalchemy join string relationship 2.0",
        summary="Simple string relationship joins are good deterministic cleanup. Multi-hop join chains are not.",
        answer=(
            "When the root entity is obvious, replace the string path with the "
            "mapped attribute, like User.addresses or User.orders."
        ),
        before_code=(
            'query = session.query(User).join("addresses")\n'
            'query = query.outerjoin("orders")\n'
        ),
        after_code=(
            "query = session.query(User).join(User.addresses)\n"
            "query = query.outerjoin(User.orders)\n"
        ),
        symptoms=(
            "Legacy Query calls still join relationships by string name.",
            "The right replacement is obvious in the common root-entity case.",
            "Teams do not want to hand-fix dozens of repetitive join calls.",
        ),
        covers=(
            'Simple join("relationship") rewrites.',
            'Simple outerjoin("relationship") rewrites.',
            "Reporting for the string-join cleanup bucket.",
        ),
        manual_review=(
            'Multi-hop joins like join("orders", "items").',
            "Alias-heavy query builders.",
            "Cases where the root entity is not obvious from the call site.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="string-loader-options",
        title="Replace string loader options in SQLAlchemy 2.0",
        h1="How to replace string loader options in SQLAlchemy 2.0",
        description='Replace joinedload("addresses") and similar string loader options with mapped attributes when the relationship root is obvious.',
        search_term="joinedload string path sqlalchemy 2.0",
        summary="Simple loader strings are cleanup work. Dotted paths and query-shape-dependent options are not.",
        answer=(
            "For straightforward paths, replace the string with the mapped "
            "attribute, like joinedload(User.addresses)."
        ),
        before_code=(
            'query = session.query(User).options(joinedload("addresses"))\n'
            'query = query.options(selectinload("orders"))\n'
        ),
        after_code=(
            "query = session.query(User).options(joinedload(User.addresses))\n"
            "query = query.options(selectinload(User.orders))\n"
        ),
        symptoms=(
            "Loader options still depend on legacy string paths.",
            "The easy cases are repetitive but not conceptually hard.",
            "Teams need a clean stop signal before dotted or aliased paths.",
        ),
        covers=(
            "Simple joinedload/lazyload/selectinload/subqueryload string cleanup.",
            "Mapped-attribute replacements when the root entity is obvious.",
            "Cross-links to the dotted-path and joinedload_all manual buckets.",
        ),
        manual_review=(
            'Dotted paths like joinedload("orders.items").',
            "contains_eager and duplicate-join interactions.",
            "Cases where the owning entity is not obvious from the local code.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="declarative-imports",
        title="Move sqlalchemy.ext.declarative imports to sqlalchemy.orm",
        h1="How to move sqlalchemy.ext.declarative imports to sqlalchemy.orm",
        description="Replace legacy declarative_base and declared_attr imports from sqlalchemy.ext.declarative.",
        search_term="sqlalchemy.ext.declarative moved sqlalchemy.orm",
        summary="This is a clean import migration and a strong automation target.",
        answer=(
            "Import declarative_base and declared_attr from sqlalchemy.orm "
            "instead of sqlalchemy.ext.declarative."
        ),
        before_code=(
            "from sqlalchemy.ext.declarative import declarative_base, declared_attr\n"
        ),
        after_code=("from sqlalchemy.orm import declarative_base, declared_attr\n"),
        symptoms=(
            "Legacy declarative imports survive long after the runtime bump.",
            "The replacement is direct and low-risk.",
            "Teams want the syntax cleanup handled in the same migration pass.",
        ),
        covers=(
            "Direct declarative_base import rewrites.",
            "Direct declared_attr import rewrites.",
            "Reporting when mixed legacy imports need closer review.",
        ),
        manual_review=(
            "Mixed sqlalchemy.ext.declarative imports beyond the supported symbols.",
            "Indirect imports hidden behind helper modules.",
            "Files that already combine supported and blocked legacy patterns.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="insert-values-kwargs",
        title="Replace insert(..., values=...) in SQLAlchemy 2.0",
        h1="How to replace insert(..., values=...) in SQLAlchemy 2.0",
        description="Move legacy insert constructor kwargs onto the statement object with .values(...).",
        search_term="insert values keyword sqlalchemy 2.0",
        summary="Legacy DML constructor kwargs are repetitive syntax cleanup that good codemods should handle.",
        answer=("Build the statement first, then call .values({...}) on it."),
        before_code=('stmt = insert(user_table, values={"name": name})\n'),
        after_code=('stmt = insert(user_table).values({"name": name})\n'),
        symptoms=(
            "Insert helpers still rely on constructor kwargs from older SQLAlchemy code.",
            "The fix is obvious but spread across many files.",
            "Teams want the DML syntax cleanup folded into the same migration run.",
        ),
        covers=(
            "Direct insert(table, values=...) rewrites.",
            "Report entries for where the legacy constructor form still appears.",
            "Links to the matching update and delete pages.",
        ),
        manual_review=(
            "Calls wrapped in helper functions that reshape arguments.",
            "Generated SQL-builder code that obscures the constructor call.",
            "Files bundled with unsupported execution-path changes.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="update-values-kwargs",
        title="Replace update(..., whereclause=..., values=...) in SQLAlchemy 2.0",
        h1="How to replace update(..., whereclause=..., values=...) in SQLAlchemy 2.0",
        description="Move legacy update constructor kwargs onto the statement object with .where(...).values(...).",
        search_term="update whereclause values sqlalchemy 2.0",
        summary="The supported update case is syntax cleanup, not a semantic query rewrite.",
        answer=(
            "Build the update statement first, then chain .where(expr) and "
            ".values({...}) on it."
        ),
        before_code=(
            "stmt = update(\n"
            "    user_table,\n"
            "    whereclause=user_table.c.id == user_id,\n"
            '    values={"name": name},\n'
            ")\n"
        ),
        after_code=(
            "stmt = (\n"
            "    update(user_table)\n"
            "    .where(user_table.c.id == user_id)\n"
            '    .values({"name": name})\n'
            ")\n"
        ),
        symptoms=(
            "Legacy whereclause and values constructor kwargs still show up in Core code.",
            "The replacement shape is stable in the supported subset.",
            "Teams want the repetitive update cleanup removed from code review.",
        ),
        covers=(
            "Direct update(table, whereclause=..., values=...) rewrites.",
            "Repo reporting for the legacy update syntax bucket.",
            "Cross-links to the insert and delete constructor pages.",
        ),
        manual_review=(
            "Helper wrappers that compute where clauses indirectly.",
            "Generated code where the update call is assembled dynamically.",
            "Files that also contain unsupported transaction-bound changes.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="delete-whereclause",
        title="Replace delete(..., whereclause=...) in SQLAlchemy 2.0",
        h1="How to replace delete(..., whereclause=...) in SQLAlchemy 2.0",
        description="Move legacy delete constructor kwargs onto the statement object with .where(...).",
        search_term="delete whereclause sqlalchemy 2.0",
        summary="This is exactly the kind of legacy DML syntax change that benefits from deterministic cleanup.",
        answer=("Build the delete statement first, then chain .where(expr) on it."),
        before_code=(
            "stmt = delete(user_table, whereclause=user_table.c.id == user_id)\n"
        ),
        after_code=("stmt = delete(user_table).where(user_table.c.id == user_id)\n"),
        symptoms=(
            "Delete statements still use constructor kwargs from pre-2.0 style code.",
            "The mechanical fix is easy but repetitive.",
            "Teams want the scanner to separate syntax cleanup from execution changes.",
        ),
        covers=(
            "Direct delete(table, whereclause=...) rewrites.",
            "Report entries for legacy delete constructor usage.",
            "Links to the matching insert and update pages.",
        ),
        manual_review=(
            "Calls wrapped in app-specific delete helpers.",
            "Dynamic statement factories that obscure the call shape.",
            "Files that also contain unsupported engine.execute(...) cleanup.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="from-self-removed",
        title="What to do about Query.from_self() removal in SQLAlchemy 2.0",
        h1="What to do about Query.from_self() removal in SQLAlchemy 2.0",
        description="Treat Query.from_self() as a manual-review migration instead of pretending there is one safe automatic replacement.",
        search_term="from_self removed sqlalchemy 2.0",
        summary="from_self() is a real migration problem, but the replacement depends on query shape and result semantics.",
        answer=(
            "Keep Query.from_self() in manual review. The right replacement "
            "depends on the surrounding query structure and what rows should "
            "come back."
        ),
        before_code=(
            "query = session.query(User).filter(User.active == True).from_self(User.id)\n"
        ),
        after_code=(
            "# manual review required\n"
            "# replacement depends on the surrounding query and result shape\n"
        ),
        symptoms=(
            "Repos still depend on Query.from_self() in legacy ORM code.",
            "Teams want an honest stop signal instead of a guessed rewrite.",
            "Reviewers need to separate this from the easy Query cleanup bucket.",
        ),
        covers=(
            "Detection and reporting for Query.from_self() usage.",
            "Cross-links to the safe Query.get and string-join cleanup pages.",
            "Repo-fit guidance before buying the SQLAlchemy pack.",
        ),
        manual_review=(
            "Selecting the right select()/subquery replacement.",
            "Result-shape and column-projection decisions.",
            "Query chains that already need broader 2.0 redesign.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="multi-hop-string-joins",
        title="Why multi-hop string joins are a manual-review case in SQLAlchemy 2.0",
        h1="Why multi-hop string joins are a manual-review case in SQLAlchemy 2.0",
        description='Understand why join("orders", "items") belongs in manual review instead of a guessed codemod.',
        search_term="sqlalchemy join string multiple relationships 2.0",
        summary="Single relationship strings are automatable. Multi-hop string joins are not.",
        answer=(
            "Treat multi-hop string joins as manual review. The right mapped "
            "attribute chain depends on the surrounding entities and join shape."
        ),
        before_code=('query = session.query(User).join("orders", "items")\n'),
        after_code=(
            "# manual review required\n"
            "# replacement depends on the actual join path and root entity\n"
        ),
        symptoms=(
            "Legacy ORM code still passes multiple string relationship hops to join().",
            "The easy single-hop replacements are mixed with a smaller hard bucket.",
            "Reviewers need a clear line between supported and blocked join cleanup.",
        ),
        covers=(
            "Detection and explicit reporting for multi-hop string joins.",
            "Cross-links to the supported simple string-join page.",
            "Repo-fit guidance before buying the SQLAlchemy pack.",
        ),
        manual_review=(
            "Choosing the correct mapped attribute chain.",
            "Aliased joins and query-shape-dependent paths.",
            "Cases bundled with other removed Query helpers.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="pydantic",
        slug="validator-to-field-validator",
        title="Replace @validator with @field_validator in Pydantic v2",
        h1="How to replace @validator with @field_validator in Pydantic v2",
        description="Fix simple Pydantic validator migrations and keep signature-heavy cases out of the automatic path.",
        search_term="validator field_validator pydantic v2",
        summary="Direct imports and simple validator signatures are good automation targets. The rest should stop cleanly.",
        answer=(
            "If the validator uses the supported direct-import path and the simple "
            "classmethod signature, the clean rewrite is @field_validator."
        ),
        before_code=(
            "from pydantic import BaseModel, validator\n\n"
            "class UserModel(BaseModel):\n"
            "    email: str\n\n"
            '    @validator("email")\n'
            "    def normalize_email(cls, value: str) -> str:\n"
            "        return value.strip().lower()\n"
        ),
        after_code=(
            "from pydantic import BaseModel, field_validator\n\n"
            "class UserModel(BaseModel):\n"
            "    email: str\n\n"
            '    @field_validator("email")\n'
            "    def normalize_email(cls, value: str) -> str:\n"
            "        return value.strip().lower()\n"
        ),
        symptoms=(
            "The repo still imports validator from pydantic or pydantic.v1.",
            "Simple validators are mixed with a smaller hard bucket.",
            "Teams want deterministic migration first.",
        ),
        covers=(
            "Direct validator to field_validator rewrites.",
            "Repo reporting for supported files.",
            "Links to related Pydantic guides.",
        ),
        manual_review=(
            "Validators that use values, field, config, each_item, or always.",
            "Alias-heavy imports.",
            "Decorator wrappers and meta-programming.",
        ),
        product_slug="pydantic-v2-porter",
    ),
    GuidePage(
        family="pydantic",
        slug="basesettings-moved",
        title="Move BaseSettings to pydantic-settings in Pydantic v2",
        h1="How to move BaseSettings to pydantic-settings in Pydantic v2",
        description="Fix BaseSettings migrations for Pydantic v2 and keep config cleanup inside the supported subset.",
        search_term="BaseSettings moved pydantic v2",
        summary="BaseSettings left core Pydantic, so the migration is both an import move and a config cleanup.",
        answer=(
            "Import BaseSettings from pydantic_settings and update supported Config "
            "keys when the settings class stays inside the safe subset."
        ),
        before_code="from pydantic import BaseSettings\n\nclass Settings(BaseSettings):\n    api_url: str\n",
        after_code="from pydantic_settings import BaseSettings\n\nclass Settings(BaseSettings):\n    api_url: str\n",
        symptoms=(
            "BaseSettings imports break after the v2 bump.",
            "Settings models often also carry Config migrations.",
            "Teams want one pass that separates easy moves from hard ones.",
        ),
        covers=(
            "Direct BaseSettings import moves.",
            "Connected safe Config-to-model_config cleanup.",
            "Cross-links to the model_config guide.",
        ),
        manual_review=(
            "Removed config keys.",
            "Indirect imports and wrappers.",
            "Files that already depend on unsupported validator signatures.",
        ),
        product_slug="pydantic-v2-porter",
    ),
    GuidePage(
        family="pydantic",
        slug="config-to-model-config",
        title="Convert Config to model_config in Pydantic v2",
        h1="How to convert Config to model_config in Pydantic v2",
        description="Convert safe nested Config classes into model_config and refuse removed keys.",
        search_term="Config to model_config pydantic v2",
        summary="The safe case is a nested Config class with known key renames. The unsafe case is everything else.",
        answer=(
            "Move supported Config values into model_config and rename the keys "
            "that have a direct Pydantic v2 equivalent."
        ),
        before_code=(
            "class Config:\n"
            "    orm_mode = True\n"
            "    allow_population_by_field_name = True\n"
        ),
        after_code=(
            "model_config = ConfigDict(\n"
            "    from_attributes=True,\n"
            "    populate_by_name=True,\n"
            ")\n"
        ),
        symptoms=(
            "Safe config renames are mixed with removed keys.",
            "Teams want one report that shows both supported and blocked files.",
            "Reviewers need proof that the porter will not bluff through removed keys.",
        ),
        covers=(
            "Supported Config to model_config conversion.",
            "Known key renames in the safe subset.",
            "Manual-review findings for removed or unsupported keys.",
        ),
        manual_review=(
            "Removed config keys.",
            "Config logic that depends on project-specific behavior.",
            "Alias-heavy imports in the same file.",
        ),
        product_slug="pydantic-v2-porter",
    ),
    GuidePage(
        family="pydantic",
        slug="validate-arguments",
        title="Replace validate_arguments with validate_call in Pydantic v2",
        h1="How to replace validate_arguments with validate_call in Pydantic v2",
        description="Fix validate_arguments migrations and keep the rewrite narrow enough to stay deterministic.",
        search_term="validate_arguments validate_call pydantic v2",
        summary="This is a clean decorator migration when the import path is direct and the decorator is bare.",
        answer="The direct decorator rename is validate_call. Stop when the decorator is wrapped or aliased.",
        before_code=(
            "from pydantic import validate_arguments\n\n"
            "@validate_arguments\n"
            "def create_user(email: str, age: int) -> None:\n"
            "    ...\n"
        ),
        after_code=(
            "from pydantic import validate_call\n\n"
            "@validate_call\n"
            "def create_user(email: str, age: int) -> None:\n"
            "    ...\n"
        ),
        symptoms=(
            "Decorators still use validate_arguments after the v2 bump.",
            "Teams want the easy decorator rename handled automatically.",
            "Migration should stop if the decorator is wrapped or aliased.",
        ),
        covers=(
            "Direct validate_arguments to validate_call rewrites.",
            "Reporting for exactly where the decorator still appears.",
            "Links to the other direct-import Pydantic pages.",
        ),
        manual_review=(
            "Aliased decorator imports.",
            "Decorator wrappers.",
            "Files bundled with unsupported validator signatures.",
        ),
        product_slug="pydantic-v2-porter",
    ),
    GuidePage(
        family="pydantic",
        slug="root-validator-pre",
        title='Replace @root_validator(pre=True) with @model_validator(mode="before")',
        h1='How to replace @root_validator(pre=True) with @model_validator(mode="before")',
        description="Migrate the supported pre root-validator subset in Pydantic v2 and keep the rest out of the automatic path.",
        search_term="root_validator pre model_validator pydantic v2",
        summary="The safe root-validator case is pre=True with the simple (cls, values) classmethod signature.",
        answer=(
            "For supported pre=True root validators with the simple (cls, values) "
            'signature, the v2 replacement is @model_validator(mode="before").'
        ),
        before_code=(
            "from pydantic import BaseModel, root_validator\n\n"
            "class Payload(BaseModel):\n"
            "    name: str\n\n"
            "    @root_validator(pre=True)\n"
            "    def normalize_input(cls, values):\n"
            "        return values\n"
        ),
        after_code=(
            "from pydantic import BaseModel, model_validator\n\n"
            "class Payload(BaseModel):\n"
            "    name: str\n\n"
            '    @model_validator(mode="before")\n'
            "    def normalize_input(cls, values):\n"
            "        return values\n"
        ),
        symptoms=(
            "Repos still use pre=True root validators from Pydantic v1.",
            "Teams want the clean decorator migration handled automatically.",
            "Reviewers need a stop signal before post validators or custom signatures.",
        ),
        covers=(
            'pre=True root_validator to model_validator(mode="before") rewrites.',
            "Reporting for exactly where the supported root-validator subset appears.",
            "Cross-links to the post root-validator manual bucket.",
        ),
        manual_review=(
            "Post root validators.",
            "root_validator kwargs outside pre=True.",
            "Signatures more complex than exact (cls, values).",
        ),
        product_slug="pydantic-v2-porter",
    ),
    GuidePage(
        family="pydantic",
        slug="root-validator-post",
        title="Why post root validators need manual review in Pydantic v2",
        h1="Why post root validators need manual review in Pydantic v2",
        description="Understand why post root validators are outside the deterministic migration path.",
        search_term="root_validator post pydantic v2",
        summary="Post root validators are not a one-line decorator rename because the semantics change with the model lifecycle.",
        answer=(
            "Treat post root validators as manual review. The replacement "
            "depends on when validation should run and what object shape the "
            "code expects."
        ),
        before_code=(
            "from pydantic import BaseModel, root_validator\n\n"
            "class Payload(BaseModel):\n"
            "    @root_validator\n"
            "    def check_consistency(cls, values):\n"
            "        return values\n"
        ),
        after_code=(
            "# manual review required\n"
            "# post root validators do not have one safe mechanical replacement\n"
        ),
        symptoms=(
            "The repo still depends on post root-validator behavior from Pydantic v1.",
            "The migration needs a clean red flag instead of a guessed decorator swap.",
            "Teams want to know fast which validators stay in manual review.",
        ),
        covers=(
            "Detection and explicit reporting for post root validators.",
            "Cross-links to the supported pre=True root-validator page.",
            "Repo-fit guidance before running the paid porter.",
        ),
        manual_review=(
            "Choosing the right model_validator mode.",
            "Signature and lifecycle decisions tied to app behavior.",
            "Files that already mix supported and blocked validator changes.",
        ),
        product_slug="pydantic-v2-porter",
    ),
    GuidePage(
        family="pydantic",
        slug="pydantic-v1-imports",
        title="Move pydantic.v1 imports onto pydantic in the safe v2 subset",
        h1="How to move pydantic.v1 imports onto pydantic in the safe Pydantic v2 subset",
        description="Rewrite direct pydantic.v1 imports when the imported symbols stay inside the supported v2 subset.",
        search_term="pydantic.v1 import path pydantic v2",
        summary="Direct import path cleanup is deterministic as long as the symbols stay in the supported subset.",
        answer=(
            "For supported direct imports, move from pydantic.v1 back to "
            "pydantic. Keep BaseSettings and unsupported decorators in their own "
            "migration buckets."
        ),
        before_code=("from pydantic.v1 import BaseModel, ValidationError\n"),
        after_code=("from pydantic import BaseModel, ValidationError\n"),
        symptoms=(
            "Repos still pin import paths to pydantic.v1 after starting the v2 migration.",
            "Teams want the import cleanup separated from the harder validator and config work.",
            "Reviewers need proof that the porter will not touch unsupported symbols by guesswork.",
        ),
        covers=(
            "Direct pydantic.v1 import-path rewrites in the supported subset.",
            "Cross-links to the BaseSettings and validator pages.",
            "Repo reporting for files that still rely on pydantic.v1 imports.",
        ),
        manual_review=(
            "Aliased imports.",
            "Imports that include BaseSettings or other moved symbols.",
            "Files that also contain unsupported validator/config patterns.",
        ),
        product_slug="pydantic-v2-porter",
    ),
    GuidePage(
        family="pydantic",
        slug="config-fields-removed",
        title="Why Config.fields is a manual-review case in Pydantic v2",
        h1="Why Config.fields is a manual-review case in Pydantic v2",
        description="Config.fields was removed in Pydantic v2, so this is not a simple model_config rename.",
        search_term="Config fields removed pydantic v2",
        summary="Some Config keys have a direct rename. Config.fields does not.",
        answer=(
            "Treat Config.fields as manual review. It was removed in Pydantic v2, "
            "so the migration depends on what behavior the model actually needs."
        ),
        before_code=('class Config:\n    fields = {"name": {"alias": "full_name"}}\n'),
        after_code=(
            "# manual review required\n# Config.fields was removed in Pydantic v2\n"
        ),
        symptoms=(
            "Teams expect every Config key to become a simple model_config entry.",
            "The porter needs to stop cleanly on removed keys instead of bluffing through them.",
            "Reviewers want a clear list of which files still need manual follow-up.",
        ),
        covers=(
            "Explicit findings for removed Config keys like fields.",
            "Cross-links to the supported Config-to-model_config page.",
            "Repo-fit guidance before buying the porter.",
        ),
        manual_review=(
            "Choosing the right replacement behavior per model.",
            "Files that also combine supported and unsupported Config keys.",
            "Any config logic that depends on project-specific validation behavior.",
        ),
        product_slug="pydantic-v2-porter",
    ),
    GuidePage(
        family="pydantic",
        slug="validator-each-item",
        title="Why @validator(each_item=True) needs manual review in Pydantic v2",
        h1="Why @validator(each_item=True) needs manual review in Pydantic v2",
        description="Understand why validator(each_item=True) stays outside the deterministic migration path.",
        search_term="validator each_item pydantic v2",
        summary="Simple validators are automatable. each_item=True is not in the current safe subset.",
        answer=(
            "Treat validator(each_item=True) as manual review. The replacement "
            "depends on how item-level validation should be expressed in the "
            "target model."
        ),
        before_code=(
            "from pydantic import BaseModel, validator\n\n"
            "class Payload(BaseModel):\n"
            "    tags: list[str]\n\n"
            '    @validator("tags", each_item=True)\n'
            "    def normalize_tag(cls, value: str) -> str:\n"
            "        return value.strip()\n"
        ),
        after_code=(
            "# manual review required\n"
            "# validator(each_item=True) is outside the deterministic porter subset\n"
        ),
        symptoms=(
            "The repo still uses each_item=True validators from Pydantic v1.",
            "The easy validator renames are mixed with a smaller hard bucket.",
            "Teams need a fail-closed report instead of a guessed replacement.",
        ),
        covers=(
            "Explicit unsupported-validator-each-item findings.",
            "Cross-links to the supported @validator to @field_validator page.",
            "Repo-fit guidance before running the paid porter.",
        ),
        manual_review=(
            "Choosing the right item-level validation expression in v2.",
            "Validators that also depend on values, field, or config.",
            "Files with other unsupported decorator signatures.",
        ),
        product_slug="pydantic-v2-porter",
    ),
    GuidePage(
        family="pydantic",
        slug="validate-arguments-configured",
        title="Why configured @validate_arguments needs manual review in Pydantic v2",
        h1="Why configured @validate_arguments needs manual review in Pydantic v2",
        description="Configured validate_arguments decorators are outside the current deterministic migration subset.",
        search_term="validate_arguments kwargs pydantic v2",
        summary="Bare validate_arguments is a clean rename. Configured validate_arguments is not.",
        answer=(
            "Keep configured @validate_arguments decorators in manual review. "
            "The replacement depends on the decorator options and call-site "
            "behavior."
        ),
        before_code=(
            "from pydantic import validate_arguments\n\n"
            '@validate_arguments(config={"arbitrary_types_allowed": True})\n'
            "def create_user(user) -> None:\n"
            "    ...\n"
        ),
        after_code=(
            "# manual review required\n"
            "# configured validate_arguments decorators are outside the supported subset\n"
        ),
        symptoms=(
            "The repo already moved beyond bare validate_arguments usage.",
            "Teams want the porter to distinguish easy decorator renames from the harder cases.",
            "Reviewers need an explicit report entry for configured decorator usage.",
        ),
        covers=(
            "Explicit unsupported-validate-arguments findings for configured decorators.",
            "Cross-links to the supported bare validate_arguments page.",
            "Repo-fit guidance before buying the porter.",
        ),
        manual_review=(
            "Decorator config options that change runtime behavior.",
            "Wrapped or aliased decorator usage.",
            "Files bundled with unsupported validator signatures or config migrations.",
        ),
        product_slug="pydantic-v2-porter",
    ),
    GuidePage(
        family="eslint",
        slug="eslintrc-to-flat-config",
        title="Migrate .eslintrc to eslint.config.cjs with FlatCompat",
        h1="How to migrate .eslintrc to eslint.config.cjs with FlatCompat",
        description="Convert static .eslintrc JSON or YAML into eslint.config.cjs without executing JS logic.",
        search_term="eslintrc to flat config",
        summary="The honest path is to bridge static config with FlatCompat and stop on JS-backed config.",
        answer=(
            "If the source config is static JSON or YAML data, the bridge file can "
            "be generated deterministically."
        ),
        before_code=(
            "{\n"
            '  "extends": ["eslint:recommended"],\n'
            '  "rules": {"no-console": "warn"}\n'
            "}\n"
        ),
        after_code=(
            'const { FlatCompat } = require("@eslint/eslintrc");\n'
            "const compat = new FlatCompat();\n\n"
            "module.exports = [\n"
            "  ...compat.config({\n"
            '    extends: ["eslint:recommended"],\n'
            '    rules: { "no-console": "warn" },\n'
            "  }),\n"
            "];\n"
        ),
        symptoms=(
            "The repo still has a static .eslintrc file.",
            "The team wants a bridge, not a plugin-by-plugin rewrite party.",
            "People need a clear stop signal on JS configs.",
        ),
        covers=(
            "Static JSON and YAML config discovery.",
            "FlatCompat bridge generation in the supported subset.",
            "Manual-review findings for JS configs and existing flat config files.",
        ),
        manual_review=(
            ".eslintrc.js, .cjs, or .mjs logic.",
            "Repos that already have eslint.config.*.",
            "Ambiguous ignore rules that do not map cleanly.",
        ),
        product_slug="flatconfig-lift",
    ),
    GuidePage(
        family="eslint",
        slug="package-json-eslintconfig",
        title="Migrate package.json eslintConfig to flat config",
        h1="How to migrate package.json eslintConfig to flat config",
        description="Convert static package.json eslintConfig blocks into flat config without evaluating JS.",
        search_term="package.json eslintConfig flat config",
        summary="package.json eslintConfig is a good automation target because the source is structured data.",
        answer=(
            "When the repo exposes one static eslintConfig source in package.json, "
            "the bridge file can be generated cleanly."
        ),
        before_code=(
            '"eslintConfig": {\n'
            '  "extends": ["eslint:recommended"],\n'
            '  "env": {"node": true}\n'
            "}\n"
        ),
        after_code=(
            "module.exports = [\n"
            "  ...compat.config({\n"
            '    extends: ["eslint:recommended"],\n'
            "    env: { node: true },\n"
            "  }),\n"
            "];\n"
        ),
        symptoms=(
            "The repo never had a standalone .eslintrc file.",
            "Teams need a deterministic config export before plugin cleanup.",
            "Reviewers want to know whether multiple config sources block the easy path.",
        ),
        covers=(
            "Static package.json eslintConfig discovery and reporting.",
            "Generated FlatCompat bridge in the supported subset.",
            "Manual-review findings for multiple config sources.",
        ),
        manual_review=(
            "Multiple ESLint config sources in one repo.",
            "Existing flat config files.",
            "JS-driven config logic outside static data.",
        ),
        product_slug="flatconfig-lift",
    ),
    GuidePage(
        family="eslint",
        slug="eslintrc-js-unsupported",
        title="Why .eslintrc.js is a manual-review case for flat config migration",
        h1="Why .eslintrc.js is a manual-review case for flat config migration",
        description="Understand why JS-backed ESLint configs are out of scope for deterministic flat-config migration.",
        search_term=".eslintrc.js flat config migration",
        summary="JS config files look close to static config until they are not. Good tooling should report them, not execute them.",
        answer=(
            "Treat .eslintrc.js and its cousins as a repo-fit boundary. The honest "
            "move is to detect them, report them, and leave them untouched."
        ),
        before_code=(
            "module.exports = {\n"
            '  extends: ["eslint:recommended"],\n'
            '  rules: process.env.CI ? { "no-console": "error" } : {},\n'
            "};\n"
        ),
        after_code="// manual review required\n// keep logic-bearing config out of the deterministic path\n",
        symptoms=(
            "The repo config contains logic, not static data.",
            "The migration needs a clean red flag instead of a false promise.",
            "Teams want to know fast whether the repo is a fit.",
        ),
        covers=(
            "Explicit unsupported-js-config findings.",
            "Fast repo qualification before buying the flat-config pack.",
            "Links to the supported static-config guides.",
        ),
        manual_review=(
            "Any JS config that computes env, plugins, or rules.",
            "Module imports inside the config file.",
            "Repos that already started a custom flat config migration.",
        ),
        product_slug="flatconfig-lift",
    ),
    GuidePage(
        family="eslint",
        slug="eslintignore-migration",
        title="Move .eslintignore patterns into flat config",
        h1="How to move .eslintignore patterns into flat config",
        description="Carry straightforward .eslintignore and ignorePatterns entries into flat config while keeping the hard cases explicit.",
        search_term=".eslintignore flat config",
        summary="Simple ignore patterns are portable. Negated and malformed patterns are not.",
        answer=(
            "Move straightforward ignore patterns into the flat config ignores "
            "list. Stop when a pattern is negated or otherwise ambiguous."
        ),
        before_code=("dist/\ncoverage/\n"),
        after_code=(
            "module.exports = [\n"
            "  {\n"
            '    ignores: ["**/dist", "**/coverage"],\n'
            "  },\n"
            "];\n"
        ),
        symptoms=(
            "The repo still relies on .eslintignore or ignorePatterns.",
            "The migration needs a clean carry-forward path for simple ignores.",
            "Reviewers want to know which ignore rules stay safe and which do not.",
        ),
        covers=(
            "Straightforward .eslintignore pattern normalization.",
            "Straightforward ignorePatterns migration from static configs.",
            "Cross-links to the negated-pattern manual bucket.",
        ),
        manual_review=(
            "Negated ignore patterns.",
            "Non-string ignorePatterns entries.",
            "Ignore logic bundled with unsupported JS config files.",
        ),
        product_slug="flatconfig-lift",
    ),
    GuidePage(
        family="eslint",
        slug="negated-ignore-patterns",
        title="Why negated ignore patterns need manual review in flat config migration",
        h1="Why negated ignore patterns need manual review in flat config migration",
        description="Understand why negated ignore rules belong in manual review instead of a guessed flat-config translation.",
        search_term="negated ignore patterns flat config",
        summary="Simple ignore rules can move mechanically. Negated patterns need a closer read.",
        answer=(
            "Treat negated ignore patterns as manual review. The target flat "
            "config behavior depends on how the rest of the ignore list is "
            "supposed to interact."
        ),
        before_code=("dist/\n!dist/keep.js\n"),
        after_code=(
            "# manual review required\n"
            "# negated ignore patterns are outside the deterministic flat-config subset\n"
        ),
        symptoms=(
            "The repo already uses exceptions inside .eslintignore or ignorePatterns.",
            "A guessed migration can silently change which files are linted.",
            "Teams want a clean stop signal instead of a risky translation.",
        ),
        covers=(
            "Explicit unsupported ignore-pattern findings.",
            "Cross-links to the supported .eslintignore migration page.",
            "Repo-fit guidance before buying the flat-config pack.",
        ),
        manual_review=(
            "Rebuilding the intended include/exclude behavior in flat config.",
            "Ignore rules mixed with multiple config sources.",
            "Repos that already started a custom flat-config migration.",
        ),
        product_slug="flatconfig-lift",
    ),
    GuidePage(
        family="eslint",
        slug="multiple-legacy-configs",
        title="Why multiple legacy ESLint config sources block flat config migration",
        h1="Why multiple legacy ESLint config sources block flat config migration",
        description="If a repo has more than one legacy ESLint config source, the deterministic migration path should stop for manual review.",
        search_term="multiple ESLint config sources flat config migration",
        summary="One static config source is a fit. Multiple overlapping sources are not a clean automatic migration target.",
        answer=(
            "Keep multiple legacy ESLint config sources in manual review. The "
            "first job is deciding which source is authoritative before "
            "generating a flat config bridge."
        ),
        before_code=(".eslintrc.json\npackage.json#eslintConfig\n"),
        after_code=(
            "# manual review required\n"
            "# choose the authoritative legacy config source before migration\n"
        ),
        symptoms=(
            "The repo has both .eslintrc data and package.json eslintConfig.",
            "Teams want one pass that qualifies repo fit before generating anything.",
            "Reviewers need a clear reason why the flat-config pack stopped.",
        ),
        covers=(
            "Explicit multiple-config-sources findings.",
            "Cross-links to the supported .eslintrc and package.json pages.",
            "Repo-fit guidance before buying the flat-config pack.",
        ),
        manual_review=(
            "Choosing the real source of truth.",
            "Merging overlapping rules and ignores.",
            "Repos that also already have eslint.config.* files.",
        ),
        product_slug="flatconfig-lift",
    ),
    GuidePage(
        family="eslint",
        slug="existing-flat-config",
        title="What to do when eslint.config.* already exists",
        h1="What to do when eslint.config.* already exists",
        description="If the repo already has eslint.config.js, .cjs, or .mjs, the static legacy-config migration path should stop for manual review.",
        search_term="existing eslint.config flat config migration",
        summary="If the repo already has a flat config file, you are not starting from the simple bridge case anymore.",
        answer=(
            "Treat existing eslint.config.* files as manual review. The next step "
            "depends on whether the flat config is authoritative, partial, or "
            "mid-migration."
        ),
        before_code=("eslint.config.cjs\n.eslintrc.json\n"),
        after_code=(
            "# manual review required\n# repo already has a flat config file\n"
        ),
        symptoms=(
            "The repo already contains eslint.config.js, .cjs, or .mjs.",
            "The flat-config pack needs to stop before generating duplicate or conflicting output.",
            "Teams want fast repo qualification instead of accidental config churn.",
        ),
        covers=(
            "Explicit existing-flat-config findings.",
            "Cross-links to the supported static legacy-config pages.",
            "Repo-fit guidance before buying the flat-config pack.",
        ),
        manual_review=(
            "Deciding whether the existing flat config is authoritative.",
            "Cleaning up mixed legacy and flat-config states.",
            "Repos that also have JS-backed legacy configs.",
        ),
        product_slug="flatconfig-lift",
    ),
    # --- Additional SQLAlchemy pages ---
    GuidePage(
        family="sqlalchemy",
        slug="scalar-subquery",
        title="Replace Query.as_scalar() with scalar_subquery() in SQLAlchemy 2.0",
        h1="How to replace Query.as_scalar() with scalar_subquery() in SQLAlchemy 2.0",
        description="Migrate legacy Query.subquery().as_scalar() calls to the scalar_subquery() method.",
        search_term="as_scalar scalar_subquery sqlalchemy 2.0",
        summary="The as_scalar() method is gone. The replacement is scalar_subquery().",
        answer=(
            "Replace .subquery().as_scalar() or .as_scalar() with .scalar_subquery() on "
            "the select or query."
        ),
        before_code=(
            "subq = session.query(func.count(Order.id)).filter(\n"
            "    Order.user_id == User.id\n"
            ").as_scalar()\n"
        ),
        after_code=(
            "subq = (\n"
            "    select(func.count(Order.id))\n"
            "    .where(Order.user_id == User.id)\n"
            "    .scalar_subquery()\n"
            ")\n"
        ),
        symptoms=(
            "Legacy queries still use .as_scalar() for correlated subqueries.",
            "AttributeError on .as_scalar() after the 2.0 upgrade.",
            "Teams need the scalar subquery cleanup bundled with other Query fixes.",
        ),
        covers=(
            "Direct .as_scalar() to .scalar_subquery() rewrites.",
            "Reporting for where the legacy pattern still appears.",
            "Cross-links to the select syntax cleanup page.",
        ),
        manual_review=(
            "Complex correlated subqueries tied to broader query redesign.",
            "Cases where the subquery shape also needs correction.",
            "Files mixed with unsupported execution-path changes.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="text-wrapping",
        title="Wrap raw SQL in text() for SQLAlchemy 2.0",
        h1="How to wrap raw SQL strings in text() for SQLAlchemy 2.0",
        description="Raw SQL strings now need explicit text() wrapping in SQLAlchemy 2.0 execute calls.",
        search_term="text() raw sql sqlalchemy 2.0",
        summary="SQLAlchemy 2.0 no longer auto-coerces string SQL. Use text() explicitly.",
        answer=(
            "Wrap any raw SQL string passed to execute() in text() from sqlalchemy."
        ),
        before_code=(
            'result = conn.execute("SELECT * FROM users WHERE id = :id", {"id": 1})\n'
        ),
        after_code=(
            "from sqlalchemy import text\n\n"
            'result = conn.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 1})\n'
        ),
        symptoms=(
            "ArgumentError about expected executable but got string.",
            "Old helpers pass raw SQL to execute() calls.",
            "Teams want the easy text() wrapping handled automatically.",
        ),
        covers=(
            "Detection of raw string SQL passed to execute().",
            "text() import injection and wrapping.",
            "Report entries for where raw SQL still appears.",
        ),
        manual_review=(
            "Dynamic SQL construction that mixes strings and expressions.",
            "Helpers that reshape SQL arguments before execution.",
            "Files bundled with engine.execute() removal.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="session-execute-orm",
        title="Adapt session.execute() result handling in SQLAlchemy 2.0",
        h1="How to adapt session.execute() result handling in SQLAlchemy 2.0",
        description="Session.execute() in 2.0 returns Result objects, not lists. Use .scalars() or .all() for ORM rows.",
        search_term="session.execute result scalars sqlalchemy 2.0",
        summary="The result shape changed. Call .scalars().all() for ORM entity rows.",
        answer=(
            "Call .scalars() on the Result to get ORM entity rows, then .all() or iterate."
        ),
        before_code=(
            "users = session.execute(select(User)).fetchall()  # returns list of Row\n"
        ),
        after_code=(
            "users = session.execute(select(User)).scalars().all()  # returns list of User\n"
        ),
        symptoms=(
            "Code expects User objects but gets Row tuples.",
            "Iteration over result gives tuples instead of mapped instances.",
            "Teams need to update ORM result access patterns.",
        ),
        covers=(
            "Detection of legacy result-access patterns.",
            ".scalars() insertion for ORM entity queries.",
            "Cross-links to the select syntax cleanup page.",
        ),
        manual_review=(
            "Mixed column and entity queries that need custom unpacking.",
            "Result-shape changes tied to broader query redesign.",
            "Helpers that already wrap result processing.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="relationship-backref-to-back-populates",
        title="Replace backref with back_populates in SQLAlchemy 2.0",
        h1="How to replace backref strings with back_populates in SQLAlchemy 2.0",
        description="The string backref pattern still works but explicit back_populates is the modern approach.",
        search_term="backref back_populates sqlalchemy 2.0",
        summary="String backref is legacy. Explicit back_populates is cleaner for migration.",
        answer=(
            "Keep backref if it works, or convert to explicit back_populates on both sides "
            "when the migration also touches the relationship."
        ),
        before_code=(
            'class User(Base):\n    orders = relationship("Order", backref="user")\n'
        ),
        after_code=(
            "class User(Base):\n"
            '    orders = relationship("Order", back_populates="user")\n\n'
            "class Order(Base):\n"
            '    user = relationship("User", back_populates="orders")\n'
        ),
        symptoms=(
            "Reviewers prefer explicit back_populates over magic backref strings.",
            "Migration is already touching the relationship definition.",
            "Teams want both directions documented in code.",
        ),
        covers=(
            "Detection of string backref usage.",
            "Reporting for where backref still appears.",
            "Cross-links to the string loader cleanup pages.",
        ),
        manual_review=(
            "Complex relationship inheritance.",
            "backref() with custom arguments.",
            "Files where both sides are not easily accessible.",
        ),
        product_slug="sa20-pack",
    ),
    # --- Additional Pydantic pages ---
    GuidePage(
        family="pydantic",
        slug="extra-forbid",
        title="Replace Extra.forbid with extra='forbid' in Pydantic v2",
        h1="How to replace Extra.forbid with extra='forbid' in Pydantic v2",
        description="Migrate the Extra enum usage to string literal in model_config.",
        search_term="Extra.forbid pydantic v2",
        summary="The Extra enum is gone. Use string literals in model_config.",
        answer=(
            "Replace Extra.forbid (and Extra.allow, Extra.ignore) with the string literal "
            "'forbid', 'allow', or 'ignore' in model_config."
        ),
        before_code=(
            "from pydantic import BaseModel, Extra\n\n"
            "class Strict(BaseModel):\n"
            "    class Config:\n"
            "        extra = Extra.forbid\n"
        ),
        after_code=(
            "from pydantic import BaseModel, ConfigDict\n\n"
            "class Strict(BaseModel):\n"
            '    model_config = ConfigDict(extra="forbid")\n'
        ),
        symptoms=(
            "ImportError for Extra from pydantic.",
            "Models still reference Extra.forbid in nested Config.",
            "Teams want the Extra cleanup bundled with Config migration.",
        ),
        covers=(
            "Extra.forbid/allow/ignore to string literal rewrites.",
            "Nested Config to model_config conversion.",
            "Cross-links to the Config migration page.",
        ),
        manual_review=(
            "Dynamic extra config based on runtime logic.",
            "Files with other unsupported Config keys.",
            "Alias imports of Extra.",
        ),
        product_slug="pydantic-v2-porter",
    ),
    GuidePage(
        family="pydantic",
        slug="schema-extra-to-json-schema-extra",
        title="Replace schema_extra with json_schema_extra in Pydantic v2",
        h1="How to replace schema_extra with json_schema_extra in Pydantic v2",
        description="Migrate schema_extra in Config to json_schema_extra in model_config.",
        search_term="schema_extra json_schema_extra pydantic v2",
        summary="schema_extra was renamed to json_schema_extra in Pydantic v2.",
        answer=("Replace schema_extra with json_schema_extra in your model_config."),
        before_code=(
            "class User(BaseModel):\n"
            "    class Config:\n"
            '        schema_extra = {"examples": [{"name": "Alice"}]}\n'
        ),
        after_code=(
            "class User(BaseModel):\n"
            "    model_config = ConfigDict(\n"
            '        json_schema_extra={"examples": [{"name": "Alice"}]}\n'
            "    )\n"
        ),
        symptoms=(
            "Schema generation ignores the old schema_extra key.",
            "Config migration needs to rename this alongside other keys.",
            "Teams want all Config key renames handled consistently.",
        ),
        covers=(
            "schema_extra to json_schema_extra rename.",
            "Integration with Config to model_config migration.",
            "Reporting for where the old key appears.",
        ),
        manual_review=(
            "schema_extra as a callable that needs signature changes.",
            "Files with other unsupported Config keys.",
            "Dynamic schema_extra generation.",
        ),
        product_slug="pydantic-v2-porter",
    ),
    GuidePage(
        family="pydantic",
        slug="orm-mode-to-from-attributes",
        title="Replace orm_mode with from_attributes in Pydantic v2",
        h1="How to replace orm_mode=True with from_attributes=True in Pydantic v2",
        description="The orm_mode config key was renamed to from_attributes in Pydantic v2.",
        search_term="orm_mode from_attributes pydantic v2",
        summary="orm_mode is now from_attributes. This is a simple rename.",
        answer=("Replace orm_mode=True with from_attributes=True in model_config."),
        before_code=(
            "class UserOut(BaseModel):\n    class Config:\n        orm_mode = True\n"
        ),
        after_code=(
            "class UserOut(BaseModel):\n"
            "    model_config = ConfigDict(from_attributes=True)\n"
        ),
        symptoms=(
            "Validation error when constructing model from ORM object.",
            "Config still uses the legacy orm_mode key.",
            "Teams need this rename bundled with other Config cleanup.",
        ),
        covers=(
            "Direct orm_mode to from_attributes rename.",
            "Integration with full Config to model_config conversion.",
            "Cross-links to the allow_population_by_field_name rename.",
        ),
        manual_review=(
            "Files with other removed Config keys.",
            "Models that also need validator migration.",
            "Alias-heavy imports in the same file.",
        ),
        product_slug="pydantic-v2-porter",
    ),
    GuidePage(
        family="pydantic",
        slug="field-const-removed",
        title="Why Field(const=True) needs manual review in Pydantic v2",
        h1="Why Field(const=True) needs manual review in Pydantic v2",
        description="Field(const=True) was removed in Pydantic v2. Use Literal types instead.",
        search_term="Field const removed pydantic v2",
        summary="const=True is gone. The replacement depends on how the constant should behave.",
        answer=(
            "Replace Field(const=True, default=value) with a Literal type annotation. "
            "This changes the validation behavior."
        ),
        before_code=(
            "from pydantic import BaseModel, Field\n\n"
            "class Config(BaseModel):\n"
            '    version: str = Field(const=True, default="1.0")\n'
        ),
        after_code=(
            "from typing import Literal\n"
            "from pydantic import BaseModel\n\n"
            "class Config(BaseModel):\n"
            '    version: Literal["1.0"] = "1.0"\n'
        ),
        symptoms=(
            "TypeError about unexpected keyword const.",
            "Models need constant fields that reject other values.",
            "Teams want clear guidance on the Literal replacement.",
        ),
        covers=(
            "Detection and reporting of Field(const=True) usage.",
            "Guidance on the Literal type replacement.",
            "Cross-links to other Field parameter changes.",
        ),
        manual_review=(
            "Choosing the right Literal type for the constant.",
            "Fields where the const behavior interacts with validation.",
            "Files with other removed Field parameters.",
        ),
        product_slug="pydantic-v2-porter",
    ),
    # --- Additional ESLint pages ---
    GuidePage(
        family="eslint",
        slug="env-globals-flat-config",
        title="Migrate env and globals to flat config",
        h1="How to migrate env and globals settings to ESLint flat config",
        description="Move env and globals from legacy config into the flat config languageOptions object.",
        search_term="eslint env globals flat config",
        summary="env and globals move into languageOptions in flat config.",
        answer=(
            "Move env settings to languageOptions.globals using the globals package, "
            "and move globals directly into languageOptions.globals."
        ),
        before_code=(
            "{\n"
            '  "env": {"browser": true, "node": true},\n'
            '  "globals": {"myGlobal": "readonly"}\n'
            "}\n"
        ),
        after_code=(
            'const globals = require("globals");\n\n'
            "module.exports = [{\n"
            "  languageOptions: {\n"
            "    globals: {\n"
            "      ...globals.browser,\n"
            "      ...globals.node,\n"
            '      myGlobal: "readonly",\n'
            "    },\n"
            "  },\n"
            "}];\n"
        ),
        symptoms=(
            "Legacy config still uses env for browser/node globals.",
            "Custom globals need to move into the new structure.",
            "Teams want the env/globals migration handled with the config bridge.",
        ),
        covers=(
            "Static env configuration mapping to globals package imports.",
            "Custom globals migration to languageOptions.globals.",
            "Integration with FlatCompat bridge generation.",
        ),
        manual_review=(
            "Dynamic env selection based on file patterns.",
            "Overlapping globals from multiple sources.",
            "Repos with JS-backed legacy config logic.",
        ),
        product_slug="flatconfig-lift",
    ),
    GuidePage(
        family="eslint",
        slug="overrides-flat-config",
        title="Migrate overrides to flat config arrays",
        h1="How to migrate ESLint overrides to flat config arrays",
        description="Overrides in legacy config become separate array elements in flat config.",
        search_term="eslint overrides flat config",
        summary="Overrides become array elements with files patterns in flat config.",
        answer=(
            "Each override becomes a separate config object in the array with its own files pattern."
        ),
        before_code=(
            "{\n"
            '  "rules": {"no-console": "warn"},\n'
            '  "overrides": [{\n'
            '    "files": ["*.test.js"],\n'
            '    "rules": {"no-console": "off"}\n'
            "  }]\n"
            "}\n"
        ),
        after_code=(
            "module.exports = [\n"
            '  { rules: { "no-console": "warn" } },\n'
            "  {\n"
            '    files: ["**/*.test.js"],\n'
            '    rules: { "no-console": "off" },\n'
            "  },\n"
            "];\n"
        ),
        symptoms=(
            "Legacy config uses overrides for test files or specific directories.",
            "Teams need the override patterns preserved in flat config.",
            "FlatCompat can carry simple overrides through.",
        ),
        covers=(
            "Static override patterns in JSON/YAML configs.",
            "FlatCompat handling of simple overrides.",
            "Cross-links to the ignore pattern migration.",
        ),
        manual_review=(
            "Complex nested overrides with multiple extends.",
            "Overrides that depend on JS logic.",
            "Repos with multiple config sources.",
        ),
        product_slug="flatconfig-lift",
    ),
    GuidePage(
        family="eslint",
        slug="parser-options-flat-config",
        title="Migrate parserOptions to flat config",
        h1="How to migrate parserOptions to ESLint flat config",
        description="Move parserOptions into languageOptions.parserOptions in flat config.",
        search_term="eslint parserOptions flat config",
        summary="parserOptions moves into languageOptions in flat config.",
        answer=(
            "Move parserOptions settings like ecmaVersion and sourceType into languageOptions."
        ),
        before_code=(
            "{\n"
            '  "parserOptions": {\n'
            '    "ecmaVersion": 2022,\n'
            '    "sourceType": "module"\n'
            "  }\n"
            "}\n"
        ),
        after_code=(
            "module.exports = [{\n"
            "  languageOptions: {\n"
            "    ecmaVersion: 2022,\n"
            '    sourceType: "module",\n'
            "  },\n"
            "}];\n"
        ),
        symptoms=(
            "Legacy config sets ecmaVersion and sourceType in parserOptions.",
            "Teams need parser settings preserved in the flat config bridge.",
            "FlatCompat can carry these through automatically.",
        ),
        covers=(
            "Static parserOptions in JSON/YAML configs.",
            "ecmaVersion and sourceType migration.",
            "Integration with FlatCompat bridge generation.",
        ),
        manual_review=(
            "Custom parser configurations beyond standard options.",
            "TypeScript parser settings that need @typescript-eslint/parser.",
            "Repos with JS-backed parser logic.",
        ),
        product_slug="flatconfig-lift",
    ),
    # --- Error-message and decision pages for high-intent search ---
    GuidePage(
        family="sqlalchemy",
        slug="optionengine-execute-error",
        title="'OptionEngine' object has no attribute 'execute' in SQLAlchemy 2.0",
        h1="Fix 'OptionEngine' object has no attribute 'execute' in SQLAlchemy 2.0",
        description="Fix the common OptionEngine execute error by moving execution onto a Connection or Session.",
        search_term="'OptionEngine' object has no attribute 'execute'",
        summary="This error usually means code or a dependency still expects the removed Engine.execute path.",
        answer=(
            "Open an explicit connection, wrap raw SQL in text(...), and pass the "
            "Connection into code that still expects an executable object."
        ),
        before_code=(
            'rows = pd.read_sql_query("SELECT id FROM users", engine)\n'
            "result = engine.execution_options(stream_results=True).execute(stmt)\n"
        ),
        after_code=(
            "from sqlalchemy import text\n\n"
            "with engine.connect() as conn:\n"
            '    rows = pd.read_sql_query(text("SELECT id FROM users"), conn)\n'
            "    result = conn.execution_options(stream_results=True).execute(stmt)\n"
        ),
        symptoms=(
            "Pandas or helper code fails after upgrading SQLAlchemy.",
            "The stack trace mentions OptionEngine.execute.",
            "Execution options are chained from engine before execute(...).",
        ),
        covers=(
            "Detection of engine and OptionEngine execution paths.",
            "Manual-review reporting for execution-boundary changes.",
            "Links to the broader engine.execute removal guide.",
        ),
        manual_review=(
            "Transaction boundaries around writes.",
            "Third-party libraries that need version-compatible adapters.",
            "Raw SQL strings that should become text(...).",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="engine-attribute-error-execute",
        title="'Engine' object has no attribute 'execute' in SQLAlchemy 2.0",
        h1="Fix 'Engine' object has no attribute 'execute' in SQLAlchemy 2.0",
        description="Resolve Engine.execute attribute errors without guessing transaction behavior.",
        search_term="'Engine' object has no attribute 'execute'",
        summary="Engine.execute was removed, so the replacement depends on whether the code is reading, writing, or wrapping another library.",
        answer=(
            "Use engine.connect() or engine.begin(), then execute on the returned "
            "Connection. Do not blindly replace engine.execute with session.execute."
        ),
        before_code=(
            "result = engine.execute(stmt)\n"
            'engine.execute(user_table.insert(), {"name": "Ada"})\n'
        ),
        after_code=(
            "with engine.connect() as conn:\n"
            "    result = conn.execute(stmt)\n\n"
            "with engine.begin() as conn:\n"
            '    conn.execute(user_table.insert(), {"name": "Ada"})\n'
        ),
        symptoms=(
            "AttributeError appears immediately after the SQLAlchemy 2.0 bump.",
            "Legacy database helpers call engine.execute directly.",
            "Write paths relied on implicit autocommit behavior.",
        ),
        covers=(
            "Detection of removed engine.execute calls.",
            "Separation of read and write examples.",
            "Fail-closed reporting when transaction semantics are unclear.",
        ),
        manual_review=(
            "Choosing connect() versus begin().",
            "Implicit autocommit replacements.",
            "Helper APIs that hide the engine object.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="legacyapiwarning-query-get",
        title="Fix LegacyAPIWarning for Query.get() in SQLAlchemy 2.0",
        h1="Fix LegacyAPIWarning: Query.get() is legacy in SQLAlchemy 2.0",
        description="Replace Query.get warnings with Session.get in the safe primary-key lookup subset.",
        search_term="LegacyAPIWarning Query.get SQLAlchemy 2.0",
        summary="Query.get is a low-risk cleanup when the call is a direct primary-key lookup.",
        answer=(
            "Replace session.query(Model).get(primary_key) with "
            "session.get(Model, primary_key)."
        ),
        before_code="user = session.query(User).get(user_id)\n",
        after_code="user = session.get(User, user_id)\n",
        symptoms=(
            "Test output includes LegacyAPIWarning for Query.get().",
            "Many files still use session.query(Model).get(...).",
            "The migration has warning noise before real failures appear.",
        ),
        covers=(
            "Direct Query.get primary-key lookup rewrites.",
            "Warning cleanup that keeps result shape stable.",
            "Report entries for unsupported chained Query.get cases.",
        ),
        manual_review=(
            "Query chains before .get(...).",
            "Non-primary-key lookups.",
            "Custom query properties or session wrappers.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="select-legacy-mode-warning",
        title="Fix legacy select([..]) warnings in SQLAlchemy 2.0",
        h1="Fix SQLAlchemy legacy select([..]) warnings",
        description="Drop the old select list wrapper and use direct select(...) arguments.",
        search_term="SQLAlchemy select legacy mode warning",
        summary="select([..]) is syntax cleanup, not a business-logic migration.",
        answer="Pass entities or columns directly into select(...), without the wrapper list.",
        before_code="stmt = select([User.id, User.email])\n",
        after_code="stmt = select(User.id, User.email)\n",
        symptoms=(
            "Warnings mention legacy calling style for select().",
            "Old Core query builders still wrap columns in a list.",
            "The same simple edit appears across many files.",
        ),
        covers=(
            "Direct select([..]) to select(..) rewrites.",
            "Sitemap-linked explanation for warning cleanup.",
            "Cross-links to DML constructor cleanup pages.",
        ),
        manual_review=(
            "Dynamically assembled select arguments.",
            "Code generation templates.",
            "Files that mix select syntax with execution-boundary changes.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="joinedload-all-nameerror",
        title="Fix joinedload_all is not defined during SQLAlchemy migration",
        h1="Fix joinedload_all is not defined in SQLAlchemy 2.0",
        description="Replace joinedload_all usage with chained joinedload calls when the path is obvious.",
        search_term="joinedload_all is not defined SQLAlchemy 2.0",
        summary="joinedload_all was removed, but only the simple relationship paths are safe to rewrite mechanically.",
        answer=(
            "Use chained joinedload(...) calls with mapped attributes for clear paths. "
            "Stop for aliases, contains_eager, and duplicate join interactions."
        ),
        before_code='query = session.query(User).options(joinedload_all("orders.items"))\n',
        after_code=(
            "query = session.query(User).options(\n"
            "    joinedload(User.orders).joinedload(Order.items)\n"
            ")\n"
        ),
        symptoms=(
            "Importing joinedload_all fails after the upgrade.",
            "Loader options still use dotted string paths.",
            "The query also contains explicit joins or aliases.",
        ),
        covers=(
            "Simple joinedload_all detection and explanation.",
            "Safe-path examples for mapped attributes.",
            "Manual-review boundaries for query-shape-dependent loading.",
        ),
        manual_review=(
            "contains_eager usage.",
            "Aliased classes in the same query.",
            "Duplicate joins created by old helper functions.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="sqlalchemy-20-triage-checklist",
        title="SQLAlchemy 2.0 migration triage checklist",
        h1="SQLAlchemy 2.0 migration triage checklist",
        description="Sort SQLAlchemy 2.0 migration work into safe codemod, manual review, and staged refactor buckets.",
        search_term="SQLAlchemy 2.0 migration checklist",
        summary="A migration moves faster when the easy syntax cleanup is separated from transaction and query-shape decisions.",
        answer=(
            "Start with direct syntax cleanup, report execution-boundary changes, "
            "and leave broad Query-to-select rewrites for a deliberate stage."
        ),
        before_code=(
            "1. Warnings and removed imports\n"
            "2. Repetitive syntax cleanup\n"
            "3. Execution-boundary failures\n"
            "4. Query-shape refactors\n"
        ),
        after_code=(
            "codemod: Query.get, select([..]), simple string paths\n"
            "manual review: engine.execute, from_self, multi-hop joins\n"
            "later stage: broad Query-to-select redesign\n"
        ),
        symptoms=(
            "The repo has many different SQLAlchemy warnings at once.",
            "Developers are mixing easy syntax edits with risky behavior changes.",
            "Managers need a staging plan before approving migration time.",
        ),
        covers=(
            "A practical order for migration cleanup.",
            "Which pages map to each decision bucket.",
            "A scanner-first way to qualify product fit.",
        ),
        manual_review=(
            "Application-specific transaction rules.",
            "Result-shape changes from ORM query rewrites.",
            "Migrations that require domain knowledge.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="sqlalchemy",
        slug="sqlalchemy-manual-vs-codemod",
        title="Manual SQLAlchemy migration vs codemod",
        h1="Manual SQLAlchemy 2.0 migration vs codemod",
        description="Decide when a SQLAlchemy 2.0 migration should use a deterministic codemod and when it should stay manual.",
        search_term="SQLAlchemy 2.0 codemod vs manual migration",
        summary="Codemods are valuable for repetitive syntax cleanup. They are risky when the right answer depends on runtime behavior.",
        answer=(
            "Use a codemod for direct, syntax-aware changes. Keep transaction "
            "boundaries, alias-heavy loaders, and broad query redesign in manual review."
        ),
        before_code=(
            "manual only:\n"
            "    rewrite every query shape by hand\n"
            "codemod only:\n"
            "    guess through engine.execute and aliases\n"
        ),
        after_code=(
            "hybrid:\n"
            "    automate direct syntax cleanup\n"
            "    report ambiguous files\n"
            "    validate before claiming success\n"
        ),
        symptoms=(
            "The team is unsure whether automation is safe.",
            "A full manual migration looks too expensive.",
            "A blanket AI refactor feels too risky for database code.",
        ),
        covers=(
            "A decision framework for codemod fit.",
            "Examples of safe and blocked buckets.",
            "Product positioning without broad migration promises.",
        ),
        manual_review=(
            "Business logic hidden in query construction.",
            "Runtime-only behavior changes.",
            "Validation failures after automated cleanup.",
        ),
        product_slug="sa20-pack",
    ),
    GuidePage(
        family="pydantic",
        slug="basesettings-import-error",
        title="Fix BaseSettings import errors in Pydantic v2",
        h1="Fix BaseSettings import errors in Pydantic v2",
        description="Move BaseSettings imports to pydantic-settings when upgrading to Pydantic v2.",
        search_term="BaseSettings import error pydantic v2",
        summary="BaseSettings moved out of pydantic and into the pydantic-settings package.",
        answer="Import BaseSettings from pydantic_settings instead of pydantic.",
        before_code="from pydantic import BaseSettings\n",
        after_code="from pydantic_settings import BaseSettings\n",
        symptoms=(
            "ImportError or PydanticImportError mentions BaseSettings.",
            "Settings models still import directly from pydantic.",
            "The repo has mostly straightforward settings classes.",
        ),
        covers=(
            "Direct BaseSettings import rewrites.",
            "Direct pydantic.v1 BaseSettings import cleanup.",
            "Reporting when alias imports hide the symbol.",
        ),
        manual_review=(
            "Dynamic imports.",
            "Alias-heavy settings modules.",
            "Settings behavior that changed alongside validators.",
        ),
        product_slug="pydantic-v2-porter",
    ),
    GuidePage(
        family="pydantic",
        slug="validator-deprecation-warning",
        title="Fix Pydantic v2 @validator deprecation warnings",
        h1="Fix Pydantic v2 @validator deprecation warnings",
        description="Replace simple @validator usage with @field_validator in the safe Pydantic v2 subset.",
        search_term="PydanticDeprecatedSince20 validator field_validator",
        summary="Simple validators are safe cleanup; signature-heavy validators need review.",
        answer=(
            "Use @field_validator for simple field validators, but stop when the "
            "validator depends on values, field, config, each_item, or always."
        ),
        before_code=(
            "from pydantic import BaseModel, validator\n\n"
            "class User(BaseModel):\n"
            '    @validator("email")\n'
            "    def clean_email(cls, value):\n"
            "        return value.lower()\n"
        ),
        after_code=(
            "from pydantic import BaseModel, field_validator\n\n"
            "class User(BaseModel):\n"
            '    @field_validator("email")\n'
            "    @classmethod\n"
            "    def clean_email(cls, value):\n"
            "        return value.lower()\n"
        ),
        symptoms=(
            "Test output includes PydanticDeprecatedSince20 warnings.",
            "Validators are simple field-level cleanup functions.",
            "Some validators have extra signature arguments.",
        ),
        covers=(
            "Simple @validator to @field_validator rewrites.",
            "Import cleanup for field_validator.",
            "Manual-review findings for signature-heavy cases.",
        ),
        manual_review=(
            "values, field, or config parameters.",
            "each_item=True or always=True behavior.",
            "Validators that change model-level semantics.",
        ),
        product_slug="pydantic-v2-porter",
    ),
    GuidePage(
        family="pydantic",
        slug="config-class-deprecated-warning",
        title="Fix Pydantic v2 class Config deprecation warnings",
        h1="Fix Pydantic v2 class Config deprecation warnings",
        description="Convert safe class Config blocks into model_config with ConfigDict.",
        search_term="PydanticDeprecatedSince20 class Config model_config",
        summary="A nested class Config can become model_config when every key is in the supported rename subset.",
        answer=(
            "Use ConfigDict and model_config for supported keys like extra, "
            "from_attributes, populate_by_name, and json_schema_extra."
        ),
        before_code=(
            "class User(BaseModel):\n"
            "    class Config:\n"
            "        orm_mode = True\n"
            "        allow_population_by_field_name = True\n"
        ),
        after_code=(
            "from pydantic import ConfigDict\n\n"
            "class User(BaseModel):\n"
            "    model_config = ConfigDict(\n"
            "        from_attributes=True,\n"
            "        populate_by_name=True,\n"
            "    )\n"
        ),
        symptoms=(
            "Warnings mention class-based Config being deprecated.",
            "Models use old config keys that were renamed.",
            "Some Config blocks contain removed keys.",
        ),
        covers=(
            "Safe Config to model_config conversion.",
            "Supported key renames.",
            "Manual-review findings for removed Config keys.",
        ),
        manual_review=(
            "Config.fields and other removed keys.",
            "Dynamic Config attributes.",
            "Config behavior coupled to custom validators.",
        ),
        product_slug="pydantic-v2-porter",
    ),
)


PRODUCTS: tuple[ProductPage, ...] = (
    ProductPage(
        slug="actions-upgrade-guard",
        name="GitHub Actions Upgrade Guard",
        family="GitHub Actions deadline-readiness",
        description="Local scanner for GitHub Actions workflow deprecations, runner drift, permissions risk, and manual migration guidance.",
        summary="Use Action Guard when workflow deadlines or platform changes are likely to break CI and you need a local report, source-linked manual alternatives, and fail-closed findings.",
        who_it_is_for=(
            "Platform engineers responsible for keeping many GitHub Actions workflows current.",
            "DevOps leads cleaning up artifact, cache, runner, Node runtime, and permission risks before they block releases.",
            "Repo owners who need a manager-readable Actions risk report without giving a hosted service repository access.",
        ),
        proof_points=(
            "Public proof shows legacy artifact and cache references with explicit manual review and no automatic edits.",
            "Runner, Node runtime, permission, local-action, and invalid-YAML cases stay visible as findings instead of guessed fixes.",
            "The scanner runs locally with no GitHub token, source upload, or automatic workflow edits.",
        ),
        not_for=(
            "Teams looking for hosted monitoring or automatic GitHub account access.",
            "Generated workflows where the generated YAML is not checked into the repo.",
            "Security hardening beyond the documented workflow-upgrade rules.",
        ),
        guide_slugs=(),
        docs=(("README", ACTION_GUARD_README_PATH),),
        price="",  # Paid SKU intentionally paused until proof demand is visible.
    ),
    ProductPage(
        slug="fit-report",
        name=FIT_REPORT_NAME,
        family="SQLAlchemy or Pydantic scanner output",
        description="Local software add-on that turns SQLAlchemy or Pydantic scanner output into an autonomous buy/do-not-buy migration fit summary.",
        summary="Use the fit report when the scan output is promising but ambiguous and you want a local recommendation before buying a cleanup pack.",
        who_it_is_for=(
            "Teams with SQLAlchemy or Pydantic scanner output but no clear buy/no-buy decision yet.",
            "Buyers who need a manager-readable fit summary without uploading source code.",
            "Repos where supported and manual-review findings are mixed enough to justify a second local check.",
        ),
        proof_points=(
            "Reads scanner output locally instead of requiring private repo upload.",
            "Separates supported findings from manual-review risk before a larger purchase.",
            "Produces a software-generated recommendation without human service delivery.",
        ),
        not_for=(
            "Repos that have not run the SQLAlchemy or Pydantic scanner yet.",
            "Teams that already know they need the full cleanup pack.",
            "ESLint proof-only scans; this add-on is scoped to SQLAlchemy and Pydantic output.",
        ),
        guide_slugs=(),
        docs=(
            ("Pricing", "docs/pricing.md"),
            ("Store products", "docs/store-products.md"),
            ("Fulfillment", "docs/fulfillment.md"),
        ),
        price="99",
        checkout_path=FIT_REPORT_ROUTE,
    ),
    ProductPage(
        slug="sa20-pack",
        name="SQLAlchemy 1.4 to 2.0 Migration Cleanup Pack",
        family="SQLAlchemy 1.4 -> 2.0",
        description="Deterministic local workflow for finding and cleaning up repeated SQLAlchemy 1.4 to 2.0 migration patterns.",
        summary="Start with the free scan, inspect the report, and only move to the cleanup pack if the repo has repeated supported patterns that are still expensive to fix by hand.",
        who_it_is_for=(
            "Teams still cleaning up SQLAlchemy 1.4 legacy query patterns.",
            "Repos that still contain Query.get(...), select([..]), string joins, or string loader paths.",
            "Engineering managers who need a narrow, honest migration tool.",
        ),
        proof_points=(
            "Public proof shows supported rewrites on real public files.",
            "Fail-closed proof shows engine.execute(...) stays blocked instead of guessed.",
            "The public repo remains scanner-first so a buyer can qualify fit before purchase.",
        ),
        not_for=(
            "Repos whose real pain is broad Query-to-select rewriting.",
            "Teams that want a full custom migration service.",
            "Any workflow that expects engine.execute(...) to be auto-fixed everywhere.",
        ),
        guide_slugs=(
            "session-query-get",
            "session-query-migration",
            "engine-execute-removed",
            "joinedload-all-removed",
            "select-list-syntax",
            "string-join-paths",
            "string-loader-options",
            "declarative-imports",
            "insert-values-kwargs",
            "update-values-kwargs",
            "delete-whereclause",
            "from-self-removed",
            "multi-hop-string-joins",
            "scalar-subquery",
            "text-wrapping",
            "session-execute-orm",
            "relationship-backref-to-back-populates",
            "optionengine-execute-error",
            "engine-attribute-error-execute",
            "legacyapiwarning-query-get",
            "select-legacy-mode-warning",
            "joinedload-all-nameerror",
            "sqlalchemy-20-triage-checklist",
            "sqlalchemy-manual-vs-codemod",
        ),
        docs=(
            ("Public proof", "docs/public-proof.md"),
            ("Commercial case", "docs/commercial-case.md"),
            ("Pricing", "docs/pricing.md"),
        ),
        price="299.99",
        checkout_path="/go/sa20-pack",
    ),
    ProductPage(
        slug="pydantic-v2-porter",
        name="Pydantic v1 to v2 Migration Cleanup Pack",
        family="Pydantic v1 -> v2",
        description="Deterministic local cleanup pack for supported Pydantic v1 to v2 imports, validators, config, and BaseSettings moves.",
        summary="The cleanup pack is strongest when the repo still uses direct pydantic imports and a clean validator/settings/config subset.",
        who_it_is_for=(
            "Teams upgrading direct pydantic imports to v2.",
            "Repos dominated by BaseSettings, safe Config, and simple validator cleanup.",
            "Buyers who want deterministic fit assessment before running a paid migration pack.",
        ),
        proof_points=(
            "Public proof covers supported validator and settings rewrites on real public repos.",
            "Manual-review findings stay explicit for values-heavy validators.",
            "The paid path stays software-only, with no human coding dependency.",
        ),
        not_for=(
            "Repos that rely on alias-heavy imports or import pydantic attribute access.",
            "Validator-heavy code that depends on values, field, config, each_item, or always.",
            "Teams that want a promise of full repo-wide v1 to v2 migration coverage.",
        ),
        guide_slugs=(
            "validator-to-field-validator",
            "basesettings-moved",
            "config-to-model-config",
            "validate-arguments",
            "root-validator-pre",
            "root-validator-post",
            "pydantic-v1-imports",
            "config-fields-removed",
            "validator-each-item",
            "validate-arguments-configured",
            "extra-forbid",
            "schema-extra-to-json-schema-extra",
            "orm-mode-to-from-attributes",
            "field-const-removed",
            "basesettings-import-error",
            "validator-deprecation-warning",
            "config-class-deprecated-warning",
        ),
        docs=(
            ("Public proof", "products/pydantic-v2-porter/docs/public-proof.md"),
            ("Commercial case", "products/pydantic-v2-porter/docs/commercial-case.md"),
            ("Dedicated scanner repo", PYDANTIC_REPO_URL),
        ),
        price="249.99",
        checkout_path="/go/pydantic-v2-porter",
    ),
    ProductPage(
        slug="sa20-preset",
        name=SA20_PRESET_NAME,
        family="SQLAlchemy rollout documentation",
        description="Downloadable rollout checklist, manager summary template, triage presets, review buckets, and handoff notes for SQLAlchemy migration cleanup.",
        summary="Use the preset bundle when the team needs rollout structure and manager-ready migration notes, not code rewrites.",
        who_it_is_for=(
            "Teams that already have scanner output and need a repeatable rollout plan.",
            "Engineering leads who need manager-ready status language and review buckets.",
            "Buyers who want documentation and handoff structure without a consulting engagement.",
        ),
        proof_points=(
            "Shows the exact deliverable shape: rollout checklist, manager summary, triage presets, review buckets, and handoff notes.",
            "Keeps the boundary clear: downloadable docs and presets, not a code rewrite engine.",
            "Uses the same Stripe Checkout and verified ZIP delivery path as the paid packs.",
        ),
        not_for=(
            "Teams that need deterministic code rewrites; use the SQLAlchemy cleanup pack instead.",
            "Repos that have not run the free SQLAlchemy scan yet.",
            "Buyers expecting human migration planning or private code review.",
        ),
        guide_slugs=(
            "sqlalchemy-20-triage-checklist",
            "sqlalchemy-manual-vs-codemod",
            "session-query-migration",
        ),
        docs=(
            ("Pricing", "docs/pricing.md"),
            ("Store products", "docs/store-products.md"),
            ("Fulfillment", "docs/fulfillment.md"),
        ),
        price=SA20_PRESET_PRICE,
        checkout_path=SA20_PRESET_CHECKOUT_PATH,
    ),
    ProductPage(
        slug="flatconfig-lift",
        name="ESLint Flat Config Migration Cleanup Pack",
        family="ESLint legacy config -> flat config",
        description="Static-config migration cleanup pack for deterministic .eslintrc and package.json eslintConfig conversion into flat config.",
        summary="This product exists for the static-config subset. It does not pretend to evaluate JS config logic.",
        who_it_is_for=(
            "Teams migrating static .eslintrc JSON or YAML configs.",
            "Repos that still store eslintConfig inside package.json.",
            "Buyers who want a generated FlatCompat bridge instead of a hand-made first pass.",
        ),
        proof_points=(
            "Public proof covers static JSON and YAML configs from real public repos.",
            "JS configs and existing flat config files are blocked instead of guessed through.",
            "The bridge output stays close to the source config with machine-generated reporting.",
        ),
        not_for=(
            "Repos built around .eslintrc.js, .cjs, or .mjs logic.",
            "Repos that already migrated to eslint.config.*.",
            "Teams that want the tool to understand arbitrary plugin ecosystem behavior.",
        ),
        guide_slugs=(
            "eslintrc-to-flat-config",
            "package-json-eslintconfig",
            "eslintrc-js-unsupported",
            "eslintignore-migration",
            "negated-ignore-patterns",
            "multiple-legacy-configs",
            "existing-flat-config",
            "env-globals-flat-config",
            "overrides-flat-config",
            "parser-options-flat-config",
        ),
        docs=(
            ("Public proof", "products/flatconfig-lift/docs/public-proof.md"),
            ("Commercial case", "products/flatconfig-lift/docs/commercial-case.md"),
            ("README", "products/flatconfig-lift/README.md"),
        ),
        price="",  # Not yet listed in Stripe checkout
    ),
)
