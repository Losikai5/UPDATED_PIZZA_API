import { useState } from "react";
import { Link } from "react-router-dom";
import { signup as signupRequest } from "../../services/auth";
import PizzaMark from "../../components/PizzaMark";
import PasswordInput from "../../components/PasswordInput";
import FieldError from "../../components/FieldError";
import { isEmail, validateAll } from "../../utils/validation";

const EMPTY = {
  username: "",
  first_name: "",
  last_name: "",
  email: "",
  password: "",
};

const RULES = {
  first_name: (f) => (f.first_name.trim() ? "" : "First name is required."),
  last_name: (f) => (f.last_name.trim() ? "" : "Last name is required."),
  username: (f) =>
    f.username.trim().length >= 3 ? "" : "Username must be at least 3 characters.",
  email: (f) =>
    !f.email.trim()
      ? "Email is required."
      : !isEmail(f.email)
        ? "Enter a valid email address."
        : "",
  password: (f) =>
    f.password.length >= 6 ? "" : "Password must be at least 6 characters.",
};

export default function SignupPage() {
  const [form, setForm] = useState(EMPTY);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const isInvalid = (n) => Boolean(touched[n] && errors[n]);

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
    setSuccess("");

    const found = validateAll(form, RULES);
    setErrors(found);
    setTouched({
      first_name: true, last_name: true, username: true, email: true, password: true,
    });
    const firstInvalid = Object.keys(RULES).find((n) => found[n]);
    if (firstInvalid) {
      document.getElementById(firstInvalid)?.focus();
      return;
    }

    setLoading(true);
    try {
      const data = await signupRequest(form);
      setSuccess(
        data.message ||
          "Account created! Check your email to verify your account before logging in."
      );
      setForm(EMPTY);
      setTouched({});
      setErrors({});
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        Array.isArray(detail)
          ? detail.map((d) => d.msg).join(", ")
          : detail || "Could not create account. Please try again."
      );
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
            <h1 className="auth-wordmark">Join<br />the<br /><em>table.</em></h1>
            <p className="auth-tagline" style={{ marginTop: 18 }}>
              Create an account and get your first wood-fired pie on the way in minutes.
            </p>
          </div>
          <p style={{ position: "relative", zIndex: 1, fontSize: 13, opacity: 0.8 }}>
            No queues. Just pizza.
          </p>
        </aside>

        <div className="auth-formpane">
          <div className="auth-card stack">
            <div className="stack" style={{ gap: 6 }}>
              <span className="eyebrow">Get started</span>
              <h1>Create account</h1>
              <p className="muted">Sign up to start ordering.</p>
            </div>

            {error && <div className="alert alert-error">{error}</div>}
            {success && <div className="alert alert-success">{success}</div>}

            <form className="stack" onSubmit={handleSubmit} noValidate>
          <div className="row" style={{ gap: 10, alignItems: "flex-start" }}>
            <div className="field" style={{ flex: 1 }}>
              <label htmlFor="first_name">First name<span className="req" aria-hidden="true">*</span></label>
              <input {...fieldProps("first_name")}
                className={`input${isInvalid("first_name") ? " is-invalid" : ""}`}
                autoComplete="given-name" />
              <FieldError name="first_name" errors={errors} touched={touched} />
            </div>
            <div className="field" style={{ flex: 1 }}>
              <label htmlFor="last_name">Last name<span className="req" aria-hidden="true">*</span></label>
              <input {...fieldProps("last_name")}
                className={`input${isInvalid("last_name") ? " is-invalid" : ""}`}
                autoComplete="family-name" />
              <FieldError name="last_name" errors={errors} touched={touched} />
            </div>
          </div>
          <div className="field">
            <label htmlFor="username">Username<span className="req" aria-hidden="true">*</span></label>
            <input {...fieldProps("username")}
              className={`input${isInvalid("username") ? " is-invalid" : ""}`}
              autoComplete="username" />
            <FieldError name="username" errors={errors} touched={touched} />
          </div>
          <div className="field">
            <label htmlFor="email">Email<span className="req" aria-hidden="true">*</span></label>
            <input {...fieldProps("email")} type="email"
              className={`input${isInvalid("email") ? " is-invalid" : ""}`}
              autoComplete="email" />
            <FieldError name="email" errors={errors} touched={touched} />
          </div>
          <div className="field">
            <label htmlFor="password">Password<span className="req" aria-hidden="true">*</span></label>
            <PasswordInput {...fieldProps("password")} invalid={isInvalid("password")}
              autoComplete="new-password" />
            {isInvalid("password") ? (
              <FieldError name="password" errors={errors} touched={touched} />
            ) : (
              <span className="field-hint">At least 6 characters.</span>
            )}
          </div>
          <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
            {loading ? "Creating account…" : "Sign up"}
          </button>
        </form>

            <p className="muted center" style={{ fontSize: 14 }}>
              Already have an account? <Link to="/login">Log in</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
