document.addEventListener('DOMContentLoaded', () => {
    // Payment Method Toggle
    const paymentCards = document.querySelectorAll('.payment-method-card');
    const paymentDetails = document.querySelectorAll('.payment-details');

    paymentCards.forEach(card => {
        card.addEventListener('click', () => {
            // Remove active classes
            paymentCards.forEach(c => c.classList.remove('active'));
            paymentDetails.forEach(d => d.classList.remove('active'));
            
            // Check radio
            const radio = card.querySelector('input[type="radio"]');
            radio.checked = true;
            
            // Add active classes
            card.classList.add('active');
            const targetId = radio.value + '-details';
            const targetDetail = document.getElementById(targetId);
            if (targetDetail) {
                targetDetail.classList.add('active');
            }
            
            validateForm();
        });
    });

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
    const formInputs = document.querySelectorAll('input[required], select[required]');
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
        
        if (input.value.trim() === '') {
            isValid = false;
        } else if (input.type === 'email') {
            const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            isValid = re.test(input.value);
        } else if (input.id === 'card-number') {
            isValid = input.value.replace(/\s/g, '').length === 16;
        } else if (input.id === 'card-expiry') {
            const re = /^(0[1-9]|1[0-2])\/\d{2}$/;
            isValid = re.test(input.value);
        } else if (input.id === 'card-cvv') {
            isValid = input.value.length === 3 || input.value.length === 4;
        }

        const group = input.closest('.form-group');
        if (isValid) {
            group.classList.remove('has-error');
            input.classList.remove('error');
        } else {
            group.classList.add('has-error');
            input.classList.add('error');
        }
        
        return isValid;
    }

    function validateForm() {
        let isFormValid = true;
        
        // Validate basic info and address
        const basicInputs = document.querySelectorAll('#customer-info input[required], #delivery-address input[required], #delivery-address select[required]');
        basicInputs.forEach(input => {
            if (!validateInput(input)) {
                isFormValid = false;
            }
        });

        // Validate active payment method details
        const activeMethod = document.querySelector('input[name="payment_method"]:checked').value;
        const activeDetails = document.getElementById(activeMethod + '-details');
        
        if (activeDetails) {
            const paymentInputs = activeDetails.querySelectorAll('input[required], select[required]');
            paymentInputs.forEach(input => {
                if (!validateInput(input)) {
                    isFormValid = false;
                }
            });
        }

        placeOrderBtn.disabled = !isFormValid;
    }
    
    // Initial Validation Check
    validateForm();
    
    // Handle Place Order Click
    placeOrderBtn.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Simple loading state
        placeOrderBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        placeOrderBtn.disabled = true;
        
        // Submit the form to backend
        const form = document.getElementById('checkout-form');
        form.submit();
    });
});
