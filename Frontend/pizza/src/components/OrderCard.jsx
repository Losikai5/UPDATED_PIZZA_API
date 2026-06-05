import { formatPrice, SIZE_LABELS } from "../utils/format";

const STATUS_BADGE = {
  pending: "badge-amber",
  order_accepted: "badge-blue",
  in_transit: "badge-blue",
  completed: "badge-green",
  cancelled: "badge-red",
};

const STATUS_LABEL = {
  pending: "Pending",
  order_accepted: "Accepted",
  in_transit: "In transit",
  completed: "Completed",
  cancelled: "Cancelled",
};

function OrderStatusBadge({ status }) {
  return (
    <span className={`badge ${STATUS_BADGE[status] || "badge-gray"}`}>
      {STATUS_LABEL[status] || status}
    </span>
  );
}

export default function OrderCard({ order, children }) {
  return (
    <div className="card stack">
      <div className="spread">
        <h3 style={{ textTransform: "capitalize" }}>{order.flavour} pizza</h3>
        <OrderStatusBadge status={order.order_status} />
      </div>

      <div className="row wrap" style={{ gap: 16, fontSize: 14 }}>
        <span className="muted">
          {SIZE_LABELS[order.pizza_size] || order.pizza_size} · Qty {order.quantity}
        </span>
        <span className="price">{formatPrice(order.total_price)}</span>
      </div>

      <span className="muted" style={{ fontSize: 13 }}>
        Placed {new Date(order.placed_at).toLocaleString()}
      </span>
      <span className="muted" style={{ fontSize: 12, fontFamily: "monospace" }}>
        #{String(order.uid).slice(0, 8)}
      </span>

      {children && (
        <>
          <hr className="divider" />
          <div className="row wrap">{children}</div>
        </>
      )}
    </div>
  );
}

export { OrderStatusBadge };
