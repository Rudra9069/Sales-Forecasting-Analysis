document.addEventListener('DOMContentLoaded', () => {

    // Promo Code Logic
    const promoBtn = document.getElementById('apply-promo');
    const promoInput = document.getElementById('promo-code');
    const promoMessage = document.getElementById('promo-message');

    if (promoBtn) {
        promoBtn.addEventListener('click', () => {
            const code = promoInput.value.trim().toUpperCase();
            if (code === 'SAVE20') {
                promoMessage.textContent = 'Coupon applied successfully! 20% off.';
                promoMessage.className = 'promo-message success';

                const totalElem = document.getElementById('summary-total');
                const originalTotal = parseFloat(totalElem.getAttribute('data-original-total') || 0);
                const discount = originalTotal * 0.20;
                const newTotal = originalTotal - discount;

                document.getElementById('summary-discount').textContent = `-₹${discount.toFixed(2)}`;
                totalElem.textContent = `₹${newTotal.toFixed(2)}`;
            } else if (code !== '') {
                promoMessage.textContent = 'Invalid or expired coupon code.';
                promoMessage.className = 'promo-message error';
            }
        });
    }

    // Form Validation Logic
    const formInputs = document.querySelectorAll('#customer-info input[required], #delivery-address input[required], #delivery-address select[required]');
    const placeOrderBtn = document.getElementById('place-order-btn');

    formInputs.forEach(input => {
        input.addEventListener('input', () => {
            validateInput(input);
            validateForm();
        });
        input.addEventListener('blur', () => {
            validateInput(input);
            validateForm();
        });
    });

    function validateInput(input) {
        let isValid = true;

        if (!input.value || input.value.trim() === '') {
            isValid = false;
        } else if (input.type === 'email') {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            isValid = re.test(input.value.trim());
        }

        const group = input.closest('.form-group');
        if (group) {
            if (isValid) {
                group.classList.remove('has-error');
                input.classList.remove('error');
            } else {
                group.classList.add('has-error');
                input.classList.add('error');
            }
        }

        return isValid;
    }

    function validateForm() {
        let isFormValid = true;

        const basicInputs = document.querySelectorAll('#customer-info input[required], #delivery-address input[required], #delivery-address select[required]');
        basicInputs.forEach(input => {
            if (!validateInput(input)) {
                isFormValid = false;
            }
        });

        if (placeOrderBtn) {
            placeOrderBtn.disabled = !isFormValid;
        }
        return isFormValid;
    }

    // Initial Validation Check
    validateForm();

    function resetButton() {
        if (!placeOrderBtn) return;
        placeOrderBtn.disabled = false;
        placeOrderBtn.innerHTML = '<i class="fas fa-lock"></i> Place Order & Pay';
    }

    // Handle Place Order Click — always launches Razorpay
    if (placeOrderBtn) {
        placeOrderBtn.addEventListener('click', async (e) => {
            e.preventDefault();

            if (!validateForm()) {
                const firstError = document.querySelector('.form-group.has-error input, .form-group.has-error select');
                if (firstError) {
                    firstError.focus();
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                return;
            }

            const promoCode = promoInput ? promoInput.value.trim().toUpperCase() : '';
            placeOrderBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting to Razorpay...';
            placeOrderBtn.disabled = true;

            try {
                // Call backend to create Razorpay Order
                const res = await fetch('/create_razorpay_order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ promo_code: promoCode })
                });

                const data = await res.json();
                if (!data.success) {
                    alert(data.message || 'Unable to initiate Razorpay checkout. Please try again.');
                    resetButton();
                    return;
                }

                if (typeof Razorpay === 'undefined') {
                    alert('Razorpay Checkout SDK is still loading. Please check your internet connection and try again.');
                    resetButton();
                    return;
                }

                const customerName  = document.getElementById('full-name')?.value || '';
                const customerEmail = document.getElementById('email')?.value || '';
                const customerPhone = document.getElementById('phone')?.value || '';

                const options = {
                    key: data.key_id,
                    amount: data.amount,
                    currency: data.currency || 'INR',
                    name: 'Forecastify',
                    description: 'Order Checkout (Test Mode)',
                    image: window.location.origin + '/static/images/logo.png',
                    order_id: data.order_id,
                    handler: async function (response) {
                        placeOrderBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying Payment...';

                        try {
                            const verifyRes = await fetch('/verify_razorpay_payment', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    razorpay_order_id:  response.razorpay_order_id,
                                    razorpay_payment_id: response.razorpay_payment_id,
                                    razorpay_signature:  response.razorpay_signature,
                                    full_name: customerName,
                                    email:     customerEmail,
                                    phone:     customerPhone,
                                    address:  document.getElementById('address')?.value  || '',
                                    city:     document.getElementById('city')?.value     || '',
                                    state:    document.getElementById('state')?.value    || '',
                                    pincode:  document.getElementById('pincode')?.value  || '',
                                    payment_method: 'razorpay',
                                    promo_code: promoCode
                                })
                            });

                            const verifyData = await verifyRes.json();
                            if (verifyData.success && verifyData.redirect_url) {
                                window.location.href = verifyData.redirect_url;
                            } else {
                                alert(verifyData.message || 'Payment verification failed. Please contact support.');
                                resetButton();
                            }
                        } catch (err) {
                            console.error('Verification error:', err);
                            alert('Network error while verifying payment. Please refresh or contact support.');
                            resetButton();
                        }
                    },
                    prefill: {
                        name:    customerName,
                        email:   customerEmail,
                        contact: customerPhone
                    },
                    theme: {
                        color: '#2563EB'
                    },
                    modal: {
                        ondismiss: function () {
                            resetButton();
                        }
                    }
                };

                const rzp = new Razorpay(options);
                rzp.on('payment.failed', function (resp) {
                    const desc = resp.error ? resp.error.description : 'Payment was not successful.';
                    alert('Payment Failed: ' + desc);
                    resetButton();
                });

                rzp.open();

            } catch (err) {
                console.error('Error during checkout initiation:', err);
                alert('Something went wrong connecting to payment gateway. Please try again.');
                resetButton();
            }
        });
    }
});
