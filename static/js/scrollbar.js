/**
 * Forecastify - Liquid Glass Navigation Controller
 * Provides liquid glass morphing hamburger animation, floating capsule drawer state,
 * and ambient backdrop blur across all storefront pages.
 */
(function () {
    function initLiquidGlassMenu() {
        let menuToggle = document.getElementById('menuToggle') || document.querySelector('.menu-toggle');
        const navbarNav = document.getElementById('navbarLinks') || document.querySelector('.navbar-nav');

        if (!menuToggle || !navbarNav) return;
        if (menuToggle.dataset.liquidInit === 'true') return;

        // 1. Inject Liquid Glass Morphing Lines if not already present
        if (!menuToggle.querySelector('.liquid-hamburger-box')) {
            const existingIcon = menuToggle.querySelector('i');
            if (existingIcon) {
                existingIcon.style.display = 'none';
            }

            const liquidBox = document.createElement('span');
            liquidBox.className = 'liquid-hamburger-box';
            liquidBox.setAttribute('aria-hidden', 'true');
            liquidBox.innerHTML = `
                <span class="liquid-line line-top"></span>
                <span class="liquid-line line-mid"></span>
                <span class="liquid-line line-bot"></span>
            `;
            menuToggle.appendChild(liquidBox);
        }

        // 2. Clone the button to remove conflicting legacy listeners attached by individual templates
        const cleanToggle = menuToggle.cloneNode(true);
        if (menuToggle.parentNode) {
            menuToggle.parentNode.replaceChild(cleanToggle, menuToggle);
            menuToggle = cleanToggle;
        }
        menuToggle.dataset.liquidInit = 'true';

        // 3. Ensure ambient liquid glass backdrop overlay exists in the DOM
        let backdrop = document.querySelector('.liquid-navbar-backdrop');
        if (!backdrop) {
            backdrop = document.createElement('div');
            backdrop.className = 'liquid-navbar-backdrop';
            backdrop.setAttribute('aria-hidden', 'true');
            document.body.appendChild(backdrop);
        }

        // 4. State Management Functions
        function openLiquidMenu() {
            navbarNav.classList.add('show', 'active');
            menuToggle.classList.add('active');
            menuToggle.setAttribute('aria-expanded', 'true');
            backdrop.classList.add('active');
            document.body.style.overflow = 'hidden'; // Lock background scroll
        }

        function closeLiquidMenu() {
            navbarNav.classList.remove('show', 'active');
            menuToggle.classList.remove('active');
            menuToggle.setAttribute('aria-expanded', 'false');
            backdrop.classList.remove('active');
            document.body.style.overflow = '';
        }

        function toggleLiquidMenu(e) {
            if (e) {
                e.preventDefault();
                e.stopPropagation();
            }
            const isOpen = navbarNav.classList.contains('show') || navbarNav.classList.contains('active');
            if (isOpen) {
                closeLiquidMenu();
            } else {
                openLiquidMenu();
            }
        }

        // 5. Bind Clean Events
        menuToggle.addEventListener('click', toggleLiquidMenu);

        // Click outside (Backdrop) closes menu
        backdrop.addEventListener('click', (e) => {
            e.stopPropagation();
            closeLiquidMenu();
        });

        // Escape key closes menu
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && (navbarNav.classList.contains('show') || navbarNav.classList.contains('active'))) {
                closeLiquidMenu();
            }
        });

        // Clicking any menu link closes menu gracefully
        navbarNav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                closeLiquidMenu();
            });
        });

        // Auto close if viewport resized back to desktop
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                if (window.innerWidth > 960 && (navbarNav.classList.contains('show') || navbarNav.classList.contains('active'))) {
                    closeLiquidMenu();
                }
            }, 100);
        }, { passive: true });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initLiquidGlassMenu);
    } else {
        initLiquidGlassMenu();
    }
})();
