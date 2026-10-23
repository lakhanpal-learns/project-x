/**
 * MrShine Centralized API Client
 * Manages CSRF tokens, Bearer authentication headers, and uniform error reporting.
 * Explicitly avoids console.log; surfaces notifications to user UI.
 */

let cachedCsrfToken = null;

/**
 * Surface clean on-screen toast / banner notifications without using console.log
 */
function showToast(message, type = "error") {
  let toastContainer = document.getElementById("toastContainer");
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.id = "toastContainer";
    toastContainer.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 99999;
      display: flex;
      flex-direction: column;
      gap: 10px;
      max-width: 380px;
    `;
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement("div");
  const isError = type === "error";
  toast.style.cssText = `
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 0.88rem;
    font-family: 'DM Sans', sans-serif;
    color: ${isError ? "#912018" : "#166534"};
    background: ${isError ? "#fff1f0" : "#f0fdf4"};
    border: 1px solid ${isError ? "#fecaca" : "#bbf7d0"};
    box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    animation: fadeIn 0.3s ease;
  `;
  const toastMessage = document.createElement("span");
  toastMessage.textContent = String(message ?? "");

  const closeButton = document.createElement("button");
  closeButton.type = "button";
  closeButton.setAttribute("aria-label", "Dismiss notification");
  closeButton.textContent = "×";
  closeButton.style.cssText = "background:none;border:none;cursor:pointer;font-size:1.1rem;color:inherit;";
  closeButton.addEventListener("click", () => toast.remove());

  toast.append(toastMessage, closeButton);
  toastContainer.appendChild(toast);
  setTimeout(() => {
    if (toast.parentElement) toast.remove();
  }, 5000);
}

/**
 * Fetch and cache CSRF token from backend
 */
async function getCsrfToken() {
  if (cachedCsrfToken) return cachedCsrfToken;
  try {
    const res = await fetch("/api/v1/auth/csrf-token");
    if (res.ok) {
      const data = await res.json();
      cachedCsrfToken = data.csrf_token;
      return cachedCsrfToken;
    }
  } catch (err) {
    // Graceful fallback
  }
  return "";
}

/**
 * Unified API Request Handler
 */
async function apiRequest(endpoint, options = {}) {
  const token =
    localStorage.getItem("mrshine_access_token") ||
    sessionStorage.getItem("mrshine_access_token");

  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const method = (options.method || "GET").toUpperCase();
  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const csrf = await getCsrfToken();
    if (csrf) {
      headers["X-CSRF-Token"] = csrf;
    }
  }

  try {
    const response = await fetch(endpoint, {
      ...options,
      headers,
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const errorMessage =
        data.detail || data.message || "An error occurred with your request.";
      throw new Error(errorMessage);
    }

    return data;
  } catch (error) {
    showToast(error.message, "error");
    throw error;
  }
}

/**
 * Show an inline alert banner in the UI (not console.log)
 * @param {HTMLElement} el - The banner element
 * @param {string} message - Message text (empty string = hide)
 * @param {string} type - "success" | "error" | "warning"
 */
function showAlert(el, message, type = "error") {
  if (!el) return;
  if (!message) {
    el.style.display = "none";
    el.textContent = "";
    return;
  }
  el.style.display = "block";
  el.textContent = message;
  const colours = {
    error: { bg: "#fff1f0", color: "#912018", border: "#fecaca" },
    success: { bg: "#f0fdf4", color: "#166534", border: "#bbf7d0" },
    warning: { bg: "#fffbeb", color: "#92400e", border: "#fde68a" },
  };
  const c = colours[type] || colours.error;
  el.style.background = c.bg;
  el.style.color = c.color;
  el.style.border = `1px solid ${c.border}`;
  el.style.borderRadius = "8px";
  el.style.padding = "12px 14px";
  el.style.fontSize = "0.88rem";
}

// Make showAlert and showToast globally available
window.showAlert = showAlert;
window.showToast = showToast;

// Named API Helper Functions
const Api = {
  getCsrfToken,
  showToast,
  getServices: () => apiRequest("/api/v1/services"),
  createRequest: (data) => apiRequest("/api/v1/requests", { method: "POST", body: JSON.stringify(data) }),
  getMyRequests: () => apiRequest("/api/v1/requests/my"),
  submitFeedback: (data) => apiRequest("/api/v1/feedback", { method: "POST", body: JSON.stringify(data) }),
  getAdminStats: () => apiRequest("/api/v1/admin/stats"),
  getAdminRequests: () => apiRequest("/api/v1/admin/requests"),
  updateRequestStatus: (id, status, admin_notes = null) =>
    apiRequest(`/api/v1/admin/requests/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status, admin_notes }),
    }),
  createService: (data) => apiRequest("/api/v1/admin/services", { method: "POST", body: JSON.stringify(data) }),
  updateService: (id, data) => apiRequest(`/api/v1/admin/services/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteService: (id) => apiRequest(`/api/v1/admin/services/${id}`, { method: "DELETE" }),
  getMe: () => apiRequest("/api/v1/auth/me"),
  updateProfile: (data) => apiRequest("/api/v1/auth/profile", { method: "PUT", body: JSON.stringify(data) }),
};
