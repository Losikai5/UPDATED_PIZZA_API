import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../../components/Navbar";
import CartItem from "../../components/CartItem";
import LoadingSpinner from "../../components/LoadingSpinner";
import { formatPrice } from "../../utils/format";
import { update_item, remove_item, clear_cart } from "../../services/cart";
import { create_order } from "../../services/orders";
import { useCart } from "../../context/CartContext";

export default function CartPage() {
  const navigate = useNavigate();
  const { cart, cartItems, cartTotal, refreshCart } = useCart();

  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");

  useEffect(() => {
    (async () => {
      await refreshCart();
      setLoading(false);
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleUpdate(itemUid, quantity) {
    setBusy(true);
    setError("");
    try {
      await update_item(itemUid, quantity);
      await refreshCart();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not update item.");
    } finally {
      setBusy(false);
    }
  }

  async function handleRemove(itemUid) {
    setBusy(true);
    setError("");
    try {
      await remove_item(itemUid);
      await refreshCart();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not remove item.");
    } finally {
      setBusy(false);
    }
  }

  async function handleClear() {
    setBusy(true);
    setError("");
    try {
      await clear_cart();
      await refreshCart();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not clear cart.");
    } finally {
      setBusy(false);
    }
  }

  async function handleCheckout() {
    setBusy(true);
    setError("");
    setInfo("");
    try {
      // The backend places one pizza per order and allows a single pending
      // order at a time, so we submit cart items one by one.
      for (const item of cartItems) {
        await create_order({
          quantity: item.quantity,
          pizza_size: item.pizza_size,
          // Use the menu flavour (not the display name) so the backend can
          // price the order — calculate_total_price matches on flavour + size.
          flavour: item.flavour,
        });
      }
      await clear_cart();
      await refreshCart();
      navigate("/orders");
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Could not place your order. Please try again."
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Navbar />
      <main className="page">
        <div className="page-head">
          <h1>Your Cart</h1>
        </div>

        {error && <div className="alert alert-error" style={{ marginBottom: 18 }}>{error}</div>}
        {info && <div className="alert alert-info" style={{ marginBottom: 18 }}>{info}</div>}

        {loading ? (
          <LoadingSpinner label="Loading cart…" />
        ) : !cart || cartItems.length === 0 ? (
          <div className="empty">
            Your cart is empty.{" "}
            <span
              role="button"
              tabIndex={0}
              onClick={() => navigate("/menu")}
              onKeyDown={(e) => e.key === "Enter" && navigate("/menu")}
              style={{ color: "var(--accent)", cursor: "pointer" }}
            >
              Browse the menu →
            </span>
          </div>
        ) : (
          <div style={{ display: "grid", gap: 24, gridTemplateColumns: "1fr", maxWidth: 720 }}>
            <div className="stack">
              {cartItems.map((item) => (
                <CartItem
                  key={item.uid}
                  item={item}
                  onUpdateQty={handleUpdate}
                  onRemove={handleRemove}
                  busy={busy}
                />
              ))}
            </div>

            <div className="card stack">
              <div className="spread">
                <span style={{ fontWeight: 600 }}>Total</span>
                <span className="price" style={{ fontSize: 20 }}>{formatPrice(cartTotal)}</span>
              </div>
              <div className="row wrap">
                <button className="btn btn-primary" onClick={handleCheckout} disabled={busy}>
                  {busy ? "Placing order…" : "Checkout"}
                </button>
                <button className="btn btn-outline" onClick={handleClear} disabled={busy}>
                  Clear cart
                </button>
                <button className="btn btn-ghost" onClick={() => navigate("/menu")} disabled={busy}>
                  Add more
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </>
  );
}
