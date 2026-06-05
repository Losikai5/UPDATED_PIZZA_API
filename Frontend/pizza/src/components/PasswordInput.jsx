import { useState } from "react";

// Eye / eye-off glyph, stroke-based to match PizzaMark and inherit currentColor.
function EyeIcon({ off }) {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {off ? (
        <>
          <path d="M9.9 4.24A9.1 9.1 0 0 1 12 4c7 0 10 8 10 8a18.5 18.5 0 0 1-2.16 3.19M6.6 6.6A18.5 18.5 0 0 0 2 12s3 8 10 8a9.1 9.1 0 0 0 5.4-1.6" />
          <path d="M14.12 14.12a3 3 0 1 1-4.24-4.24" />
          <line x1="2" y1="2" x2="22" y2="22" />
        </>
      ) : (
        <>
          <path d="M2 12s3-8 10-8 10 8 10 8-3 8-10 8-10-8-10-8Z" />
          <circle cx="12" cy="12" r="3" />
        </>
      )}
    </svg>
  );
}

// Password field that adds a show/hide toggle. Spreads all other props
// (id, name, value, onChange, onBlur, aria-*, required, autoComplete) onto the
// underlying input so it behaves like a normal controlled input.
export default function PasswordInput({ invalid, ...props }) {
  const [show, setShow] = useState(false);

  return (
    <div className="input-affix">
      <input
        {...props}
        type={show ? "text" : "password"}
        className={`input${invalid ? " is-invalid" : ""}`}
      />
      <button
        type="button"
        className="affix-btn"
        onClick={() => setShow((s) => !s)}
        aria-label={show ? "Hide password" : "Show password"}
        aria-pressed={show}
      >
        <EyeIcon off={show} />
      </button>
    </div>
  );
}
