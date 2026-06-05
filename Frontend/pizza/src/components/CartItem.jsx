import { formatPrice, SIZE_LABELS } from "../utils/format";

export default function CartItem({ item, onUpdateQty, onRemove, busy }) {
  return (
    <div className="card spread" style={{ gap: 16 }}>
      <div className="stack" style={{ gap: 4, alignItems: "flex-start" }}>
        <h3>{item.menu_item_name}</h3>
        <span className="muted" style={{ fontSize: 14 }}>
          {SIZE_LABELS[item.pizza_size] || item.pizza_size} · {formatPrice(item.unit_price)} each
        </span>
      </div>

      <div className="row">
        <div className="row" style={{ gap: 6 }}>
          <button
            className="btn btn-outline btn-sm"
            onClick={() => onUpdateQty(item.uid, item.quantity - 1)}
            disabled={busy || item.quantity <= 1}
            aria-label="Decrease quantity"
          >
            −
          </button>
          <span style={{ minWidth: 24, textAlign: "center", fontWeight: 600 }}>
            {item.quantity}
          </span>
          <button
            className="btn btn-outline btn-sm"
            onClick={() => onUpdateQty(item.uid, item.quantity + 1)}
            disabled={busy}
            aria-label="Increase quantity"
          >
            +
          </button>
        </div>

        <span className="price" style={{ minWidth: 110, textAlign: "right" }}>
          {formatPrice(item.subtotal)}
        </span>

        <button
          className="btn btn-danger btn-sm"
          onClick={() => onRemove(item.uid)}
          disabled={busy}
        >
          Remove
        </button>
      </div>
    </div>
  );
}
