import {
  checkoutSale,
  saleIsActive,
  commerce,
  productByKey,
  productTrackingUrl,
} from "./product_catalog.mjs";

(function () {
  const config = window.SA20_SITE_CONFIG || {};
  const placeholderPattern =
    /REPLACE_|YOUR_|example\.com|CHANGE_ME|PUBLIC_REPO_URL/;
  const productUrlKeys = {
    freeScan: "freeStartUrl",
    actionGuard: "actionGuardFreeScanUrl",
    sa20: "paidPackUrl",
    sa20Preset: "presetBundleUrl",
    pydantic: "pydanticPackUrl",
    fitReport: "fitReportUrl",
  };

  function isPlaceholder(value) {
    return !value || placeholderPattern.test(value);
  }

  function productFor(key) {
    const product = productByKey(key);
    if (!product) {
      return null;
    }

    const overrides = config.products || {};
    return {
      ...product,
      ...(overrides[product.key] || {}),
      ...(overrides[product.slug] || {}),
    };
  }

  function setHref(selector, value, fallbackText) {
    document.querySelectorAll(selector).forEach((element) => {
      if (!(element instanceof HTMLAnchorElement)) {
        return;
      }

      if (isPlaceholder(value)) {
        element.href = "#";
        element.classList.add("disabled");
        if (fallbackText) {
          element.textContent = fallbackText;
        }
        return;
      }

      const currentHref = element.getAttribute("href") || "";
      if (value.startsWith("/go/") && currentHref.startsWith(`${value}/`)) {
        element.href = currentHref;
        return;
      }

      element.href = value;
    });
  }

  function blobUrl(path) {
    if (isPlaceholder(config.repoUrl)) {
      return "#";
    }

    const trimmed = config.repoUrl.replace(/\/$/, "");
    return `${trimmed}/blob/main/${path}`;
  }

  function productUrl(product) {
    const configured = config[productUrlKeys[product.key]];
    if (!isPlaceholder(configured)) {
      return configured;
    }
    if (product.key === "freeScan") {
      return blobUrl("docs/quickstart.md");
    }
    return product.checkoutUrl || product.links?.[0]?.href || "#";
  }

  function applySaleBanner() {
    const existing = document.querySelector("[data-sale-banner]");
    if (!saleIsActive()) {
      existing?.remove();
      return;
    }
    if (existing) {
      return;
    }

    const warning = document.getElementById("launch-warning");
    const banner = document.createElement("section");
    banner.className = "sale-banner";
    banner.dataset.saleBanner = "";
    banner.dataset.saleEnds = checkoutSale.endsLabel || "";
    banner.innerHTML = `
      <div>
        <p class="kicker">${checkoutSale.badge} for three weeks</p>
        <strong>${checkoutSale.name}</strong>
        <span>${checkoutSale.note}</span>
      </div>
      <a class="button secondary" href="/pricing">See sale pricing</a>
    `;
    if (warning?.parentElement) {
      warning.insertAdjacentElement("afterend", banner);
    }
  }

  function trackedProductUrl(product, source) {
    return productTrackingUrl({ ...product, checkoutUrl: productUrl(product) }, source);
  }

  function setProductHref(selector, key, fallbackText) {
    const product = productFor(key);
    if (!product) {
      return;
    }
    setHref(selector, productUrl(product), fallbackText);
  }

  function applyDocLinks() {
    document.querySelectorAll("[data-doc-path]").forEach((element) => {
      if (!(element instanceof HTMLAnchorElement)) {
        return;
      }

      const docPath = element.getAttribute("data-doc-path");
      if (!docPath) {
        return;
      }

      const target = blobUrl(docPath);
      if (target === "#") {
        element.href = "#";
        element.classList.add("disabled");
      } else {
        element.href = target;
      }
    });
  }

  function applyText(selector, value, fallback) {
    document.querySelectorAll(selector).forEach((element) => {
      element.textContent = isPlaceholder(value) ? fallback : value;
    });
  }

  function contactEmail() {
    return isPlaceholder(config.contactEmail)
      ? commerce.supportEmail
      : config.contactEmail;
  }

  function applyContactLinks() {
    document.querySelectorAll("[data-contact-link]").forEach((element) => {
      if (!(element instanceof HTMLAnchorElement)) {
        return;
      }

      if (element.getAttribute("href") && element.getAttribute("href") !== "#") {
        return;
      }

      const email = contactEmail();
      if (isPlaceholder(email)) {
        element.href = "#";
        element.classList.add("disabled");
      } else {
        element.href = `mailto:${email}`;
      }
    });
  }

  function showWarning(missingKeys) {
    const warning = document.getElementById("launch-warning");
    if (!warning || missingKeys.length === 0) {
      return;
    }

    warning.style.display = "block";
    warning.innerHTML =
      `<strong>Site configuration is incomplete.</strong> Update <code>site/config.js</code> for these required public values: ` +
      missingKeys.join(", ");
  }

  function loadCloudflareAnalytics() {
    if (isPlaceholder(config.cloudflareAnalyticsToken)) {
      return;
    }

    const script = document.createElement("script");
    script.src = "https://static.cloudflareinsights.com/beacon.min.js";
    script.defer = true;
    script.setAttribute(
      "data-cf-beacon",
      JSON.stringify({ token: config.cloudflareAnalyticsToken }),
    );
    document.head.appendChild(script);
  }

  function appendList(parent, items) {
    if (!items || items.length === 0) {
      return;
    }
    const list = document.createElement("ul");
    list.className = "clean";
    items.forEach((item) => {
      const row = document.createElement("li");
      row.textContent = item;
      list.appendChild(row);
    });
    parent.appendChild(list);
  }

  function createProductCta(product, source, label, secondary = true) {
    const link = document.createElement("a");
    link.className = secondary ? "button secondary" : "button";
    link.href = trackedProductUrl(product, source);
    link.textContent = label || product.ctaLabel;
    return link;
  }

  function appendSmallLinks(parent, links) {
    if (!links || links.length === 0) {
      return;
    }
    const wrapper = document.createElement("div");
    wrapper.className = "small-links";
    links.forEach((item) => {
      const link = document.createElement("a");
      link.href = item.href;
      link.textContent = item.label;
      wrapper.appendChild(link);
    });
    parent.appendChild(wrapper);
  }

  function createProductCard(product, source) {
    const card = document.createElement("section");
    card.className = "offer";

    const label = document.createElement("p");
    label.className = "offer-label";
    label.textContent = product.offerLabel || product.price || product.status;
    card.appendChild(label);

    const heading = document.createElement("h3");
    const primaryLink = product.links?.[0]?.href;
    if (primaryLink) {
      const link = document.createElement("a");
      link.href = primaryLink;
      link.textContent = product.cardTitle || product.shortName || product.name;
      heading.appendChild(link);
    } else {
      heading.textContent = product.cardTitle || product.shortName || product.name;
    }
    card.appendChild(heading);

    const copy = document.createElement("p");
    copy.textContent = product.cardDescription || product.description;
    card.appendChild(copy);

    card.appendChild(
      createProductCta(
        product,
        source,
        product.ctaLabelWithPrice || product.ctaLabel,
        product.key !== "freeScan",
      ),
    );
    if (product.checkoutProvider === commerce.checkoutProvider) {
      const note = document.createElement("p");
      note.className = "small";
      note.textContent = commerce.secureCheckoutNote;
      card.appendChild(note);
    }
    appendSmallLinks(card, product.links);
    return card;
  }

  function renderProductCards() {
    document.querySelectorAll("[data-product-cards]").forEach((container) => {
      // Preserve any static fallback content already present in the markup so
      // the page still sells the products when JavaScript is disabled or
      // delayed. Only fill empty containers with JS-rendered cards.
      if (container.firstElementChild) {
        return;
      }
      const keys = (container.getAttribute("data-product-cards") || "")
        .split(",")
        .map((key) => key.trim())
        .filter(Boolean);
      const source = container.getAttribute("data-product-source") || "";
      const cards = keys
        .map((key) => productFor(key))
        .filter(Boolean)
        .map((product) => createProductCard(product, source));
      container.replaceChildren(...cards);
    });
  }

  function createPricingPanel(product, source) {
    const panel = document.createElement("section");
    panel.className = "page-panel";
    if (product.pricingId) {
      panel.id = product.pricingId;
    }

    const label = document.createElement("p");
    label.className = "offer-label";
    label.textContent = product.offerLabel || product.price;
    panel.appendChild(label);

    const heading = document.createElement("h2");
    heading.textContent = product.name;
    panel.appendChild(heading);

    const price = document.createElement("p");
    price.textContent =
      product.key === "freeScan"
        ? "Price: "
        : saleIsActive()
          ? "Sale price: "
          : "Current checkout price: ";
    const pill = document.createElement("span");
    pill.className = "pill";
    pill.textContent = product.priceDetail || product.price;
    price.appendChild(pill);
    panel.appendChild(price);

    appendList(panel, product.bullets);

    if (product.pricingNote) {
      const note = document.createElement("p");
      note.className = "small";
      note.textContent = product.pricingNote;
      panel.appendChild(note);
    }

    appendList(panel, product.assurances);

    const actions = document.createElement("div");
    actions.className = "page-actions";
    actions.appendChild(
      createProductCta(
        product,
        source,
        product.ctaLabel,
        product.key !== "freeScan",
      ),
    );
    panel.appendChild(actions);
    appendSmallLinks(panel, product.links);
    return panel;
  }

  function renderPricingPanels() {
    document.querySelectorAll("[data-product-pricing-list]").forEach((container) => {
      // Preserve static fallback panels rendered into the HTML so /pricing
      // sells the products even with JS disabled or before app.js loads.
      if (container.firstElementChild) {
        return;
      }
      const keys = (container.getAttribute("data-product-pricing-list") || "")
        .split(",")
        .map((key) => key.trim())
        .filter(Boolean);
      const source = container.getAttribute("data-product-source") || "pricing";
      const panels = keys
        .map((key) => productFor(key))
        .filter(Boolean)
        .map((product) => createPricingPanel(product, source));
      container.replaceChildren(...panels);
    });
  }

  function renderPricingRows() {
    document.querySelectorAll("[data-product-pricing-rows]").forEach((body) => {
      // Preserve static <tr> fallback rows when present.
      if (body.firstElementChild) {
        return;
      }
      const keys = (body.getAttribute("data-product-pricing-rows") || "")
        .split(",")
        .map((key) => key.trim())
        .filter(Boolean);
      const rows = keys.map((key) => {
        const product = productFor(key);
        const row = document.createElement("tr");
        if (!product) {
          return row;
        }
        [product.buyerQuestion, product.offerName, product.stage].forEach(
          (value) => {
            const cell = document.createElement("td");
            cell.textContent = value;
            row.appendChild(cell);
          },
        );
        return row;
      });
      body.replaceChildren(...rows);
    });
  }

  function applyProductCtas() {
    document.querySelectorAll("[data-product-cta]").forEach((element) => {
      if (!(element instanceof HTMLAnchorElement)) {
        return;
      }
      const product = productFor(element.getAttribute("data-product-cta"));
      if (!product) {
        return;
      }
      const source = element.getAttribute("data-product-source") || "";
      const labelField = element.getAttribute("data-product-label");
      element.href = trackedProductUrl(product, source);
      element.textContent =
        (labelField && product[labelField]) || product.ctaLabel;
    });
  }

  function applyProductText() {
    document.querySelectorAll("[data-product-text]").forEach((element) => {
      const [key, field] = (element.getAttribute("data-product-text") || "").split(
        ".",
      );
      const product = productFor(key);
      if (!product || !field || product[field] === undefined) {
        return;
      }
      element.textContent = product[field];
    });
    document.querySelectorAll("[data-commerce-text]").forEach((element) => {
      const field = element.getAttribute("data-commerce-text");
      if (!field || commerce[field] === undefined) {
        return;
      }
      element.textContent = commerce[field];
    });
  }

  function applyCancelTitle() {
    if (window.location.pathname.replace(/\/$/, "") !== "/cancel") {
      return;
    }
    const productSlug = new URLSearchParams(window.location.search).get("product");
    const labels = {
      "fit-report": "Fit Report",
      "sa20-pack": "SQLAlchemy Cleanup Pack",
      "sa20-preset": "Migration Preset Bundle",
      "pydantic-v2-porter": "Pydantic Cleanup Pack",
    };
    document.title = `Checkout canceled | ${labels[productSlug] || "Zipper Tools"}`;
  }

  const missing = [];
  ["sellerName", "contactEmail", "repoUrl"].forEach((key) => {
    if (isPlaceholder(config[key])) {
      missing.push(key);
    }
  });

  setHref("[data-repo-link]", config.repoUrl, "Add public repo URL");
  setProductHref("[data-free-link]", "freeScan", "Add repo or quickstart URL");
  setProductHref("[data-pack-link]", "sa20", "Checkout coming soon");
  setProductHref("[data-bundle-link]", "sa20Preset", "Preset bundle coming soon");
  setProductHref("[data-pydantic-link]", "pydantic", "Pydantic pack coming soon");
  setProductHref("[data-fit-report-link]", "fitReport", "Fit report coming soon");

  applyText("[data-seller-name]", config.sellerName, "the seller");
  applyText("[data-contact-email]", contactEmail(), "contact email");
  applyProductText();
  applyCancelTitle();
  applySaleBanner();
  applyProductCtas();
  renderPricingRows();
  renderProductCards();
  renderPricingPanels();
  applyDocLinks();
  applyContactLinks();
  showWarning(missing);
  loadCloudflareAnalytics();
})();
