/**
 * Forecastify - Liquid Glass Navigation Controller
 * Manages the floating bottom liquid glass tab bar for mobile,
 * active route synchronization, and tactile micro-interactions.
 */
(function () {
    function initMobileLiquidTabBar() {
        const path = window.location.pathname.toLowerCase();

        // Never show or inject bottom liquid tab bar on Login, Register, Auth, or Admin pages
        if (
            path.includes('login') ||
            path.includes('register') ||
            path.includes('auth') ||
            path.includes('admin') ||
            document.querySelector('.auth-container') ||
            document.querySelector('.admin-layout')
        ) {
            const existing = document.querySelector('.bottom-liquid-tab-bar');
            if (existing) existing.remove();
            return;
        }

        const tabBar = document.querySelector('.bottom-liquid-tab-bar');
        if (!tabBar) {
            return;
        }

        // 2. Synchronize active state based on current location pathname
        const tabItems = tabBar.querySelectorAll('.liquid-tab-item');

        tabItems.forEach(item => {
            const route = item.dataset.route || '';
            let isActive = false;

            if (route === 'home' && (path === '/' || path === '/home' || path.endsWith('index.html'))) {
                isActive = true;
            } else if (route === 'products' && path.includes('product')) {
                isActive = true;
            } else if (route === 'cart' && path.includes('cart')) {
                isActive = true;
            } else if (route === 'about' && path.includes('about')) {
                isActive = true;
            } else if (route === 'contact' && path.includes('contact')) {
                isActive = true;
            } else if (route === 'profile' && path.includes('profile')) {
                isActive = true;
            } else if (route === 'login' && (path.includes('login') || path.includes('register') || path.includes('auth'))) {
                isActive = true;
            }

            if (isActive) {
                tabItems.forEach(t => t.classList.remove('active'));
                item.classList.add('active');
            }
        });

        // 3. Tactile touch micro-interactions
        tabItems.forEach(item => {
            item.addEventListener('touchstart', function () {
                this.style.transform = 'scale(0.92)';
            }, { passive: true });
            item.addEventListener('touchend', function () {
                this.style.transform = '';
            }, { passive: true });
            item.addEventListener('touchcancel', function () {
                this.style.transform = '';
            }, { passive: true });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMobileLiquidTabBar);
    } else {
        initMobileLiquidTabBar();
    }
})();
