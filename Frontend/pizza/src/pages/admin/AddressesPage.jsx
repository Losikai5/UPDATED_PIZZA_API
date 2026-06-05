import { useEffect, useState } from "react";
import Navbar from "../../components/Navbar";
import LoadingSpinner from "../../components/LoadingSpinner";
import {
  get_my_addresses,
  create_address,
  update_address,
  delete_address,
  set_default_address,
} from "../../services/addresses";

const EMPTY = {
  street_address: "",
  city: "",
  state: "",
  country: "",
  postal_code: "",
  is_default: false,
};

export default function AddressesPage() {
  const [addresses, setAddresses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(EMPTY);

  async function load() {
    try {
      setAddresses(await get_my_addresses());
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load addresses.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    (async () => { await load(); })();
  }, []);

  function update(e) {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
  }

  function resetForm() {
    setForm(EMPTY);
    setEditingId(null);
  }

  function startEdit(addr) {
    setEditingId(addr.uid);
    setForm({
      street_address: addr.street_address,
      city: addr.city,
      state: addr.state,
      country: addr.country,
      postal_code: addr.postal_code,
      is_default: addr.is_default,
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      if (editingId) {
        await update_address(editingId, form);
      } else {
        await create_address(form);
      }
      resetForm();
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not save the address.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(uid) {
    if (!window.confirm("Delete this address?")) return;
    setBusy(true);
    try {
      await delete_address(uid);
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not delete the address.");
    } finally {
      setBusy(false);
    }
  }

  async function handleSetDefault(uid) {
    setBusy(true);
    try {
      await set_default_address(uid);
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not set default address.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Navbar />
      <main className="page">
        <div className="page-head">
          <h1>Delivery Addresses</h1>
        </div>

        {error && <div className="alert alert-error" style={{ marginBottom: 18 }}>{error}</div>}

        <section className="card card-pad-lg" style={{ marginBottom: 28, maxWidth: 640 }}>
          <h2 style={{ marginBottom: 14 }}>{editingId ? "Edit address" : "Add an address"}</h2>
          <form className="stack" onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="street_address">Street address</label>
              <input id="street_address" name="street_address" className="input" required
                value={form.street_address} onChange={update} />
            </div>
            <div className="row" style={{ gap: 12 }}>
              <div className="field" style={{ flex: 1 }}>
                <label htmlFor="city">City</label>
                <input id="city" name="city" className="input" required value={form.city} onChange={update} />
              </div>
              <div className="field" style={{ flex: 1 }}>
                <label htmlFor="state">State / Region</label>
                <input id="state" name="state" className="input" required value={form.state} onChange={update} />
              </div>
            </div>
            <div className="row" style={{ gap: 12 }}>
              <div className="field" style={{ flex: 1 }}>
                <label htmlFor="country">Country</label>
                <input id="country" name="country" className="input" required value={form.country} onChange={update} />
              </div>
              <div className="field" style={{ flex: 1 }}>
                <label htmlFor="postal_code">Postal code</label>
                <input id="postal_code" name="postal_code" className="input" required
                  value={form.postal_code} onChange={update} />
              </div>
            </div>
            <label className="row" style={{ gap: 8, cursor: "pointer" }}>
              <input type="checkbox" name="is_default" checked={form.is_default} onChange={update} />
              <span>Set as default address</span>
            </label>
            <div className="row">
              <button className="btn btn-primary" type="submit" disabled={busy}>
                {busy ? "Saving…" : editingId ? "Update address" : "Add address"}
              </button>
              {editingId && (
                <button type="button" className="btn btn-ghost" onClick={resetForm}>Cancel</button>
              )}
            </div>
          </form>
        </section>

        <h2 style={{ marginBottom: 14 }}>Saved addresses</h2>
        {loading ? (
          <LoadingSpinner />
        ) : addresses.length === 0 ? (
          <div className="empty">No saved addresses yet.</div>
        ) : (
          <div className="grid">
            {addresses.map((addr) => (
              <div className="card stack" key={addr.uid}>
                <div className="spread">
                  <h3>{addr.city}</h3>
                  {addr.is_default && <span className="badge badge-green">Default</span>}
                </div>
                <p className="muted" style={{ textAlign: "left", fontSize: 14 }}>
                  {addr.street_address}<br />
                  {addr.state}, {addr.country} {addr.postal_code}
                </p>
                <hr className="divider" />
                <div className="row wrap">
                  {!addr.is_default && (
                    <button className="btn btn-outline btn-sm" onClick={() => handleSetDefault(addr.uid)} disabled={busy}>
                      Set default
                    </button>
                  )}
                  <button className="btn btn-outline btn-sm" onClick={() => startEdit(addr)} disabled={busy}>Edit</button>
                  <button className="btn btn-danger btn-sm" onClick={() => handleDelete(addr.uid)} disabled={busy}>Delete</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
