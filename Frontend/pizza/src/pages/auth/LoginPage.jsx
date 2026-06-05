import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login as loginRequest } from "../../services/auth";
import { useAuth } from "../../context/AuthContext";
import PizzaMark from "../../components/PizzaMark";
import PasswordInput from "../../components/PasswordInput";
import FieldError from "../../components/FieldError";
import { isEmail, validateAll } from "../../utils/validation";

const RULES = {
  email: (f) =>
    !f.email.trim()
      ? "Email is required."
      : !isEmail(f.email)
        ? "Enter a valid email address."
        : "",
  password: (f) => (!f.password ? "Password is required." : ""),
};

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const isInvalid = (n) => Boolean(touched[n] && errors[n]);

  // Shared props applied to every input: keeps controlled state, blur
  // validation, and aria wiring consistent.
  const fieldProps = (n) => ({
    id: n,
    name: n,
    value: form[n],
    onChange: update,
    onBlur: handleBlur,
    "aria-invalid": isInvalid(n) || undefined,
    "aria-describedby": isInvalid(n) ? `${n}-error` : undefined,
  });

  function update(e) {
    const { name, value } = e.target;
    const next = { ...form, [name]: value };
    setForm(next);
    // Once a field has been blurred, re-validate live so errors clear as the
    // user fixes them (validate-on-blur, then correct-on-change).
    if (touched[name]) {
      setErrors((prev) => ({ ...prev, [name]: RULES[name](next) }));
    }
  }

  function handleBlur(e) {
    const { name } = e.target;
    setTouched((prev) => ({ ...prev, [name]: true }));
    setErrors((prev) => ({ ...prev, [name]: RULES[name](form) }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const found = validateAll(form, RULES);
    setErrors(found);
    setTouched({ email: true, password: true });
    const firstInvalid = Object.keys(RULES).find((n) => found[n]);
    if (firstInvalid) {
      document.getElementById(firstInvalid)?.focus();
      return;
    }

    setLoading(true);
    try {
      const data = await loginRequest(form);
      // Sync the auth context (and re-store tokens) so the UI reflects the session.
      login(data.access_token, data.refresh_token);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to log in. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-split">
        <aside className="auth-brandpane">
          <div className="row" style={{ gap: 14, position: "relative", zIndex: 1 }}>
            <span className="seal"><PizzaMark size={34} /></span>
            <span className="eyebrow" style={{ color: "var(--paper)" }}>Losika · Est. 2026</span>
          </div>
          <div style={{ position: "relative", zIndex: 1 }}>
            <h1 className="auth-wordmark">Hot.<br />Fresh.<br /><em>Yours.</em></h1>
            <p className="auth-tagline" style={{ marginTop: 18 }}>
              Wood-fired, hand-tossed pizza — ordered in seconds, delivered in thirty minutes.
            </p>
          </div>
          <p style={{ position: "relative", zIndex: 1, fontSize: 13, opacity: 0.8 }}>
            Made fresh, every single day.
          </p>
        </aside>

        <div className="auth-formpane">
          <div className="auth-card stack">
            <div className="stack" style={{ gap: 6 }}>
              <span className="eyebrow">Welcome back</span>
              <h1>Log in</h1>
              <p className="muted">Sign in to order your favourite pizza.</p>
            </div>

            {error && <div className="alert alert-error">{error}</div>}

            <form className="stack" onSubmit={handleSubmit} noValidate>
          <div className="field">
            <label htmlFor="email">Email<span className="req" aria-hidden="true">*</span></label>
            <input
              {...fieldProps("email")} type="email"
              className={`input${isInvalid("email") ? " is-invalid" : ""}`}
              autoComplete="email" placeholder="you@example.com"
            />
            <FieldError name="email" errors={errors} touched={touched} />
          </div>
          <div className="field">
            <label htmlFor="password">Password<span className="req" aria-hidden="true">*</span></label>
            <PasswordInput
              {...fieldProps("password")} invalid={isInvalid("password")}
              autoComplete="current-password" placeholder="••••••••"
            />
            <FieldError name="password" errors={errors} touched={touched} />
          </div>
          <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
            {loading ? "Logging in…" : "Log in"}
          </button>
        </form>

            <p className="muted center" style={{ fontSize: 14 }}>
              New here? <Link to="/signup">Create an account</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
