document.addEventListener('DOMContentLoaded', () => {
    // --- Password Visibility Toggle ---
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            
            if (input.type === 'password') {
                input.type = 'text';
                this.classList.remove('fa-eye');
                this.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                this.classList.remove('fa-eye-slash');
                this.classList.add('fa-eye');
            }
        });
    });

    // --- Password Strength Indicator ---
    const passwordInput = document.getElementById('password');
    const strengthBars = document.querySelectorAll('.strength-bar');
    const strengthText = document.querySelector('.password-strength-text');

    if (passwordInput && strengthBars.length > 0 && strengthText) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;

            if (password.length === 0) {
                // Reset bars and text when empty
                strengthBars.forEach(bar => bar.style.backgroundColor = '#D9D9D9');
                strengthText.textContent = '';
                return;
            }

            // Scoring criteria
            if (password.length >= 6) strength++;
            if (password.length >= 10) strength++;
            if (/[A-Z]/.test(password)) strength++;
            if (/[0-9]/.test(password)) strength++;
            if (/[^A-Za-z0-9]/.test(password)) strength++;

            // Map score to level
            let level, color, text;
            if (strength <= 2) {
                level = 1;
                color = '#e74c3c';
                text = 'Weak';
            } else if (strength <= 3) {
                level = 2;
                color = '#f39c12';
                text = 'Strong';
            } else {
                level = 3;
                color = '#2ecc71';
                text = 'Perfect';
            }

            // Update strength bars
            strengthBars.forEach((bar, index) => {
                if (index < level) {
                    bar.style.backgroundColor = color;
                } else {
                    bar.style.backgroundColor = '#D9D9D9';
                }
            });

            // Update strength text
            strengthText.textContent = text;
            strengthText.style.color = color;
        });
    }

    // --- Password Match Indicator ---
    const confirmPasswordInput = document.getElementById('confirm_password');
    const matchIndicator = document.getElementById('match-indicator');

    if (confirmPasswordInput && matchIndicator && passwordInput) {
        confirmPasswordInput.addEventListener('input', function() {
            const password = passwordInput.value;
            const confirmPassword = this.value;

            if (confirmPassword.length === 0) {
                matchIndicator.textContent = '';
                matchIndicator.className = 'match-indicator';
                return;
            }

            if (password === confirmPassword) {
                matchIndicator.textContent = '✓ Passwords match';
                matchIndicator.className = 'match-indicator success';
            } else {
                matchIndicator.textContent = '✗ Passwords do not match';
                matchIndicator.className = 'match-indicator error';
            }
        });

        // Also re-check when the original password changes
        passwordInput.addEventListener('input', function() {
            const confirmPassword = confirmPasswordInput.value;

            if (confirmPassword.length === 0) {
                matchIndicator.textContent = '';
                matchIndicator.className = 'match-indicator';
                return;
            }

            if (this.value === confirmPassword) {
                matchIndicator.textContent = '✓ Passwords match';
                matchIndicator.className = 'match-indicator success';
            } else {
                matchIndicator.textContent = '✗ Passwords do not match';
                matchIndicator.className = 'match-indicator error';
            }
        });
    }
});
