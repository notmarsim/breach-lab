const express = require("express");
const fs = require("fs");

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const DATA_PATH = process.env.NEXORA_DATASET_PATH || "/data/dataset.json";

function loadDataset() {
  if (fs.existsSync(DATA_PATH)) {
    return JSON.parse(fs.readFileSync(DATA_PATH, "utf-8"));
  }
  return {
    products: [
      { sku: "NX-SEC-100", name: "Nexora Sentinel Gateway", category: "Security Appliances", price: 1299.0, stock: 42 },
      { sku: "NX-LOG-200", name: "Nexora AuditStream Enterprise", category: "Software", price: 499.0, stock: 150 },
      { sku: "NX-IAM-300", name: "Nexora Identity Vault", category: "Identity", price: 799.0, stock: 85 },
    ],
    coupons: [{ code: "NEXORA10", discount_pct: 10, active: true }],
    orders: [],
  };
}

const orders = [];
const reviews = [
  { sku: "NX-SEC-100", author: "Operations Lead", rating: 5, comment: "Reliable perimeter telemetry and zero packet drops." },
  { sku: "NX-IAM-300", author: "CISO Office", rating: 5, comment: "Clean role-based provisioning across all departments." },
];

app.get("/health", (_req, res) => {
  res.json({ status: "healthy", service: "ecommerce", domain: "shop.nexora.test" });
});

app.get("/api/products", (req, res) => {
  const data = loadDataset();
  const q = (req.query.q || "").toString().toLowerCase();
  const cat = (req.query.category || "").toString().toLowerCase();
  let items = data.products || [];
  if (q) items = items.filter((p) => p.name.toLowerCase().includes(q) || p.sku.toLowerCase().includes(q));
  if (cat) items = items.filter((p) => p.category.toLowerCase() === cat);
  res.json({ products: items });
});

app.post("/api/checkout", (req, res) => {
  const data = loadDataset();
  const { sku, quantity = 1, coupon } = req.body || {};
  const product = (data.products || []).find((p) => p.sku === sku);
  if (!product) return res.status(404).json({ error: "Product not found" });
  const qty = Math.max(1, parseInt(quantity, 10) || 1);
  let total = product.price * qty;
  let appliedCoupon = null;
  if (coupon) {
    const c = (data.coupons || []).find((x) => x.code === coupon && x.active);
    if (c) {
      total = total * (1 - c.discount_pct / 100);
      appliedCoupon = c.code;
    }
  }
  const order = {
    id: `ORD-SHOP-${1000 + orders.length + 1}`,
    sku: product.sku,
    product_name: product.name,
    quantity: qty,
    coupon: appliedCoupon,
    total_amount: Number(total.toFixed(2)),
    status: "confirmed",
    created_at: new Date().toISOString(),
  };
  orders.push(order);
  res.status(201).json({ order });
});

app.get("/api/orders", (_req, res) => res.json({ orders }));

app.post("/api/refunds", (req, res) => {
  const { order_id, reason } = req.body || {};
  const order = orders.find((o) => o.id === order_id);
  if (!order) return res.status(404).json({ error: "Order not found" });
  order.status = "refund_requested";
  order.refund_reason = reason || "Customer request";
  res.json({ order });
});

app.get("/api/reviews", (_req, res) => res.json({ reviews }));

