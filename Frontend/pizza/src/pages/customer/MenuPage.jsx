import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../../components/Navbar";
import MenuItemCard from "../../components/MenuItemCard";
import LoadingSpinner from "../../components/LoadingSpinner";
import { get_menu } from "../../services/menu";
import { add_item } from "../../services/cart";
import { useAuth } from "../../context/AuthContext";
import { useCart } from "../../context/CartContext";

export default function MenuPage() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { refreshCart } = useCart();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");
  const [addingId, setAddingId] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        setItems(await get_menu());
      } catch {
        setError("Could not load the menu. Is the server running?");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  // Auto-dismiss the "added to cart" toast so it doesn't linger (3–5s rule).
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(""), 4000);
    return () => clearTimeout(timer);
  }, [toast]);

  async function handleAdd(item, size) {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }
    setAddingId(item.uid + size.uid);
    setToast("");
    try {
      await add_item({
        menu_item_uid: item.uid,
        menu_item_size_uid: size.uid,
        quantity: 1,
      });
      await refreshCart();
      setToast(`Added ${item.name} (${size.pizza_size}) to your cart.`);
    } catch (err) {
      setToast(err.response?.data?.detail || "Could not add to cart.");
    } finally {
      setAddingId(null);
    }
  }

  return (
    <>
      <Navbar />
      <main className="page">
        <div className="page-head">
          <div>
            <h1>Our Menu</h1>
            <p className="muted">Freshly baked pizzas, made to order.</p>
          </div>
        </div>

        <div aria-live="polite" role="status">
          {toast && <div className="alert alert-success" style={{ marginBottom: 18 }}>{toast}</div>}
        </div>
        {error && <div className="alert alert-error" style={{ marginBottom: 18 }}>{error}</div>}

        {loading ? (
          <LoadingSpinner label="Loading menu…" />
        ) : items.length === 0 ? (
          <div className="empty">No menu items available yet.</div>
        ) : (
          <div className="grid">
            {items.map((item) => (
              <MenuItemCard
                key={item.uid}
                item={item}
                onAdd={handleAdd}
                adding={addingId?.startsWith(item.uid)}
              />
            ))}
          </div>
        )}
      </main>
    </>
  );
}
