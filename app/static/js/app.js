/* ==========================================================================
   StockPilot – app.js
   Handles: sidebar off-canvas toggle, overlay, active nav, toast dismiss,
            chart responsiveness, mobile UX polish.
   No backend logic is touched here.
   ========================================================================== */

(function () {
  'use strict';

  // ── Sidebar off-canvas + overlay ────────────────────────────────────────
  const sidebar  = document.querySelector('.sidebar');
  const overlay  = document.querySelector('.sidebar-overlay');
  const toggleBtn = document.getElementById('sidebarToggle');

  function openSidebar() {
    if (!sidebar) return;
    sidebar.classList.add('open');
    if (overlay) overlay.classList.add('show');
    // Prevent body scroll when sidebar is open on mobile
    document.body.style.overflow = 'hidden';
    // Accessibility: mark sidebar as expanded
    if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'true');
  }

  function closeSidebar() {
    if (!sidebar) return;
    sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('show');
    document.body.style.overflow = '';
    if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'false');
  }

  function toggleSidebar() {
    if (sidebar && sidebar.classList.contains('open')) {
      closeSidebar();
    } else {
      openSidebar();
    }
  }

  // Hamburger button
  if (toggleBtn) {
    toggleBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      toggleSidebar();
    });
  }

  // Clicking the dark overlay closes the sidebar
  if (overlay) {
    overlay.addEventListener('click', closeSidebar);
  }

  // Swipe-left on the sidebar to close (touch support)
  if (sidebar) {
    let touchStartX = 0;
    sidebar.addEventListener('touchstart', function (e) {
      touchStartX = e.changedTouches[0].clientX;
    }, { passive: true });
    sidebar.addEventListener('touchend', function (e) {
      const dx = e.changedTouches[0].clientX - touchStartX;
      // Swipe left ≥ 50px → close
      if (dx < -50) closeSidebar();
    }, { passive: true });
  }

  // Close sidebar when viewport grows back to desktop width
  // (e.g. rotating from portrait to landscape)
  window.addEventListener('resize', function () {
    if (window.innerWidth >= 768) {
      closeSidebar();
    }
  });

  // Close sidebar when a nav link is tapped on mobile
  // This makes navigation feel instant rather than leaving the overlay open
  if (sidebar) {
    sidebar.querySelectorAll('.nav-link').forEach(function (link) {
      link.addEventListener('click', function () {
        if (window.innerWidth < 768) closeSidebar();
      });
    });
  }

  // ── Active nav link highlight ────────────────────────────────────────────
  const currentPath = location.pathname;
  if (sidebar) {
    sidebar.querySelectorAll('.nav-link').forEach(function (a) {
      const href = a.getAttribute('href');
      if (!href || href === '/') return;
      if (currentPath.startsWith(href)) {
        a.classList.add('active');
      }
    });
  }

  // ── Auto-dismiss flash toasts after 5 s ──────────────────────────────────
  setTimeout(function () {
    document.querySelectorAll('.toast.show').forEach(function (el) {
      const t = bootstrap.Toast.getOrCreateInstance(el);
      t.hide();
    });
  }, 5000);

  // ── Chart.js global defaults (responsive) ────────────────────────────────
  // Chart.js is responsive by default; we set sensible global options here
  // so every chart created in page-specific scripts inherits them.
  if (typeof Chart !== 'undefined') {
    Chart.defaults.responsive          = true;
    Chart.defaults.maintainAspectRatio = true;
    // Slightly smaller font on mobile
    Chart.defaults.font.size = window.innerWidth < 600 ? 11 : 13;
    // Muted grid lines
    Chart.defaults.scale.grid = { color: 'rgba(0,0,0,.06)' };
  }

  // ── Prevent double-submit on forms ───────────────────────────────────────
  document.querySelectorAll('form').forEach(function (form) {
    form.addEventListener('submit', function () {
      const btn = form.querySelector('[type="submit"]');
      if (btn && !btn.dataset.noDisable) {
        btn.disabled = true;
        // Re-enable after 6 s in case of validation error / server error
        setTimeout(function () { btn.disabled = false; }, 6000);
      }
    });
  });

  // ── Mobile: auto-focus search inputs ─────────────────────────────────────
  // On the sale/restock search pages the search input benefits from autofocus
  // but autofocus can be annoying on desktop (it fires even for tabbed users).
  // We only do it if the user is on a touch device.
  const isTouchDevice = ('ontouchstart' in window || navigator.maxTouchPoints > 0);
  if (!isTouchDevice) {
    // Remove autofocus attribute on non-touch devices to avoid confusion
    document.querySelectorAll('[autofocus]').forEach(function (el) {
      // Keep autofocus on login page only
      if (!el.closest('.login-card')) el.removeAttribute('autofocus');
    });
  }

})();
