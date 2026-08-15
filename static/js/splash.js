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
            // Get positions
            const sourceRect = splashLogoImg.getBoundingClientRect();
            const targetRect = navbarLogoImg.getBoundingClientRect();

            // Calculate deltas from center of source to center of target
            const deltaX = (targetRect.left + targetRect.width / 2) - (sourceRect.left + sourceRect.width / 2);
            const deltaY = (targetRect.top + targetRect.height / 2) - (sourceRect.top + sourceRect.height / 2) - 16; // -16px upward offset for margin compensation
            const scale = targetRect.width / sourceRect.width;

            // Step 1: Kill the CSS intro animation so we can control transform via JS
            splashLogoWrapper.style.animation = 'none';
            splashLogoWrapper.style.opacity = '1';
            splashLogoWrapper.style.transform = 'scale(1)';

            // Step 2: Start fading background and text simultaneously
            splashScreen.classList.add('animate-out');

            // Step 3: Force reflow, then fly the logo
            splashLogoWrapper.offsetHeight;
            splashLogoWrapper.style.transition = 'transform 0.9s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.5s ease 1.2s';
            splashLogoWrapper.style.transform = `translate(${deltaX}px, ${deltaY}px) scale(${scale})`;
            splashLogoWrapper.style.opacity = '0'; // Fade out at the end of the flight (0.7s delay)

            // Step 4: Allow scrolling and clean up after animation finishes
            document.body.classList.remove('splash-active');
            setTimeout(() => {
                splashScreen.remove();
            }, 1800);
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
