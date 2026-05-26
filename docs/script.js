/* ========== Tab Switching ========== */
document.addEventListener('DOMContentLoaded', function () {
  initTabs();
  initSmoothScroll();
  initNavbarScroll();
  initMobileNav();
  initTypewriter();
  initIntersectionObserver();
});

function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      const target = this.dataset.tab;

      tabBtns.forEach(function (b) { b.classList.remove('active'); });
      tabContents.forEach(function (c) { c.classList.remove('active'); });

      this.classList.add('active');
      var targetContent = document.getElementById('tab-' + target);
      if (targetContent) {
        targetContent.classList.add('active');
      }
    });
  });
}

/* ========== Smooth Scroll ========== */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

/* ========== Navbar Scroll Effect ========== */
function initNavbarScroll() {
  var navbar = document.getElementById('navbar');
  var lastScrollY = 0;

  window.addEventListener('scroll', function () {
    var scrollY = window.scrollY;
    if (scrollY > 80) {
      navbar.style.borderColor = 'var(--border-color)';
      navbar.style.background = 'rgba(13, 17, 23, 0.95)';
    } else {
      navbar.style.borderColor = 'transparent';
      navbar.style.background = 'rgba(13, 17, 23, 0.85)';
    }
    lastScrollY = scrollY;
  }, { passive: true });
}

/* ========== Mobile Navigation ========== */
function initMobileNav() {
  var nav = document.querySelector('.nav-links');
  var toggle = document.createElement('button');
  toggle.className = 'mobile-toggle';
  toggle.innerHTML = '&#9776;';
  toggle.setAttribute('aria-label', 'Toggle navigation');

  var navContainer = document.querySelector('.nav-container');
  if (navContainer && nav) {
    navContainer.insertBefore(toggle, nav);
  }

  toggle.addEventListener('click', function () {
    nav.classList.toggle('mobile-open');
  });

  nav.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () {
      nav.classList.remove('mobile-open');
    });
  });
}

/* ========== Typewriter Effect ========== */
function initTypewriter() {
  var terminals = document.querySelectorAll('.terminal-body');
  if (terminals.length === 0) return;

  terminals.forEach(function (terminal) {
    var lines = terminal.querySelectorAll('.line');

    lines.forEach(function (line, index) {
      line.style.opacity = '0';
      line.style.transition = 'opacity 0.3s ease';
    });

    var revealIndex = 0;
    function revealNext() {
      if (revealIndex < lines.length) {
        lines[revealIndex].style.opacity = '1';
        revealIndex++;
        if (revealIndex < 30) {
          setTimeout(revealNext, 60);
        } else if (revealIndex < 60) {
          setTimeout(revealNext, 30);
        } else {
          setTimeout(revealNext, 15);
        }
      }
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          observer.unobserve(entry.target);
          setTimeout(revealNext, 400);
        }
      });
    }, { threshold: 0.1 });

    observer.observe(terminal);
  });
}

/* ========== Intersection Observer for Sections ========== */
function initIntersectionObserver() {
  var sections = document.querySelectorAll('.section');

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.05 });

  sections.forEach(function (section) {
    section.style.opacity = '0';
    section.style.transform = 'translateY(30px)';
    section.style.transition = 'opacity 0.7s ease, transform 0.7s ease';
    observer.observe(section);
  });
}
