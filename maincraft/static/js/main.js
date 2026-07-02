document.addEventListener('DOMContentLoaded', () => {

  const navItems = document.querySelectorAll('.nav-item');

navItems.forEach(item => {
  item.addEventListener('click', () => {
    sidebar.classList.add('hidden');
    localStorage.setItem('sidebarHidden', 'true');
  });
});
  // Sidebar Toggle
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('sidebarToggle');
  
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('hidden');
      // Save state to localStorage
      localStorage.setItem('sidebarHidden', sidebar.classList.contains('hidden'));
     
     
      
    });

    // Restore state
    if (localStorage.getItem('sidebarHidden') === 'true') {
    sidebar.classList.add('hidden');
}
  }

  // Theme Toggle
  const themeToggle = document.getElementById('themeToggle');
  const body = document.body;

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      body.classList.toggle('dark-mode');
      const isDark = body.classList.contains('dark-mode');
      localStorage.setItem('darkMode', isDark);
      
      // Update icon
      themeToggle.innerHTML = isDark ? '☀️' : '🌙';
    });

    // Restore state
    if (localStorage.getItem('darkMode') === 'true') {
      body.classList.add('dark-mode');
      themeToggle.innerHTML = '☀️';
    }
  }

  // Auto-dismiss toasts after 5 seconds
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach(toast => {
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 5000);
  });
}

);
