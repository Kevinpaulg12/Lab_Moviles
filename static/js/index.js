/* ══════════════════════════════════════════
   SISOL — index.js
   Cargado al final del <body> en base.html
══════════════════════════════════════════ */

"use strict";

/* ── Toasts ── */
function closeToast(triggerEl) {
    const toast = triggerEl.closest('.toast-card');
    if (!toast) return;
    toast.classList.remove('toast-enter');
    toast.classList.add('toast-exit');
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
}

(function initToasts() {
    document.querySelectorAll('.toast-card').forEach((toast, i) => {
        const btn = toast.querySelector('button[onclick]');
        if (!btn) return;
        const delay = 5000 + i * 250;
        setTimeout(() => {
            if (toast.isConnected) closeToast(btn);
        }, delay);
    });
})();


/* ── Mobile menu ── */
(function initMobileMenu() {
    const btn  = document.getElementById('mobile-menu-button');
    const menu = document.getElementById('mobile-menu');
    if (!btn || !menu) return;

    function setOpen(open) {
        menu.classList.toggle('active', open);
        btn.setAttribute('aria-expanded', String(open));
        const icon = btn.querySelector('i');
        if (icon) {
            icon.classList.toggle('fa-bars',  !open);
            icon.classList.toggle('fa-xmark',  open);
        }
    }

    btn.addEventListener('click', () => setOpen(!menu.classList.contains('active')));

    // Cerrar al pulsar un enlace o el backdrop (fuera del menú)
    menu.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => setOpen(false));
    });

    document.addEventListener('click', (e) => {
        if (!menu.contains(e.target) && !btn.contains(e.target)) {
            setOpen(false);
        }
    });

    // Cerrar con Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && menu.classList.contains('active')) setOpen(false);
    });
})();


/* ── Scroll-to-top ── */
(function initScrollTop() {
    const btn = document.getElementById('scroll-to-top');
    if (!btn) return;

    const toggle = () => btn.classList.toggle('visible', window.scrollY > 300);

    window.addEventListener('scroll', toggle, { passive: true });
    toggle(); // estado inicial
})();


/* ── Animaciones on-scroll (IntersectionObserver) ── */
(function initScrollAnimations() {
    if (!('IntersectionObserver' in window)) return;

    const items = document.querySelectorAll('.animate-fade-in-up[style*="opacity:0"]');
    if (!items.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '';   // deja que la animación CSS tome el control
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });

    items.forEach(el => observer.observe(el));
})();