export default function LoadingSpinner({ label }) {
  return (
    <div className="spinner-wrap" role="status" aria-live="polite">
      <div className="spinner" />
      {label && <span className="muted" style={{ marginLeft: 12 }}>{label}</span>}
    </div>
  );
}
