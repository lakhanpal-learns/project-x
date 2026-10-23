/**
 * MrShine Authentication, Session Guards & User Profile System
 */

const Auth = {
  getToken() {
    return (
      localStorage.getItem("mrshine_access_token") ||
      sessionStorage.getItem("mrshine_access_token")
    );
  },

  getUser() {
    const raw =
      localStorage.getItem("mrshine_user") ||
      sessionStorage.getItem("mrshine_user");
    try {
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },

  setSession(token, user, remember = false) {
    const storage = remember ? localStorage : sessionStorage;
    storage.setItem("mrshine_access_token", token);
    storage.setItem("mrshine_user", JSON.stringify(user));
  },

  clearSession() {
    localStorage.removeItem("mrshine_access_token");
    localStorage.removeItem("mrshine_user");
    sessionStorage.removeItem("mrshine_access_token");
    sessionStorage.removeItem("mrshine_user");
  },

  logout() {
    this.clearSession();
    window.location.href = "/pages/login.html";
  },

  requireAuth(redirectUrl = null) {
    const token = this.getToken();
    if (!token) {
      const target = redirectUrl || window.location.pathname;
      window.location.href = `/pages/login.html?next=${encodeURIComponent(target)}`;
      return false;
    }
    return true;
  },

  requireAdmin() {
    if (!this.requireAuth()) return false;
    const user = this.getUser();
    if (!user || user.role !== "admin") {
      window.location.href = "/pages/my-requests.html";
      return false;
    }
    return true;
  },

  redirectIfAuthenticated() {
    const token = this.getToken();
    const path = window.location.pathname.toLowerCase();
    if (token && (path.endsWith("login.html") || path.endsWith("register.html"))) {
      const user = this.getUser();
      if (user && user.role === "admin") {
        window.location.replace("/pages/admin.html");
      } else {
        window.location.replace("/pages/my-requests.html");
      }
    }
  },

  openProfileModal() {
    let modal = document.getElementById("profileModal");
    if (!modal) {
      modal = document.createElement("div");
      modal.id = "profileModal";
      modal.style.cssText = `
        position: fixed;
        inset: 0;
        z-index: 10000;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(4px);
        animation: fadeIn 0.2s ease;
      `;
      document.body.appendChild(modal);
    }

    const user = this.getUser() || {};

    modal.innerHTML = `
      <div style="background: white; border-radius: 14px; width: min(440px, 92%); padding: 32px; box-shadow: 0 20px 60px rgba(0,0,0,0.15); position: relative; font-family: 'DM Sans', sans-serif;">
        <button id="closeProfileModal" style="position: absolute; right: 18px; top: 16px; background: none; border: none; font-size: 1.4rem; cursor: pointer; color: #888;">&times;</button>
        <div style="text-align: center; margin-bottom: 20px;">
          <div style="width: 56px; height: 56px; border-radius: 50%; background: #111; color: white; display: grid; place-items: center; font-size: 1.4rem; font-weight: 800; margin: 0 auto 10px;">
            ${(user.name || "U")[0].toUpperCase()}
          </div>
          <h2 style="font-family: 'Manrope', sans-serif; font-size: 1.3rem; margin: 0 0 4px;">${user.name || "My Profile"}</h2>
          <span style="font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em; background: ${user.role === 'admin' ? '#fee2e2' : '#e0f2fe'}; color: ${user.role === 'admin' ? '#991b1b' : '#0369a1'}; padding: 3px 10px; border-radius: 20px; font-weight: 700;">
            ${user.role || 'customer'}
          </span>
        </div>

        <div id="profileAlert" style="display:none; padding: 10px; border-radius: 6px; font-size: 0.85rem; margin-bottom: 14px;"></div>

        <form id="profileForm">
          <div style="margin-bottom: 14px;">
            <label style="display:block; font-size:0.8rem; font-weight:700; margin-bottom:5px;">Email Address</label>
            <input type="text" value="${user.email || ''}" disabled style="width:100%; height:40px; border:1px solid #ddd; border-radius:6px; padding:0 12px; background:#f5f5f5; color:#777; font-size:0.9rem;">
          </div>
          <div style="margin-bottom: 14px;">
            <label style="display:block; font-size:0.8rem; font-weight:700; margin-bottom:5px;">Full Name</label>
            <input id="profName" type="text" value="${user.name || ''}" required style="width:100%; height:40px; border:1px solid #ddd; border-radius:6px; padding:0 12px; font-size:0.9rem;">
          </div>
          <div style="margin-bottom: 20px;">
            <label style="display:block; font-size:0.8rem; font-weight:700; margin-bottom:5px;">Phone Number</label>
            <input id="profPhone" type="tel" value="${user.phone || ''}" placeholder="e.g. +1 (555) 019-2834" style="width:100%; height:40px; border:1px solid #ddd; border-radius:6px; padding:0 12px; font-size:0.9rem;">
          </div>
          <button type="submit" id="saveProfBtn" style="width:100%; height:42px; background:#111; color:white; border:none; border-radius:6px; font-weight:700; cursor:pointer;">Save Changes</button>
        </form>

        <div style="margin-top: 18px; pt-3; border-top: 1px solid #eee; text-align: center;">
          <button id="modalLogoutBtn" style="background:none; border:none; color:#b42318; font-size:0.86rem; font-weight:700; cursor:pointer; padding:6px 12px;">Sign Out</button>
        </div>
      </div>
    `;

    modal.style.display = "flex";

    document.getElementById("closeProfileModal").onclick = () => { modal.style.display = "none"; };
    modal.onclick = (e) => { if (e.target === modal) modal.style.display = "none"; };
    document.getElementById("modalLogoutBtn").onclick = () => this.logout();

    document.getElementById("profileForm").onsubmit = async (e) => {
      e.preventDefault();
      const saveBtn = document.getElementById("saveProfBtn");
      const alertBox = document.getElementById("profileAlert");
      saveBtn.disabled = true;
      saveBtn.textContent = "Saving…";

      try {
        const updated = await Api.updateProfile({
          name: document.getElementById("profName").value.trim(),
          phone: document.getElementById("profPhone").value.trim() || null,
        });

        const cur = this.getUser() || {};
        cur.name = updated.name;
        cur.phone = updated.phone;
        const storage = localStorage.getItem("mrshine_user") ? localStorage : sessionStorage;
        storage.setItem("mrshine_user", JSON.stringify(cur));

        alertBox.style.display = "block";
        alertBox.style.background = "#eefbf2";
        alertBox.style.color = "#166534";
        alertBox.textContent = "Profile updated successfully!";
        this.updateHeaderUI();
        setTimeout(() => { modal.style.display = "none"; }, 1000);
      } catch (err) {
        alertBox.style.display = "block";
        alertBox.style.background = "#fff1f0";
        alertBox.style.color = "#991b1b";
        alertBox.textContent = err.message || "Failed to update profile.";
      } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = "Save Changes";
      }
    };
  },

  updateHeaderUI() {
    const user = this.getUser();
    const token = this.getToken();
    const authContainer = document.getElementById("headerAuthActions");
    if (!authContainer) return;

    if (token && user) {
      const isAdmin = user.role === "admin";
      authContainer.innerHTML = `
        <button id="headerProfileBtn" class="btn btn-outline" style="min-height:36px;padding:0 12px;font-size:0.82rem;display:inline-flex;align-items:center;gap:6px;">
          <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#10b981;"></span>
          ${user.name.split(" ")[0]}
        </button>
        ${
          isAdmin
            ? '<a href="/pages/admin.html" class="btn btn-outline" style="min-height:36px;padding:0 14px;font-size:0.82rem;">Admin Panel</a>'
            : '<a href="/pages/my-requests.html" class="btn btn-outline" style="min-height:36px;padding:0 14px;font-size:0.82rem;">Track Requests</a>'
        }
        <button id="logoutBtn" class="btn btn-outline" style="min-height:36px;padding:0 12px;font-size:0.82rem;">Logout</button>
      `;
      document.getElementById("logoutBtn").addEventListener("click", () => this.logout());
      document.getElementById("headerProfileBtn").addEventListener("click", () => this.openProfileModal());
    } else {
      authContainer.innerHTML = `
        <a href="/login.html" class="btn btn-outline" style="min-height:36px;padding:0 14px;font-size:0.82rem;">Sign in</a>
        <a href="/register.html" class="btn" style="min-height:36px;padding:0 14px;font-size:0.82rem;">Register</a>
      `;
    }
  },
};

