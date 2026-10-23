/**
 * MrShine Car Wash & Detailing - Global Navigation & Header Utility
 * Dynamically synchronizes user session state, active routes, and responsive mobile nav.
 * Note: Strict compliance with requirement: NO console.log calls.
 */

(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    initFooterYear();
  });

  function initFooterYear() {
    const yearEls = document.querySelectorAll(".current-year, #year");
    const currentYear = new Date().getFullYear();
    yearEls.forEach((el) => {
      el.textContent = currentYear;
    });
  }

  async function initNavigation() {
    // 1. Mobile Menu Toggle
    const mobileToggle = document.getElementById("mobileToggle");
    const navLinks = document.getElementById("navLinks");

    if (mobileToggle && navLinks) {
      mobileToggle.addEventListener("click", () => {
        const isOpen = navLinks.classList.toggle("open");
        mobileToggle.setAttribute("aria-expanded", String(isOpen));
        mobileToggle.setAttribute("aria-label", isOpen ? "Close navigation" : "Open navigation");
        mobileToggle.innerHTML = isOpen ? "&times;" : "&#9776;";
      });

      // Close menu when clicking outside or on a link
      navLinks.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
          navLinks.classList.remove("open");
          mobileToggle.setAttribute("aria-expanded", "false");
          mobileToggle.innerHTML = "&#9776;";
        });
      });
    }

    // 2. Active Page Highlighting
    const currentPath = window.location.pathname.toLowerCase();
    if (navLinks) {
      navLinks.querySelectorAll("a").forEach((link) => {
        const href = (link.getAttribute("href") || "").toLowerCase();
        if (
          href &&
          (currentPath.endsWith(href) ||
            (href !== "/" && href !== "#home" && currentPath.includes(href.replace(".html", ""))))
        ) {
          link.classList.add("active");
        }
      });
    }

    // 3. Dynamic Authentication State Rendering
    const navActions = document.querySelector(".nav-actions");
    if (!navActions || !window.auth) return;

    const token = window.auth.getStoredToken();
    if (!token) {
      // Guest state is maintained by default in HTML markup
      return;
    }

    // User is logged in: fetch profile to populate UI
    const user = await window.auth.getCurrentUser();
    if (!user) return;

    // Add customer or admin specific links to nav if not already present
    if (navLinks) {
      // Ensure "My Requests" exists
      if (!navLinks.querySelector('a[href*="my-requests"]')) {
        const reqLink = document.createElement("a");
        reqLink.href = "/pages/my-requests.html";
        reqLink.textContent = "My Requests";
        if (currentPath.includes("my-requests")) reqLink.classList.add("active");
        navLinks.appendChild(reqLink);
      }

      // If admin, ensure "Admin Portal" link exists
      if (user.role === "admin" && !navLinks.querySelector('a[href*="admin"]')) {
        const adminLink = document.createElement("a");
        adminLink.href = "/pages/admin.html";
        adminLink.textContent = "Admin Portal";
        if (currentPath.includes("admin")) adminLink.classList.add("active");
        navLinks.appendChild(adminLink);
      }
    }

    // Render logged-in user actions in nav-actions
    navActions.innerHTML = "";

    const userMenu = document.createElement("div");
    userMenu.className = "user-menu";

    const badge = document.createElement("div");
    badge.className = "user-badge";

    const avatar = document.createElement("span");
    avatar.className = "user-avatar";
    avatar.textContent = (user.name || "U").charAt(0).toUpperCase();

    const nameText = document.createElement("span");
    nameText.textContent = user.name || user.email;

    badge.appendChild(avatar);
    badge.appendChild(nameText);

    if (user.role === "admin") {
      const roleTag = document.createElement("span");
      roleTag.className = "role-tag role-admin";
      roleTag.textContent = "Admin";
      badge.appendChild(roleTag);
    }

    const logoutBtn = document.createElement("button");
    logoutBtn.type = "button";
    logoutBtn.className = "btn btn-outline btn-sm";
    logoutBtn.textContent = "Logout";
    logoutBtn.addEventListener("click", () => {
      window.auth.logout("/pages/login.html");
    });

    userMenu.appendChild(badge);
    userMenu.appendChild(logoutBtn);
    navActions.appendChild(userMenu);
  }
})();
