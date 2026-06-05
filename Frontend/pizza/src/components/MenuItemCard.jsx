import { useState } from "react";
import { formatPrice, SIZE_LABELS } from "../utils/format";

export default function MenuItemCard({ item, onAdd, adding }) {
  const sizes = item.sizes || [];
  const [sizeUid, setSizeUid] = useState(sizes[0]?.uid || "");

  const selectedSize = sizes.find((s) => s.uid === sizeUid) || sizes[0];

  function handleAdd() {
    if (!selectedSize || !onAdd) return;
    onAdd(item, selectedSize);
  }

  return (
    <div className="card stack">
      <div className="spread">
        <h3>{item.name}</h3>
        {item.is_available ? (
          <span className="badge badge-green">Available</span>
        ) : (
          <span className="badge badge-gray">Sold out</span>
        )}
      </div>

      <span className="eyebrow" style={{ alignSelf: "flex-start" }}>
        {item.flavour}
      </span>

      <p className="muted" style={{ textAlign: "left", fontSize: 14 }}>
        {item.description}
      </p>

      {sizes.length > 0 ? (
        <>
          <div className="field">
            <label htmlFor={`size-${item.uid}`}>Size</label>
            <select
              id={`size-${item.uid}`}
              className="select"
              value={sizeUid}
              onChange={(e) => setSizeUid(e.target.value)}
            >
              {sizes.map((s) => (
                <option key={s.uid} value={s.uid}>
                  {SIZE_LABELS[s.pizza_size] || s.pizza_size} — {formatPrice(s.price)}
                </option>
              ))}
            </select>
          </div>

          <div className="spread">
            <span className="price">{selectedSize && formatPrice(selectedSize.price)}</span>
            {onAdd && (
              <button
                className="btn btn-primary btn-sm"
                onClick={handleAdd}
                disabled={!item.is_available || adding}
              >
                {adding ? "Adding…" : "Add to cart"}
              </button>
            )}
          </div>
        </>
      ) : (
        <p className="muted" style={{ fontSize: 14 }}>No sizes configured.</p>
      )}
    </div>
  );
}
