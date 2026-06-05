// Crafted SVG pizza mark — replaces the font-dependent 🍕 emoji used as the
// brand seal. Inherits `currentColor` so it themes with its container (e.g.
// the tomato/paper inversions of .seal). Decorative by default; pass a `title`
// to expose it to assistive tech.
export default function PizzaMark({ size = 24, title, className }) {
  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      role={title ? "img" : "presentation"}
      aria-hidden={title ? undefined : "true"}
      aria-label={title}
    >
      {title && <title>{title}</title>}
      {/* slice outline */}
      <path d="M12 2.5 21 19a1.4 1.4 0 0 1-1.6 1.95L4.3 17.4A1.4 1.4 0 0 1 3.4 15L12 2.5Z" />
      {/* crust line */}
      <path d="M5.1 13.2C8.6 11.6 13 12.2 16.8 15" />
      {/* pepperoni / toppings */}
      <circle cx="11.4" cy="8.6" r="1.05" fill="currentColor" stroke="none" />
      <circle cx="9.2" cy="12.6" r="1.05" fill="currentColor" stroke="none" />
      <circle cx="13.6" cy="13.1" r="1.05" fill="currentColor" stroke="none" />
    </svg>
  );
}
