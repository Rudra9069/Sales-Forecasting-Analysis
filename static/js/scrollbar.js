/**
 * Forecastify - Liquid Glass Navigation Controller
 * Manages the floating bottom liquid glass tab bar for mobile,
 * active route synchronization, and tactile micro-interactions.
 */
(function () {
    function initMobileLiquidTabBar() {
        let tabBar = document.querySelector('.bottom-liquid-tab-bar');

        // Check if user is logged in
        const isUserLoggedIn = document.body.dataset.userLoggedIn === 'true' || 
                               !!document.querySelector('a[href*="/profile"]') ||
                               !!document.querySelector('a[href*="/logout"]');

        // Check if there is an existing cart badge count on desktop navbar
        const existingCartBadge = document.querySelector('.navbar .cart-badge') || 
                                  document.querySelector('.navbar [data-cart-count]');
        const cartCount = existingCartBadge ? (existingCartBadge.textContent.trim() || '0') : '';

        // 1. If tab bar is not in the DOM, inject it dynamically as a resilient fallback
        if (!tabBar) {
            tabBar = document.createElement('nav');
            tabBar.className = 'bottom-liquid-tab-bar';
            tabBar.setAttribute('aria-label', 'Mobile Bottom Navigation');
            
            tabBar.innerHTML = `
                <div class="liquid-tab-pill">
                    <a href="/" class="liquid-tab-item" data-route="home">
                        <i class="fas fa-house"></i>
                        <span>Home</span>
                    </a>
                    <a href="/products" class="liquid-tab-item" data-route="products">
                        <i class="fas fa-boxes-stacked"></i>
                        <span>Products</span>
                    </a>
                    <a href="/cart" class="liquid-tab-item" data-route="cart">
                        <div class="liquid-tab-icon-wrap">
                            <i class="fas fa-shopping-bag"></i>
                            ${(cartCount && cartCount !== '0') ? `<span class="liquid-tab-badge">${cartCount}</span>` : ''}
                        </div>
                        <span>Cart</span>
                    </a>
                    <a href="/about" class="liquid-tab-item" data-route="about">
                        <i class="fas fa-circle-info"></i>
                        <span>About</span>
                    </a>
                    <a href="/contact" class="liquid-tab-item" data-route="contact">
                        <i class="fas fa-headset"></i>
                        <span>Contact</span>
                    </a>
                    <a href="${isUserLoggedIn ? '/profile' : '/login'}" class="liquid-tab-item" data-route="${isUserLoggedIn ? 'profile' : 'login'}">
                        <i class="fas ${isUserLoggedIn ? 'fa-user-circle' : 'fa-user'}"></i>
                        <span>${isUserLoggedIn ? 'Profile' : 'Login'}</span>
                    </a>
                </div>
            `;
            document.body.appendChild(tabBar);
        }

        // 2. Synchronize active state based on current location pathname
        const path = window.location.pathname.toLowerCase();
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
            item.addEventListener('touchstart', function() {
                this.style.transform = 'scale(0.92)';
            }, { passive: true });
            item.addEventListener('touchend', function() {
                this.style.transform = '';
            }, { passive: true });
            item.addEventListener('touchcancel', function() {
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
