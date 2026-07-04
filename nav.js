/* Shared navbar initialiser for the CADPOINT mega-menu.
   Used by every page that injects header.html. */
function initCaddNav() {
  const coursesNav = document.getElementById('coursesNav');
  const caret = document.getElementById('coursesCaret');
  const menu = document.getElementById('coursesMegaMenu');
  const closeBtn = document.getElementById('closeMegaMenu');

  if (!coursesNav || !caret || !menu) return;

  if (closeBtn) {
    closeBtn.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      menu.classList.remove('show');
    });
  }

  if (window.innerWidth <= 991) {
    caret.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();
      menu.classList.toggle('show');
    });
    document.addEventListener('click', function (e) {
      if (!coursesNav.contains(e.target)) menu.classList.remove('show');
    });
    return;
  }

  coursesNav.addEventListener('mouseenter', function () { menu.classList.add('show'); });
  coursesNav.addEventListener('mouseleave', function () { menu.classList.remove('show'); });
  menu.addEventListener('mouseleave', function () { menu.classList.remove('show'); });

  const nav = document.getElementById('mainNav');
  if (nav) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) nav.classList.add('scrolled');
      else nav.classList.remove('scrolled');
    });
  }
}