app.get("/", (req, res) => {
  const data = loadDataset();
  const q = (req.query.q || "").toString();
  const cat = (req.query.category || "").toString();
  const allProducts = data.products || [];
  const categories = [...new Set(allProducts.map((p) => p.category))];
  const items = allProducts.filter((p) => {
    const matchQ = !q || p.name.toLowerCase().includes(q.toLowerCase()) || p.sku.toLowerCase().includes(q.toLowerCase());
    const matchC = !cat || p.category === cat;
    return matchQ && matchC;
  });

  const catLinks = [`<a href="/" class="pill ${!cat ? "active" : ""}">All</a>`]
    .concat(categories.map((c) => `<a href="/?category=${encodeURIComponent(c)}" class="pill ${cat === c ? "active" : ""}">${c}</a>`))
    .join("");

  const cards = items
    .map(
      (p) => `
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span class="badge">${p.category}</span>
          <span style="font-size:12px;color:${p.stock > 25 ? "#059669" : "#d97706"}">${p.stock > 25 ? "In Stock" : "Low Stock"} (${p.stock})</span>
        </div>
        <h3 style="margin:10px 0 4px">${p.name}</h3>
        <div style="color:#64748b;font-size:13px;margin-bottom:12px">SKU: <code>${p.sku}</code></div>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <strong style="font-size:20px">$${p.price.toFixed(2)}</strong>
          <button class="btn" onclick="addToCart('${p.sku}','${p.name.replace(/'/g, "")}',${p.price})">Add to Cart</button>
        </div>
      </div>`
    )
    .join("");

  res.send(`<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Nexora Enterprise Store</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: 'Inter', system-ui, sans-serif; margin: 0; background: #f8fafc; color: #0f172a; }
    header { background: #0f172a; color: #fff; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
    .container { max-width: 1120px; margin: 2rem auto; padding: 0 1.25rem; display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; }
    .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.25rem; }
    .badge { background: #e0f2fe; color: #0369a1; padding: 3px 9px; border-radius: 999px; font-size: 12px; font-weight: 600; }
    .pill { display: inline-block; padding: 6px 12px; border-radius: 999px; border: 1px solid #cbd5e1; color: #334155; text-decoration: none; font-size: 13px; margin-right: 6px; }
    .pill.active { background: #0ea5e9; color: #fff; border-color: #0ea5e9; }
    .btn { background: #0ea5e9; color: #fff; border: none; padding: 8px 14px; border-radius: 7px; font-weight: 600; cursor: pointer; }
    .btn:hover { background: #0284c7; }
    input { padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 7px; }
    @media (max-width: 860px) { .container { grid-template-columns: 1fr; } }
  </style></head>
  <body>
    <header>
      <div><strong style="font-size:1.15rem;color:#38bdf8">Nexora</strong> Enterprise Store <small style="color:#94a3b8">(shop.nexora.test)</small></div>
      <div style="font-size:13px;color:#cbd5e1">Promo Code: <code>NEXORA10</code></div>
    </header>
    <div class="container">
      <div>
        <form method="get" style="display:flex;gap:8px;margin-bottom:1rem">
          <input name="q" value="${q.replace(/"/g, "&quot;")}" placeholder="Search appliances, licenses, SKU..." style="flex:1">
          <button class="btn" type="submit">Search</button>
        </form>
        <div style="margin-bottom:1.25rem">${catLinks}</div>
        <div class="grid">${cards}</div>
      </div>
      <div>
        <div class="card">
          <h3 style="margin-top:0">Shopping Cart &amp; Checkout</h3>
          <div id="cart-items" style="font-size:14px;color:#475569;margin-bottom:12px">Your cart is empty.</div>
          <input id="coupon" placeholder="Coupon code (optional)" style="width:100%;margin-bottom:10px">
          <button class="btn" style="width:100%" onclick="checkout()">Complete Simulated Order</button>
          <div id="checkout-msg" style="margin-top:10px;font-size:13px"></div>
        </div>
        <div class="card" style="margin-top:1rem">
          <h4 style="margin-top:0">Verified Customer Reviews</h4>
          ${reviews.map((r) => `<p style="font-size:13px;margin:6px 0"><strong>${r.author}</strong> (${r.rating}/5): ${r.comment}</p>`).join("")}
        </div>
      </div>
    </div>
    <script>
      const cart = [];
      function addToCart(sku, name, price) {
        const existing = cart.find(i => i.sku === sku);
        if (existing) existing.quantity += 1; else cart.push({ sku, name, price, quantity: 1 });
        renderCart();
      }
      function renderCart() {
        const el = document.getElementById('cart-items');
        if (!cart.length) { el.innerHTML = 'Your cart is empty.'; return; }
        let total = 0;
        el.innerHTML = cart.map(i => { total += i.price * i.quantity; return '<div>' + i.name + ' x' + i.quantity + ' — $' + (i.price*i.quantity).toFixed(2) + '</div>'; }).join('')
          + '<hr><strong>Subtotal: $' + total.toFixed(2) + '</strong>';
      }
      async function checkout() {
        if (!cart.length) return;
        const coupon = document.getElementById('coupon').value.trim();
        const res = await fetch('/api/checkout', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sku: cart[0].sku, quantity: cart[0].quantity, coupon })
        });
        const data = await res.json();
        document.getElementById('checkout-msg').innerHTML = res.ok
          ? '<span style="color:#059669">Order confirmed: <b>' + data.order.id + '</b> ($' + data.order.total_amount + ')</span>'
          : '<span style="color:#dc2626">' + (data.error || 'Error') + '</span>';
      }
    </script>
  </body></html>`);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Nexora E-commerce listening on port ${PORT}`);
});
