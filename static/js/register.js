document.addEventListener('DOMContentLoaded', () => {
    // Password visibility toggle
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

    // Password strength simulator (Visual only)
    const passwordInput = document.getElementById('password');
    const strengthBars = document.querySelectorAll('.strength-bar');
    const strengthText = document.querySelector('.password-strength-text');

    passwordInput.addEventListener('input', function() {
        const val = this.value;
        let strength = 0;

        if (val.length > 5) strength += 1;
        if (val.length > 8) strength += 1;
        if (/[A-Z]/.test(val)) strength += 1;
        if (/[0-9]/.test(val)) strength += 1;
        if (/[^A-Za-z0-9]/.test(val)) strength += 1;

        // Reset bars
        strengthBars.forEach(bar => {
            bar.style.backgroundColor = '#D9D9D9';
        });

        if (val.length === 0) {
            strengthText.textContent = '';
            return;
        }

        // Color bars based on strength
        if (strength <= 2) {
            strengthBars[0].style.backgroundColor = '#e74c3c';
            strengthText.textContent = 'Weak';
            strengthText.style.color = '#e74c3c';
        } else if (strength <= 4) {
            strengthBars[0].style.backgroundColor = '#f1c40f';
            strengthBars[1].style.backgroundColor = '#f1c40f';
            strengthText.textContent = 'Medium';
            strengthText.style.color = '#f1c40f';
        } else {
            strengthBars[0].style.backgroundColor = '#2ecc71';
            strengthBars[1].style.backgroundColor = '#2ecc71';
            strengthBars[2].style.backgroundColor = '#2ecc71';
            strengthText.textContent = 'Strong';
            strengthText.style.color = '#2ecc71';
        }
    });

    // Password match indicator (Visual only)
    const confirmInput = document.getElementById('confirm_password');
    const matchIndicator = document.getElementById('match-indicator');

    confirmInput.addEventListener('input', checkMatch);
    passwordInput.addEventListener('input', checkMatch);

    function checkMatch() {
        if (confirmInput.value.length === 0) {
            matchIndicator.className = 'match-indicator';
            matchIndicator.textContent = '';
            return;
        }

        if (confirmInput.value === passwordInput.value) {
            matchIndicator.className = 'match-indicator success';
            matchIndicator.innerHTML = '<i class="fas fa-check-circle"></i> Passwords match';
        } else {
            matchIndicator.className = 'match-indicator error';
            matchIndicator.innerHTML = '<i class="fas fa-times-circle"></i> Passwords do not match';
        }
    }

    // Mock form validation (Visual only)
    const form = document.getElementById('registerForm');
    const emailInput = document.getElementById('email');

    form.addEventListener('submit', function(e) {
        e.preventDefault(); // Do not actually submit

        // Simple visual validation for email
        const emailGroup = emailInput.closest('.form-group');
        if (!emailInput.value.includes('@')) {
            emailGroup.classList.add('has-error');
        } else {
            emailGroup.classList.remove('has-error');
            // Mock success feedback or transition
            const btn = document.querySelector('.register-btn');
            const originalText = btn.textContent;
            btn.textContent = 'Creating Account...';
            btn.style.backgroundColor = '#2ecc71';
            
            setTimeout(() => {
                btn.textContent = 'Account Created!';
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.style.backgroundColor = '';
                    form.reset();
                    // Reset visual indicators
                    strengthBars.forEach(bar => bar.style.backgroundColor = '#D9D9D9');
                    strengthText.textContent = '';
                    matchIndicator.className = 'match-indicator';
                    matchIndicator.textContent = '';
                }, 2000);
            }, 1000);
        }
    });

    // Clear error state on input
    emailInput.addEventListener('input', function() {
        this.closest('.form-group').classList.remove('has-error');
    });
});