document.addEventListener("DOMContentLoaded", () => {
  // If user is already signed in, prevent visiting login or register pages
  Auth.redirectIfAuthenticated();
  Auth.updateHeaderUI();
});

// Global aliases for compatibility with navigation.js and inline scripts
window.auth = {
  getStoredToken: () => Auth.getToken(),
  getCurrentUser: async () => {
    // Try to get user from storage first (fast path)
    const stored = Auth.getUser();
    if (stored) return stored;
    // If token exists but no user data, fetch from API
    const token = Auth.getToken();
    if (!token) return null;
    try {
      const data = await fetch("/api/v1/auth/me", {
        headers: { "Authorization": `Bearer ${token}` }
      }).then(r => r.ok ? r.json() : null);
      if (data) {
        const storage = localStorage.getItem("mrshine_access_token") ? localStorage : sessionStorage;
        storage.setItem("mrshine_user", JSON.stringify(data));
        return data;
      }
    } catch {}
    return null;
  },
  logout: (redirectUrl) => {
    Auth.clearSession();
    window.location.href = redirectUrl || "/pages/login.html";
  },
};

// window.api shim for request-service.html inline script compatibility
window.api = {
  get: (path) => fetch(`/api/v1${path}`).then(r => r.json()),
  post: async (path, body) => {
    const token = Auth.getToken();
    const csrf = await (typeof getCsrfToken !== "undefined" ? getCsrfToken() : fetch("/api/v1/auth/csrf-token").then(r => r.json()).then(d => d.csrf_token).catch(() => ""));
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    if (csrf) headers["X-CSRF-Token"] = csrf;
    const resp = await fetch(`/api/v1${path}`, { method: "POST", headers, body: JSON.stringify(body) });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) throw new Error(data.detail || data.message || "Request failed");
    return data;
  }
};
