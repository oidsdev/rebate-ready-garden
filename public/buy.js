const CATALOG_URL = "/products.json";
const MARKETS_URL = "/markets.json";
let catalog = [];
let editionLabels = {};

async function loadCatalog() {
  const [cr, mr] = await Promise.all([fetch(CATALOG_URL), fetch(MARKETS_URL)]);
  catalog = await cr.json();
  const markets = await mr.json();
  for (const m of markets) {
    for (const e of m.editions || []) editionLabels[e.id] = e.label;
  }
  document.querySelectorAll("[data-edition]").forEach((el) => {
    renderGrid(el, el.dataset.edition);
  });
}

function editionLabel(p) {
  return editionLabels[p.edition] || p.edition;
}

function renderGrid(el, edition) {
  const items = catalog.filter((p) => p.edition === edition || (edition === "all" && true));
  el.innerHTML = items
    .map((p) => {
      if (p.status !== "live") {
        return `
    <div class="card coming-soon">
      <div class="sku">${editionLabel(p)}</div>
      <h3>${p.name}</h3>
      <div class="price">${p.price}</div>
      <p style="font-size:14px">${p.blurb}</p>
      <ul>${p.includes.map((i) => `<li>${i}</li>`).join("")}</ul>
      <button class="btn" disabled style="opacity:.55;cursor:default">Coming soon</button>
      <p class="buy-fine">Not on sale yet. We are building this edition now.</p>
    </div>`;
      }
      return `
    <div class="card">
      <div class="sku">${editionLabel(p)}</div>
      <h3>${p.name}</h3>
      <div class="price">${p.price}</div>
      <p style="font-size:14px">${p.blurb}</p>
      <ul>${p.includes.map((i) => `<li>${i}</li>`).join("")}</ul>
      <input type="email" placeholder="Email for your download link" data-email="${p.sku}" aria-label="Email for download link">
      <button class="btn" data-buy="${p.sku}">Buy ${p.price}</button>
      <p class="buy-fine">Digital download. <a href="/terms.html#refunds">Refund policy</a> &middot; <a href="/terms.html">Terms of Sale</a>. Rebate approval is the county's decision.</p>
      <div class="buy-msg" data-msg="${p.sku}"></div>
    </div>`;
    })
    .join("");
  el.querySelectorAll("[data-buy]").forEach((b) =>
    b.addEventListener("click", () => buy(b.dataset.buy))
  );
}

async function buy(sku) {
  const emailEl = document.querySelector(`[data-email="${sku}"]`);
  const msgEl = document.querySelector(`[data-msg="${sku}"]`);
  const email = (emailEl.value || "").trim();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    msgEl.textContent = "Enter a valid email. Your download link goes there.";
    return;
  }
  msgEl.textContent = "Starting secure checkout…";
  try {
    const r = await fetch("/api/checkout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sku, email }),
    });
    const d = await r.json();
    if (!r.ok) {
      msgEl.textContent = d.message || "Checkout is not available yet. Email us and we will help.";
      return;
    }
    window.location.href = d.url;
  } catch (e) {
    msgEl.textContent = "Could not reach checkout. Try again in a minute.";
  }
}

document.addEventListener("DOMContentLoaded", loadCatalog);
