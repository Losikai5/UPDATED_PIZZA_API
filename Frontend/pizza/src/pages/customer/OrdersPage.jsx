import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../../components/Navbar";
import OrderCard from "../../components/OrderCard";
import LoadingSpinner from "../../components/LoadingSpinner";
import { get_my_orders, create_order, cancel_order } from "../../services/orders";

const SIZES = [
  { value: "small", label: "Small" },
  { value: "medium", label: "Medium" },
  { value: "large", label: "Large" },
  { value: "extra_large", label: "Extra Large" },
];

export default function OrdersPage() {
  const navigate = useNavigate();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ flavour: "", pizza_size: "medium", quantity: 1 });

  async function load() {
    try {
      setOrders(await get_my_orders());
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load your orders.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    (async () => { await load(); })();
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await create_order({
        flavour: form.flavour,
        pizza_size: form.pizza_size,
        quantity: Number(form.quantity),
      });
      setForm({ flavour: "", pizza_size: "medium", quantity: 1 });
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not place the order.");
    } finally {
      setBusy(false);
    }
  }

  async function handleCancel(uid) {
    setBusy(true);
    setError("");
    try {
      await cancel_order(uid);
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not cancel the order.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Navbar />
      <main className="page">
        <div className="page-head">
          <h1>My Orders</h1>
        </div>

        {error && <div className="alert alert-error" style={{ marginBottom: 18 }}>{error}</div>}

        <section className="card card-pad-lg" style={{ marginBottom: 28, maxWidth: 640 }}>
          <h2 style={{ marginBottom: 14 }}>Place a new order</h2>
          <form className="stack" onSubmit={handleCreate}>
            <div className="field">
              <label htmlFor="flavour">Flavour</label>
              <input
                id="flavour" className="input" required
                placeholder="e.g. Pepperoni"
                value={form.flavour}
                onChange={(e) => setForm({ ...form, flavour: e.target.value })}
              />
            </div>
            <div className="row" style={{ gap: 12 }}>
              <div className="field" style={{ flex: 1 }}>
                <label htmlFor="pizza_size">Size</label>
                <select
                  id="pizza_size" className="select"
                  value={form.pizza_size}
                  onChange={(e) => setForm({ ...form, pizza_size: e.target.value })}
                >
                  {SIZES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
                </select>
              </div>
              <div className="field" style={{ width: 120 }}>
                <label htmlFor="quantity">Quantity</label>
                <input
                  id="quantity" type="number" min={1} className="input"
                  value={form.quantity}
                  onChange={(e) => setForm({ ...form, quantity: e.target.value })}
                />
              </div>
            </div>
            <button className="btn btn-primary" type="submit" disabled={busy}>
              {busy ? "Working…" : "Place order"}
            </button>
          </form>
        </section>

        <h2 style={{ marginBottom: 14 }}>Order history</h2>
        {loading ? (
          <LoadingSpinner label="Loading orders…" />
        ) : orders.length === 0 ? (
          <div className="empty">You haven't placed any orders yet.</div>
        ) : (
          <div className="grid">
            {orders.map((order) => (
              <OrderCard key={order.uid} order={order}>
                {order.order_status === "pending" && (
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleCancel(order.uid)}
                    disabled={busy}
                  >
                    Cancel
                  </button>
                )}
                {order.order_status === "completed" && (
                  <button
                    className="btn btn-outline btn-sm"
                    onClick={() => navigate("/reviews")}
                  >
                    Leave a review
                  </button>
                )}
              </OrderCard>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
