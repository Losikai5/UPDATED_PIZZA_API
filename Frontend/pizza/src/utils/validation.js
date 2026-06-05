// Lightweight form validation helpers shared by the auth forms.

export const isEmail = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test((v || "").trim());

// `rules` is a map of field name -> (form) => errorMessage | "".
// Returns an object containing only the fields that currently have errors.
export function validateAll(form, rules) {
  const errors = {};
  for (const name of Object.keys(rules)) {
    const message = rules[name](form);
    if (message) errors[name] = message;
  }
  return errors;
}
