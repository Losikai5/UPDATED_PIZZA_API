import { useEffect, useState } from "react";
import Navbar from "../../components/Navbar";
import LoadingSpinner from "../../components/LoadingSpinner";
import { get_reviews } from "../../services/reviews";

function Stars({ rating }) {
  return (
    <span className="stars" aria-label={`${rating} out of 5`}>
      {"★".repeat(rating)}{"☆".repeat(5 - rating)}
    </span>
  );
}

export default function AdminReviewsPage() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        setReviews(await get_reviews());
      } catch (err) {
        setError(err.response?.data?.detail || "Could not load reviews.");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const avg =
    reviews.length > 0
      ? (reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length).toFixed(1)
      : null;

  return (
    <>
      <Navbar />
      <main className="page">
        <div className="page-head">
          <div>
            <h1>All Reviews</h1>
            {avg && (
              <p className="muted">
                {reviews.length} review{reviews.length === 1 ? "" : "s"} · average {avg} ★
              </p>
            )}
          </div>
        </div>

        {error && <div className="alert alert-error" style={{ marginBottom: 18 }}>{error}</div>}

        {loading ? (
          <LoadingSpinner label="Loading reviews…" />
        ) : reviews.length === 0 ? (
          <div className="empty">No reviews have been submitted yet.</div>
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
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
