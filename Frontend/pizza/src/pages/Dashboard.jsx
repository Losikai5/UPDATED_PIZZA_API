import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import NotificationCard from "../components/NotificationCard";
import LoadingSpinner from "../components/LoadingSpinner";
import { useAuth } from "../context/AuthContext";
import {
  get_my_notifications,
  mark_notification_as_read,
  mark_all_as_read,
} from "../services/notifications";
import { get_dashboard_stats } from "../services/admin";

const QUICK_LINKS = [
  { to: "/menu", title: "Browse Menu", desc: "Pick your pizza and add to cart" },
  { to: "/cart", title: "Your Cart", desc: "Review items and check out" },
  { to: "/orders", title: "My Orders", desc: "Track and manage your orders" },
  { to: "/reviews", title: "Reviews", desc: "Rate your completed orders" },
];

export default function Dashboard() {
  const { user, isAdmin } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const results = await Promise.allSettled([
        get_my_notifications(),
        isAdmin ? get_dashboard_stats() : Promise.resolve(null),
      ]);
      if (results[0].status === "fulfilled") setNotifications(results[0].value || []);
      if (results[1].status === "fulfilled") setStats(results[1].value);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    (async () => { await load(); })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleMarkRead(uid) {
    setBusy(true);
    try {
      await mark_notification_as_read(uid);
      setNotifications((prev) =>
        prev.map((n) => (n.uid === uid ? { ...n, is_read: true } : n))
      );
    } finally {
      setBusy(false);
    }
  }

  async function handleMarkAll() {
    setBusy(true);
    try {
      await mark_all_as_read();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } finally {
      setBusy(false);
    }
  }

  const unread = notifications.filter((n) => !n.is_read).length;

  const statCards = stats && [
    { label: "Users", value: stats.users_count },
    { label: "Verified", value: stats.verified_users_count },
    { label: "Admins", value: stats.admins_count },
    { label: "Orders", value: stats.orders_count },
    { label: "Reviews", value: stats.reviews_count },
  ];

  return (
    <>
      <Navbar />
      <main className="page">
        <div className="page-head">
          <div>
            <h1>Hi{user?.email ? `, ${user.email.split("@")[0]}` : ""} 👋</h1>
            <p className="muted">Welcome to your Losika Pizza dashboard.</p>
          </div>
        </div>

        {isAdmin && statCards && (
          <section style={{ marginBottom: 28 }}>
            <h2 style={{ marginBottom: 14 }}>Overview</h2>
            <div className="grid" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))" }}>
              {statCards.map((s) => (
                <div className="card center" key={s.label}>
                  <div className="stat-num">{s.value ?? 0}</div>
                  <div className="muted">{s.label}</div>
                </div>
              ))}
            </div>
          </section>
        )}

        <section style={{ marginBottom: 28 }}>
          <h2 style={{ marginBottom: 14 }}>Quick actions</h2>
          <div className="grid">
            {QUICK_LINKS.map((q) => (
              <Link key={q.to} to={q.to} className="card stack" style={{ textDecoration: "none" }}>
                <h3>{q.title}</h3>
                <p className="muted" style={{ textAlign: "left", fontSize: 14 }}>{q.desc}</p>
              </Link>
            ))}
          </div>
        </section>

        <section>
          <div className="spread" style={{ marginBottom: 14 }}>
            <h2>Notifications {unread > 0 && <span className="badge badge-red">{unread} new</span>}</h2>
            {unread > 0 && (
              <button className="btn btn-outline btn-sm" onClick={handleMarkAll} disabled={busy}>
                Mark all read
              </button>
            )}
          </div>

          {loading ? (
            <LoadingSpinner />
          ) : notifications.length === 0 ? (
            <div className="empty">You have no notifications yet.</div>
          ) : (
            <div className="stack">
              {notifications.map((n) => (
                <NotificationCard
                  key={n.uid}
                  notification={n}
                  onMarkRead={handleMarkRead}
                  busy={busy}
                />
              ))}
            </div>
          )}
        </section>
      </main>
    </>
  );
}
