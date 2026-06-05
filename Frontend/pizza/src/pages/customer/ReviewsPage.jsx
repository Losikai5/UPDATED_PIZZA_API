import { useEffect, useState } from "react";
import Navbar from "../../components/Navbar";
import LoadingSpinner from "../../components/LoadingSpinner";
import { useAuth } from "../../context/AuthContext";
import { get_my_orders } from "../../services/orders";
import { create_review, get_reviews_by_user, delete_review } from "../../services/reviews";

function Stars({ rating }) {
  return (
    <span className="stars" aria-label={`${rating} out of 5`}>
      {"★".repeat(rating)}{"☆".repeat(5 - rating)}
    </span>
  );
}

export default function ReviewsPage() {
  const { user } = useAuth();
  const [completedOrders, setCompletedOrders] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [form, setForm] = useState({ orders_id: "", comment: "", rating: 5 });

  async function load() {
    setLoading(true);
    try {
      const [orders, myReviews] = await Promise.all([
        get_my_orders(),
        user?.uid ? get_reviews_by_user(user.uid) : Promise.resolve([]),
      ]);
      setCompletedOrders((orders || []).filter((o) => o.order_status === "completed"));
      setReviews(myReviews || []);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not load reviews.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    (async () => { await load(); })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.orders_id) {
      setError("Select a completed order to review.");
      return;
    }
    setBusy(true);
    setError("");
    setSuccess("");
    try {
      await create_review(form.orders_id, {
        comment: form.comment,
        rating: Number(form.rating),
      });
      setSuccess("Thanks for your review!");
      setForm({ orders_id: "", comment: "", rating: 5 });
      await load();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not submit your review.");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(uid) {
    setBusy(true);
    setError("");
    try {
      await delete_review(uid);
      setReviews((prev) => prev.filter((r) => r.uid !== uid));
    } catch (err) {
      setError(err.response?.data?.detail || "Could not delete the review.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <Navbar />
      <main className="page">
        <div className="page-head">
          <h1>Reviews</h1>
        </div>

        {error && <div className="alert alert-error" style={{ marginBottom: 18 }}>{error}</div>}
        {success && <div className="alert alert-success" style={{ marginBottom: 18 }}>{success}</div>}

        <section className="card card-pad-lg" style={{ marginBottom: 28, maxWidth: 640 }}>
          <h2 style={{ marginBottom: 14 }}>Write a review</h2>
          {completedOrders.length === 0 ? (
            <p className="muted">You can review an order once it has been completed.</p>
          ) : (
            <form className="stack" onSubmit={handleSubmit}>
              <div className="field">
                <label htmlFor="orders_id">Completed order</label>
                <select
                  id="orders_id" className="select"
                  value={form.orders_id}
                  onChange={(e) => setForm({ ...form, orders_id: e.target.value })}
                  required
                >
                  <option value="">Select an order…</option>
                  {completedOrders.map((o) => (
                    <option key={o.uid} value={o.uid}>
                      {o.flavour} · {o.pizza_size} · #{String(o.uid).slice(0, 8)}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label htmlFor="rating">Rating</label>
                <select
                  id="rating" className="select"
                  value={form.rating}
                  onChange={(e) => setForm({ ...form, rating: e.target.value })}
                >
                  {[5, 4, 3, 2, 1].map((r) => (
                    <option key={r} value={r}>{"★".repeat(r)} ({r})</option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label htmlFor="comment">Comment</label>
                <textarea
                  id="comment" className="textarea" required
                  placeholder="Tell us what you thought…"
                  value={form.comment}
                  onChange={(e) => setForm({ ...form, comment: e.target.value })}
                />
              </div>
              <button className="btn btn-primary" type="submit" disabled={busy}>
                {busy ? "Submitting…" : "Submit review"}
              </button>
            </form>
          )}
        </section>

        <h2 style={{ marginBottom: 14 }}>My reviews</h2>
        {loading ? (
          <LoadingSpinner />
        ) : reviews.length === 0 ? (
          <div className="empty">You haven't written any reviews yet.</div>
        ) : (
          <div className="grid">
            {reviews.map((r) => (
              <div className="card stack" key={r.uid}>
                <div className="spread">
                  <Stars rating={r.rating} />
                  <span className="muted" style={{ fontSize: 12 }}>
                    {new Date(r.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p style={{ textAlign: "left" }}>{r.comment}</p>
                <button
                  className="btn btn-danger btn-sm"
                  style={{ alignSelf: "flex-start" }}
                  onClick={() => handleDelete(r.uid)}
                  disabled={busy}
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
