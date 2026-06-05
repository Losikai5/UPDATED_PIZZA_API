import { useEffect, useState } from "react";
import Navbar from "../../components/Navbar";
import LoadingSpinner from "../../components/LoadingSpinner";
import { formatPrice, SIZE_LABELS } from "../../utils/format";
import {
  get_menu,
  create_menu_item,
  update_menu_item,
  delete_menu_item,
  toggle_availability,
} from "../../services/menu";

const ALL_SIZES = ["small", "medium", "large", "extra_large"];
const EMPTY_FORM = {
  name: "",
  flavour: "",
  description: "",
  is_available: true,
  sizes: [{ pizza_size: "small", price: "" }],
};

export default function AdminMenuPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);

  async function load() {
    try {
      setItems(await get_menu());
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load the menu.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    (async () => { await load(); })();
  }, []);

  function resetForm() {
    setForm(EMPTY_FORM);
    setEditingId(null);
  }

  function startEdit(item) {
    setEditingId(item.uid);
    setForm({
      name: item.name,
      flavour: item.flavour,
      description: item.description,
      is_available: item.is_available,
      sizes: item.sizes.map((s) => ({ pizza_size: s.pizza_size, price: s.price })),
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function updateSize(index, key, value) {
    setForm((f) => {
      const sizes = [...f.sizes];
      sizes[index] = { ...sizes[index], [key]: value };
      return { ...f, sizes };
    });
  }

  function addSizeRow() {
    setForm((f) => ({ ...f, sizes: [...f.sizes, { pizza_size: "medium", price: "" }] }));
  }

  function removeSizeRow(index) {
    setForm((f) => ({ ...f, sizes: f.sizes.filter((_, i) => i !== index) }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (editingId) {
        // MenuItemUpdate only supports the descriptive fields, not sizes.
        await update_menu_item(editingId, {
          name: form.name,
          flavour: form.flavour,
          description: form.description,
          is_available: form.is_available,
        });
      } else {
        await create_menu_item({
          name: form.name,
          flavour: form.flavour,
          description: form.description,
          is_available: form.is_available,
          sizes: form.sizes.map((s) => ({
            pizza_size: s.pizza_size,
            price: Number(s.price),
          })),
        });
      }
      resetForm();
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not save the menu item.");
    } finally {
      setBusy(false);
    }
  }

  async function handleToggle(item) {
    setBusy(true);
    try {
      await toggle_availability(item.uid);
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not toggle availability.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(item) {
    if (!window.confirm(`Delete "${item.name}"? This cannot be undone.`)) return;
    setBusy(true);
    try {
      await delete_menu_item(item.uid);
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not delete the menu item.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Navbar />
      <main className="page">
        <div className="page-head">
          <h1>Manage Menu</h1>
        </div>

        {error && <div className="alert alert-error" style={{ marginBottom: 18 }}>{error}</div>}

        <section className="card card-pad-lg" style={{ marginBottom: 28, maxWidth: 680 }}>
          <h2 style={{ marginBottom: 14 }}>
            {editingId ? "Edit menu item" : "Add a menu item"}
          </h2>
          <form className="stack" onSubmit={handleSubmit}>
            <div className="row" style={{ gap: 12 }}>
              <div className="field" style={{ flex: 1 }}>
                <label htmlFor="name">Name</label>
                <input id="name" className="input" required
                  value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </div>
              <div className="field" style={{ flex: 1 }}>
                <label htmlFor="flavour">Flavour</label>
                <input id="flavour" className="input" required
                  value={form.flavour} onChange={(e) => setForm({ ...form, flavour: e.target.value })} />
              </div>
            </div>
            <div className="field">
              <label htmlFor="description">Description</label>
              <textarea id="description" className="textarea" required
                value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </div>

            {!editingId && (
              <div className="field">
                <label>Sizes &amp; prices (UGX)</label>
                <div className="stack" style={{ gap: 8 }}>
                  {form.sizes.map((s, i) => (
                    <div className="row" key={i} style={{ gap: 8 }}>
                      <select
                        className="select" style={{ flex: 1 }}
                        value={s.pizza_size}
                        onChange={(e) => updateSize(i, "pizza_size", e.target.value)}
                      >
                        {ALL_SIZES.map((sz) => (
                          <option key={sz} value={sz}>{SIZE_LABELS[sz]}</option>
                        ))}
                      </select>
                      <input
                        className="input" type="number" min={0} step="any" required
                        style={{ width: 140 }} placeholder="Price"
                        value={s.price}
                        onChange={(e) => updateSize(i, "price", e.target.value)}
                      />
                      {form.sizes.length > 1 && (
                        <button type="button" className="btn btn-danger btn-sm"
                          onClick={() => removeSizeRow(i)}>×</button>
                      )}
                    </div>
                  ))}
                </div>
                <button type="button" className="btn btn-ghost btn-sm" style={{ alignSelf: "flex-start" }}
                  onClick={addSizeRow}>+ Add size</button>
              </div>
            )}

            <label className="row" style={{ gap: 8, cursor: "pointer" }}>
              <input type="checkbox" checked={form.is_available}
                onChange={(e) => setForm({ ...form, is_available: e.target.checked })} />
              <span>Available</span>
            </label>

            <div className="row">
              <button className="btn btn-primary" type="submit" disabled={busy}>
                {busy ? "Saving…" : editingId ? "Update item" : "Create item"}
              </button>
              {editingId && (
                <button type="button" className="btn btn-ghost" onClick={resetForm}>Cancel</button>
              )}
            </div>
          </form>
        </section>

        <h2 style={{ marginBottom: 14 }}>Menu items</h2>
        {loading ? (
          <LoadingSpinner />
        ) : items.length === 0 ? (
          <div className="empty">No menu items yet. Add your first one above.</div>
        ) : (
          <div className="grid">
            {items.map((item) => (
              <div className="card stack" key={item.uid}>
                <div className="spread">
                  <h3>{item.name}</h3>
                  {item.is_available
                    ? <span className="badge badge-green">Available</span>
                    : <span className="badge badge-gray">Hidden</span>}
                </div>
                <span className="badge badge-red" style={{ alignSelf: "flex-start" }}>{item.flavour}</span>
                <p className="muted" style={{ textAlign: "left", fontSize: 14 }}>{item.description}</p>
                <div className="stack" style={{ gap: 4 }}>
                  {item.sizes.map((s) => (
                    <div className="spread" key={s.uid} style={{ fontSize: 14 }}>
                      <span className="muted">{SIZE_LABELS[s.pizza_size] || s.pizza_size}</span>
                      <span className="price">{formatPrice(s.price)}</span>
                    </div>
                  ))}
                </div>
                <hr className="divider" />
                <div className="row wrap">
                  <button className="btn btn-outline btn-sm" onClick={() => startEdit(item)} disabled={busy}>Edit</button>
                  <button className="btn btn-outline btn-sm" onClick={() => handleToggle(item)} disabled={busy}>
                    {item.is_available ? "Hide" : "Show"}
                  </button>
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(item)} disabled={busy}>Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
