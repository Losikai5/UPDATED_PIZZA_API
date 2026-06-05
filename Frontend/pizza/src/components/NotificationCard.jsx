export default function NotificationCard({ notification, onMarkRead, busy }) {
  const { message, notification_type, is_read, created_at } = notification;

  return (
    <div
      className="card spread"
      style={{ gap: 14, opacity: is_read ? 0.7 : 1 }}
    >
      <div className="stack" style={{ gap: 4, alignItems: "flex-start" }}>
        <div className="row">
          {!is_read && (
            <span
              aria-hidden
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: "var(--accent)",
                display: "inline-block",
              }}
            />
          )}
          <span className="badge badge-gray">
            {String(notification_type).replace(/_/g, " ")}
          </span>
        </div>
        <p style={{ textAlign: "left", fontSize: 15 }}>{message}</p>
        <span className="muted" style={{ fontSize: 12 }}>
          {new Date(created_at).toLocaleString()}
        </span>
      </div>

      {!is_read && onMarkRead && (
        <button
          className="btn btn-ghost btn-sm"
          onClick={() => onMarkRead(notification.uid)}
          disabled={busy}
        >
          Mark read
        </button>
      )}
    </div>
  );
}
