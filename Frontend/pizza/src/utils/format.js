// Shared display helpers used across menu, cart and order views.

export const SIZE_LABELS = {
  small: "Small",
  medium: "Medium",
  large: "Large",
  extra_large: "Extra Large",
};

export function formatPrice(value) {
  return `UGX ${Number(value).toLocaleString()}`;
}
