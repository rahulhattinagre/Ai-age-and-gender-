/**
 * Age & Gender AI Detector — Landing Page JS
 * Handles: navigation, sidebar toggle, particles, stat counters, scroll animations
 */

/* ============================================================
   NAVIGATION HANDLERS
   ============================================================ */
function goToLogin() {
  // Redirect to Flask login route
  window.location.href = '/login';
}

function goToSignup() {
  // Redirect to Flask signup/register route
  window.location.href = '/signup';
}

function handleNav(page, event) {
  event.preventDefault();

  // Remove active from all
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

  // Set active on clicked item
  const clicked = document.getElementById(`nav-${page}`);
  if (clicked) clicked.classList.add('active');

  // Close sidebar on mobile after clicking
  if (window.innerWidth <= 768) closeSidebar();

  // Route to relevant section or page
  switch (page) {
    case 'home':
      smoothScrollTo('heroSection');
      break;
    case 'dashboard':
      window.location.href = '/dashboard';
      break;
    case 'about':
      smoothScrollTo('featuresSection');
      break;
    case 'docs':
      smoothScrollTo('statsSection');
      break;
  }
}

function smoothScrollTo(id) {
  const el = document.getElementById(id);
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

/* ============================================================
   SIDEBAR TOGGLE (mobile)
   ============================================================ */
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  const hamburger = document.getElementById('hamburgerBtn');

  const isOpen = sidebar.classList.toggle('open');
  overlay.classList.toggle('active', isOpen);
  hamburger.classList.toggle('is-open', isOpen);
}

function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebarOverlay').classList.remove('active');
  document.getElementById('hamburgerBtn').classList.remove('is-open');
}

/* ============================================================
   PARTICLES
   ============================================================ */
function createParticles() {
  const container = document.getElementById('particlesContainer');
  if (!container) return;

  const count = window.innerWidth < 768 ? 12 : 25;
  const colors = ['rgba(0,212,167,0.7)', 'rgba(123,97,255,0.7)', 'rgba(0,212,167,0.4)', 'rgba(255,255,255,0.3)'];

  for (let i = 0; i < count; i++) {
    const p = document.createElement('div');
    p.classList.add('particle');

    const size = Math.random() * 4 + 2;
    const color = colors[Math.floor(Math.random() * colors.length)];
    const left = Math.random() * 100;
    const duration = Math.random() * 15 + 10;
    const delay = Math.random() * 12;

    p.style.cssText = `
      width: ${size}px;
      height: ${size}px;
      background: ${color};
      left: ${left}%;
      animation-duration: ${duration}s;
      animation-delay: ${delay}s;
      box-shadow: 0 0 ${size * 3}px ${color};
    `;

    container.appendChild(p);
  }
}

/* ============================================================
   COUNTER ANIMATION
   ============================================================ */
function animateCounter(el) {
  const target = parseInt(el.getAttribute('data-target'));
  const suffix = el.getAttribute('data-suffix') || '';
  if (isNaN(target)) return;

  const duration = 2000;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // ease-out-expo
    const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);

    let value = Math.round(eased * target);

    // Format for 10K+
    if (target === 10000) {
      el.textContent = Math.round(eased * 10) + 'K+';
    } else {
      el.textContent = value + suffix;
    }

    if (progress < 1) requestAnimationFrame(update);
  }

  requestAnimationFrame(update);
}

/* ============================================================
   INTERSECTION OBSERVER — scroll reveal & stat counters
   ============================================================ */
function initScrollAnimations() {
  // Fade-in-up elements
  const fadeEls = document.querySelectorAll('.fade-in-up');
  const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.animationPlayState = 'running';
        fadeObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  fadeEls.forEach(el => {
    el.style.animationPlayState = 'paused';
    fadeObserver.observe(el);
  });

  // Stat counters
  const statNumbers = document.querySelectorAll('.stat-number[data-target]');
  const statObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        statObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  statNumbers.forEach(el => statObserver.observe(el));
}

/* ============================================================
   NAVBAR — active highlight on scroll
   ============================================================ */
function initScrollSpy() {
  const sections = ['heroSection', 'loginCardSection', 'featuresSection', 'statsSection'];
  const navMap = {
    heroSection: 'home',
    featuresSection: 'about',
    statsSection: 'docs',
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const navId = navMap[entry.target.id];
        if (navId) {
          document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
          const activeNav = document.getElementById(`nav-${navId}`);
          if (activeNav) activeNav.classList.add('active');
        }
      }
    });
  }, { threshold: 0.4 });

  sections.forEach(id => {
    const el = document.getElementById(id);
    if (el) observer.observe(el);
  });
}

/* ============================================================
   BUTTON RIPPLE EFFECT
   ============================================================ */
function addRippleEffect() {
  const buttons = document.querySelectorAll('button, .nav-item');
  buttons.forEach(btn => {
    btn.addEventListener('click', function (e) {
      const rect = this.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const ripple = document.createElement('span');
      ripple.style.cssText = `
        position: absolute;
        border-radius: 50%;
        background: rgba(255,255,255,0.2);
        width: 8px; height: 8px;
        left: ${x - 4}px; top: ${y - 4}px;
        transform: scale(0);
        animation: rippleAnim 0.5s ease-out forwards;
        pointer-events: none;
        z-index: 999;
      `;

      this.style.position = 'relative';
      this.style.overflow = 'hidden';
      this.appendChild(ripple);

      setTimeout(() => ripple.remove(), 600);
    });
  });

  // Inject keyframe
  if (!document.getElementById('rippleStyle')) {
    const style = document.createElement('style');
    style.id = 'rippleStyle';
    style.textContent = `
      @keyframes rippleAnim {
        to { transform: scale(30); opacity: 0; }
      }
    `;
    document.head.appendChild(style);
  }
}

/* ============================================================
   SIDEBAR GLASSMORPHISM GRADIENT ON HOVER
   ============================================================ */
function initSidebarGlow() {
  const sidebar = document.getElementById('sidebar');
  sidebar.addEventListener('mousemove', (e) => {
    const rect = sidebar.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    sidebar.style.background = `
      radial-gradient(circle at ${x}px ${y}px, rgba(0,212,167,0.05) 0%, transparent 60%),
      rgba(15, 32, 39, 0.85)
    `;
  });
  sidebar.addEventListener('mouseleave', () => {
    sidebar.style.background = 'rgba(15, 32, 39, 0.85)';
  });
}

/* ============================================================
   INIT
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {
  createParticles();
  initScrollAnimations();
  initScrollSpy();
  addRippleEffect();
  initSidebarGlow();

  // Trigger hero animations on load
  setTimeout(() => {
    document.querySelectorAll('.fade-in-up').forEach(el => {
      el.style.animationPlayState = 'running';
    });
  }, 100);
});

// Handle resize
window.addEventListener('resize', () => {
  if (window.innerWidth > 768) closeSidebar();
});
