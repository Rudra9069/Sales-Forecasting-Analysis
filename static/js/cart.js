document.addEventListener('DOMContentLoaded', () => {
    // Initial calculation is now done on the backend via Jinja

    // Event Listeners for Quantity Buttons
    document.querySelectorAll('.quantity-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const icon = btn.querySelector('i');
            const isPlus = icon && icon.classList.contains('fa-plus');
            const input = btn.parentElement.querySelector('.quantity-input');
            const cartItem = btn.closest('.cart-item');
            const productId = cartItem.getAttribute('data-product-id');
            let value = parseInt(input.value);

            if (isPlus) {
                value++;
            } else if (value > 1) {
                value--;
            }
            
            input.value = value;
            
            // Sync with backend
            updateCartItem(productId, value);
        });
    });

    // Event Listeners for Remove Buttons
    let itemToRemove = null;
    let itemToRemoveId = null;
    const modalOverlay = document.getElementById('remove-modal');
    const confirmBtn = document.getElementById('confirm-remove');
    const cancelBtn = document.getElementById('cancel-remove');

    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            itemToRemove = btn.closest('.cart-item');
            itemToRemoveId = btn.getAttribute('data-product-id');
            modalOverlay.classList.add('active');
        });
    });

    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            itemToRemove = null;
            itemToRemoveId = null;
            modalOverlay.classList.remove('active');
        });
    }

    if (confirmBtn) {
        confirmBtn.addEventListener('click', () => {
            if (itemToRemove && itemToRemoveId) {
                // Sync with backend
                fetch(`/remove_from_cart/${itemToRemoveId}`, {
                    method: 'POST'
                }).then(res => res.json()).then(data => {
                    if (data.status === 'success') {
                        // Reload page to reflect changes from backend
                        window.location.reload();
                    }
                }).catch(err => console.error(err));
            }
        });
    }
});

function updateCartItem(productId, quantity) {
    fetch(`/update_cart/${productId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ quantity: quantity })
    }).then(res => res.json()).then(data => {
        if (data.status === 'success') {
            // Reload page to update totals dynamically from server
            window.location.reload();
        }
    }).catch(err => console.error(err));
}

function showToast(message) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<i class="fas fa-check-circle toast-icon"></i> <span>${message}</span>`;
    
    container.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Remove after 3s
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
