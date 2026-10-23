/**
 * MrShine Car Wash & Detailing - Global Enhancements
 * Note: Strict compliance with requirement: NO console.log calls.
 */

(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", () => {
    // Gallery carousel support if present on the page
    const galleryTrack = document.getElementById("galleryTrack");
    const galleryPrev = document.getElementById("galleryPrev");
    const galleryNext = document.getElementById("galleryNext");

    if (galleryTrack && galleryPrev && galleryNext) {
      galleryPrev.addEventListener("click", () => {
        galleryTrack.scrollBy({ left: -galleryTrack.clientWidth, behavior: "smooth" });
      });
      galleryNext.addEventListener("click", () => {
        galleryTrack.scrollBy({ left: galleryTrack.clientWidth, behavior: "smooth" });
      });
    }

    // Auto-dismiss in-page alert banners after duration if configured
    document.querySelectorAll(".alert-banner[data-autohide]").forEach((banner) => {
      const ms = parseInt(banner.getAttribute("data-autohide"), 10) || 5000;
      window.setTimeout(() => {
        banner.classList.remove("show");
        banner.style.display = "none";
      }, ms);
    });
  });
})();
