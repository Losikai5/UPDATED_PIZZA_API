import { useEffect, useState } from "react";
import Navbar from "../../components/Navbar";
import OrderCard from "../../components/OrderCard";
import LoadingSpinner from "../../components/LoadingSpinner";
import { get_orders, update_order_status } from "../../services/orders";

// Valid next states per current status, mirroring ALLOWED_TRANSITIONS in
// src/Orders/service.py so the UI only offers transitions the API accepts.
const NEXT_ACTIONS = {
  pending: [
    { status: "order_accepted", label: "Accept", style: "btn-primary" },
    { status: "cancelled", label: "Cancel", style: "btn-danger" },
  ],
  order_accepted: [
    { status: "in_transit", label: "Mark in transit", style: "btn-primary" },
    { status: "cancelled", label: "Cancel", style: "btn-danger" },
  ],
  in_transit: [
    { status: "completed", label: "Mark delivered", style: "btn-primary" },
    { status: "cancelled", label: "Cancel", style: "btn-danger" },
  ],
};

const FILTERS = ["all", "pending", "order_accepted", "in_transit", "completed", "cancelled"];

export default function AdminOrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");

  async function load() {
    try {
      setOrders(await get_orders());
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load orders.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    (async () => { await load(); })();
  }, []);

  async function changeStatus(order, status) {
    setBusy(true);
    setError("");
    try {
      await update_order_status(order.uid, status);
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not update the order.");
    } finally {
      setBusy(false);
    }
  }

  const visible = filter === "all" ? orders : orders.filter((o) => o.order_status === filter);

  return (
    <>
      <Navbar />
      <main className="page">
        <div className="page-head">
          <h1>All Orders</h1>
        </div>

        {error && <div className="alert alert-error" style={{ marginBottom: 18 }}>{error}</div>}

        <div className="row wrap" style={{ marginBottom: 20 }}>
          {FILTERS.map((f) => (
            <button
              key={f}
              className={`btn btn-sm ${filter === f ? "btn-primary" : "btn-outline"}`}
              onClick={() => setFilter(f)}
            >
              {f.replace(/_/g, " ")}
            </button>
          ))}
        </div>

        {loading ? (
          <LoadingSpinner label="Loading orders…" />
        ) : visible.length === 0 ? (
          <div className="empty">No orders in this view.</div>
        ) : (
          <div className="grid">
            {visible.map((order) => (
              <OrderCard key={order.uid} order={order}>
                {(NEXT_ACTIONS[order.order_status] || []).map((action) => (
                  <button
                    key={action.status}
                    className={`btn btn-sm ${action.style}`}
                    onClick={() => changeStatus(order, action.status)}
                    disabled={busy}
                  >
                    {action.label}
                  </button>
                ))}
              </OrderCard>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
