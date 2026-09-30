const CATALOG_URL = "/products.json";
let catalog = [];

async function loadCatalog() {
  const r = await fetch(CATALOG_URL);
  catalog = await r.json();
  document.querySelectorAll("[data-edition]").forEach((el) => {
    renderGrid(el, el.dataset.edition);
  });
}

function renderGrid(el, edition) {
  const items = catalog.filter((p) => p.edition === edition || (edition === "all" && true));
  el.innerHTML = items
    .map(
      (p) => `
    <div class="card">
      <div class="sku">${p.edition === "bundle" ? "Bundle" : p.edition === "pg" ? "Prince George's edition" : "Montgomery Co. edition"}</div>
      <h3>${p.name}</h3>
      <div class="price">${p.price}</div>
      <p style="font-size:14px">${p.blurb}</p>
      <ul>${p.includes.map((i) => `<li>${i}</li>`).join("")}</ul>
      <input type="email" placeholder="Email for your download link" data-email="${p.sku}" aria-label="Email for download link">
      <button class="btn" data-buy="${p.sku}">Buy ${p.price}</button>
      <div class="buy-msg" data-msg="${p.sku}"></div>
    </div>`
    )
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
