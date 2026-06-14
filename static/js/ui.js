export function $(selector, root = document) {
  return root.querySelector(selector);
}

export function $all(selector, root = document) {
  return [...root.querySelectorAll(selector)];
}

export function showToast(message, isError = false) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.toggle("error", isError);
  toast.classList.add("show");
  window.clearTimeout(showToast._timer);
  showToast._timer = window.setTimeout(() => toast.classList.remove("show"), 3200);
}

export function openModal(id) {
  $(`#${id}`).classList.add("open");
}

export function closeModal(id) {
  $(`#${id}`).classList.remove("open");
}

export function confirmAction(message) {
  return window.confirm(message);
}

export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

export function formatPrice(value, currency) {
  if (value == null || value === "") {
    return "—";
  }
  return `${Number(value).toFixed(2)} ${currency || ""}`.trim();
}

export function formatDateTime(value) {
  if (!value) {
    return "—";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return String(value);
  }
  return date.toLocaleString();
}

export function setFieldError(form, fieldName, message) {
  const input = form.querySelector(`[name="${fieldName}"]`);
  const errorEl = form.querySelector(`[data-error-for="${fieldName}"]`);
  if (input) {
    input.classList.toggle("invalid", Boolean(message));
  }
  if (errorEl) {
    errorEl.textContent = message || "";
  }
}

export function applyFormErrors(form, errors) {
  $all("[data-error-for]", form).forEach((el) => {
    const field = el.dataset.errorFor;
    setFieldError(form, field, errors[field] || "");
  });
}

export function clearFormErrors(form) {
  applyFormErrors(form, {});
}
