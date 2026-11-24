const express = require("express");
const fs = require("fs");
const path = require("path");

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
    ],
    coupons: [{ code: "NEXORA10", discount_pct: 10, active: true }],
    orders: [],
  };
}

const orders = [];
const reviews = [{ sku: "NX-SEC-100", author: "Operations Lead", rating: 5, comment: "Reliable perimeter telemetry." }];

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
  if (coupon) {
    const c = (data.coupons || []).find((x) => x.code === coupon && x.active);
    if (c) total = total * (1 - c.discount_pct / 100);
  }
  const order = {
    id: `ORD-SHOP-${1000 + orders.length + 1}`,
    sku: product.sku,
    quantity: qty,
    total_amount: Number(total.toFixed(2)),
    status: "confirmed",
  };
  orders.push(order);
  res.status(201).json({ order });
});

app.get("/api/orders", (_req, res) => {
  res.json({ orders });
});

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
  const q = (req.query.q || "").toString().toLowerCase();
  const items = (data.products || []).filter((p) => !q || p.name.toLowerCase().includes(q));
  const cards = items
    .map(
      (p) =>
        `<div style="background:#fff;padding:1rem;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.08)">
          <h3>${p.name}</h3><p>SKU: <code>${p.sku}</code> | ${p.category}</p>
          <p><strong>$${p.price.toFixed(2)}</strong> (Stock: ${p.stock})</p>
        </div>`
    )
    .join("");
  res.send(`<!DOCTYPE html><html><head><meta charset="utf-8"><title>Nexora Store</title></head>
  <body style="font-family:system-ui,sans-serif;background:#f4f6f9;margin:0">
    <header style="background:#0f172a;color:#fff;padding:1rem 2rem"><strong>Nexora Enterprise Store</strong> (shop.nexora.test)</header>
    <main style="max-width:1000px;margin:2rem auto;padding:0 1rem">
      <form method="get" style="margin-bottom:1rem"><input name="q" value="${q}" placeholder="Search products..." style="padding:.5rem;width:260px"> <button type="submit">Search</button></form>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem">${cards}</div>
    </main>
  </body></html>`);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Nexora E-commerce listening on port ${PORT}`);
});
