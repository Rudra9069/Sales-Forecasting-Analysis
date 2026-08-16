document.addEventListener('DOMContentLoaded', () => {
    const splashScreen = document.getElementById('splash-screen');
    const splashLogoWrapper = document.querySelector('.splash-logo-wrapper');
    const splashLogoImg = document.querySelector('.splash-logo');
    const navbarLogoImg = document.querySelector('.navbar-logo');

    if (!splashScreen || !splashLogoWrapper || !splashLogoImg) return;

    // Set body to splash-active to prevent scrolling
    document.body.classList.add('splash-active');

    const MINIMUM_DISPLAY_TIME = 1600;
    const startTime = Date.now();

    const hideSplashScreen = () => {
        if (navbarLogoImg) {
            // Step 1: Kill the CSS intro animation so we can control transform via JS
            splashLogoWrapper.style.animation = 'none';
            splashLogoWrapper.style.opacity = '1';
            splashLogoWrapper.style.transform = 'scale(1)';

            // Step 2: Hide text and prepare for flight
            splashScreen.classList.add('fly-logo');

            // Step 3: Force reflow, then get exact positions and fly
            splashLogoWrapper.offsetHeight;

            const sourceRect = splashLogoImg.getBoundingClientRect();
            const targetRect = navbarLogoImg.getBoundingClientRect();

            // Calculate deltas from top-left to top-left to avoid any wrapper centering drift
            const deltaX = (targetRect.left - sourceRect.left) - 7.8;
            const deltaY = (targetRect.top - sourceRect.top) + 0.5;
            const scale = targetRect.width / sourceRect.width;

            splashLogoWrapper.style.transformOrigin = 'top left';
            splashLogoWrapper.style.transition = 'transform 0.9s cubic-bezier(0.4, 0, 0.2, 1)';
            splashLogoWrapper.style.transform = `translate(${deltaX}px, ${deltaY}px) scale(${scale})`;

            // Step 4: After flight completes, fade background and remove splash
            setTimeout(() => {
                splashScreen.classList.add('animate-out');
                splashLogoWrapper.style.transition = 'opacity 0.5s ease';
                splashLogoWrapper.style.opacity = '0';

                document.body.classList.remove('splash-active');

                setTimeout(() => {
                    splashScreen.remove();
                }, 900); // Wait for background to fade
            }, 900); // Wait for flight to complete
        } else {
            // Fallback
            splashScreen.classList.add('fade-out');
            document.body.classList.remove('splash-active');
            setTimeout(() => splashScreen.remove(), 800);
        }
    };

    // Listen for window load
    window.addEventListener('load', () => {
        const elapsedTime = Date.now() - startTime;
        const timeRemaining = Math.max(0, MINIMUM_DISPLAY_TIME - elapsedTime);
        setTimeout(() => {
            hideSplashScreen();
        }, timeRemaining);
    });

    // Fallback: max 10 seconds
    setTimeout(() => {
        if (document.body.classList.contains('splash-active')) {
            hideSplashScreen();
        }
    }, 10000);
});
