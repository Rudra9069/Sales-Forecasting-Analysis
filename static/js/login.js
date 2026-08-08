document.addEventListener('DOMContentLoaded', () => {
    // Password visibility toggle
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            
            if (input && input.type === 'password') {
                input.type = 'text';
                this.classList.remove('fa-eye');
                this.classList.add('fa-eye-slash');
            } else if (input) {
                input.type = 'password';
                this.classList.remove('fa-eye-slash');
                this.classList.add('fa-eye');
            }
        });
    });

    // Forgot Password Modal Logic
    const forgotModal = document.getElementById('forgotPasswordModal');
    const openForgotModalBtn = document.getElementById('openForgotModal');
    const closeForgotModalBtn = document.getElementById('closeForgotModal');

    const step1 = document.getElementById('forgotStep1');
    const step2 = document.getElementById('forgotStep2');
    const step3 = document.getElementById('forgotStep3');

    const form1 = document.getElementById('forgotEmailForm');
    const form2 = document.getElementById('forgotCodeForm');
    const form3 = document.getElementById('forgotResetForm');

    const msg1 = document.getElementById('forgotMsgStep1');
    const msg2 = document.getElementById('forgotMsgStep2');
    const msg3 = document.getElementById('forgotMsgStep3');

    function showAlert(element, text, type) {
        element.textContent = text;
        element.className = `modal-alert ${type}`;
    }

    function hideAlert(element) {
        element.style.display = 'none';
        element.className = 'modal-alert';
    }

    function resetModal() {
        step1.style.display = 'block';
        step2.style.display = 'none';
        step3.style.display = 'none';
        
        if (form1) form1.reset();
        if (form2) form2.reset();
        if (form3) form3.reset();

        if (msg1) hideAlert(msg1);
        if (msg2) hideAlert(msg2);
        if (msg3) hideAlert(msg3);
    }

    if (openForgotModalBtn) {
        openForgotModalBtn.addEventListener('click', (e) => {
            e.preventDefault();
            resetModal();
            if (forgotModal) forgotModal.classList.add('active');
        });
    }

    if (closeForgotModalBtn) {
        closeForgotModalBtn.addEventListener('click', () => {
            if (forgotModal) forgotModal.classList.remove('active');
        });
    }

    // Close on overlay click
    if (forgotModal) {
        forgotModal.addEventListener('click', (e) => {
            if (e.target === forgotModal) {
                forgotModal.classList.remove('active');
            }
        });
    }

    // Step 1: Submit Email
    if (form1) {
        form1.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('sendCodeBtn');
            const email = document.getElementById('forgotEmail').value;
            
            hideAlert(msg1);
            btn.disabled = true;
            btn.textContent = 'Sending Code...';

            try {
                const response = await fetch('/forgot-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email })
                });

                const data = await response.json();
                if (data.success) {
                    step1.style.display = 'none';
                    step2.style.display = 'block';
                    showAlert(msg2, data.message, 'success');
                } else {
                    showAlert(msg1, data.message, 'error');
                }
            } catch (err) {
                showAlert(msg1, 'An error occurred. Please try again.', 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = 'Send Verification Code';
            }
        });
    }

    // Step 2: Submit Verification Code
    if (form2) {
        form2.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('verifyCodeBtn');
            const code = document.getElementById('forgotCode').value;

            hideAlert(msg2);
            btn.disabled = true;
            btn.textContent = 'Verifying...';

            try {
                const response = await fetch('/verify-code', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: code })
                });

                const data = await response.json();
                if (data.success) {
                    step2.style.display = 'none';
                    step3.style.display = 'block';
                    showAlert(msg3, data.message, 'success');
                } else {
                    showAlert(msg2, data.message, 'error');
                }
            } catch (err) {
                showAlert(msg2, 'An error occurred. Please try again.', 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = 'Verify Code';
            }
        });
    }

    // Step 3: Submit Reset Password
    if (form3) {
        form3.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = document.getElementById('resetPassBtn');
            const password = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmNewPassword').value;

            hideAlert(msg3);

            if (password !== confirmPassword) {
                showAlert(msg3, 'Passwords do not match.', 'error');
                return;
            }

            btn.disabled = true;
            btn.textContent = 'Updating...';

            try {
                const response = await fetch('/reset-password', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password: password, confirm_password: confirmPassword })
                });

                const data = await response.json();
                if (data.success) {
                    if (forgotModal) forgotModal.classList.remove('active');
                    if (typeof Swal !== 'undefined') {
                        Swal.fire({
                            title: 'Success!',
                            text: data.message,
                            icon: 'success',
                            confirmButtonColor: '#1E3A5F'
                        });
                    } else {
                        alert(data.message);
                    }
                } else {
                    showAlert(msg3, data.message, 'error');
                }
            } catch (err) {
                showAlert(msg3, 'An error occurred. Please try again.', 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = 'Update Password';
            }
        });
    }
});
