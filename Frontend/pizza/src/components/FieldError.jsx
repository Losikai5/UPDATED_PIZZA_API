// Renders a field-level validation message once the field has been touched.
// Pairs with `aria-describedby={`${name}-error`}` on the input so screen
// readers announce the error.
export default function FieldError({ name, errors, touched }) {
  if (!touched[name] || !errors[name]) return null;
  return (
    <span className="field-error" id={`${name}-error`} role="alert">
      {errors[name]}
    </span>
  );
}
