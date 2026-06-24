// Sidebar toggle (mobile)
document.addEventListener('click', e => {
  if (e.target.closest('#sidebarToggle')) {
    document.querySelector('.sidebar')?.classList.toggle('open');
  }
});

// Auto-dismiss toasts after 5s
setTimeout(() => {
  document.querySelectorAll('.toast.show').forEach(t => {
    bootstrap.Toast.getOrCreateInstance(t).hide();
  });
}, 5000);

// Highlight active nav link
const path = location.pathname;
document.querySelectorAll('.sidebar .nav-link').forEach(a => {
  if (a.getAttribute('href') && path.startsWith(a.getAttribute('href')) && a.getAttribute('href') !== '/') {
    a.classList.add('active');
  }
});
