from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import os
from dotenv import load_dotenv
import random

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_super_secret_key')  # Needed for flash messages and sessions

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# --- MySQL Database Configuration ---
db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'harshit0312'),
    'database': os.environ.get('DB_NAME', 'sales_forecasting_db')
}

def get_db_connection():
    """Create and return a new MySQL database connection."""
    return mysql.connector.connect(**db_config)

def send_welcome_email(user_email, user_name):
    """Sends a welcome email to the newly registered user."""
    try:
        sender_email = os.environ.get('MAIL_USERNAME')
        sender_password = os.environ.get('MAIL_PASSWORD')
        
        msg = MIMEMultipart()
        msg['From'] = f"Forecastify <{sender_email}>"
        msg['To'] = user_email
        msg['Subject'] = "Welcome to Forecastify!"
        
        body = f"Hello {user_name},\n\nThank you for registering at Forecastify! We are excited to have you on board.\n\nBest regards,\nThe Forecastify Team"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, user_email, text)
        server.quit()
        print(f"Email sent successfully to {user_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {user_email}. Error: {e}")
        return False

def send_reset_email(user_email, code):
    """Sends a password reset code email to the user."""
    try:
        sender_email = os.environ.get('MAIL_USERNAME')
        sender_password = os.environ.get('MAIL_PASSWORD')
        
        msg = MIMEMultipart()
        msg['From'] = f"Forecastify <{sender_email}>"
        msg['To'] = user_email
        msg['Subject'] = "Your Password Reset Code"
        
        body = f"Hello,\n\nYou requested a password reset. Your 6-digit verification code is:\n\n{code}\n\nIf you did not request this, please ignore this email.\n\nBest regards,\nThe Forecastify Team"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, user_email, text)
        server.quit()
        print(f"Reset email sent successfully to {user_email}")
        return True
    except Exception as e:
        print(f"Failed to send reset email to {user_email}. Error: {e}")
        return False

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        pincode = request.form.get('pincode')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Backend Validation
        if not name or not email or not password or not confirm_password:
            flash('Please fill out all required fields.', 'error')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('register'))

        # Hash the password before storing
        hashed_password = generate_password_hash(password)

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if email already exists
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('Email is already registered. Please log in.', 'error')
                return redirect(url_for('register'))

            # Insert new user into the database
            insert_query = """
                INSERT INTO users (name, email, password, phone, address, city, state, pincode)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (name, email, hashed_password, phone, address, city, state, pincode))
            conn.commit()

            # Send welcome email asynchronously
            email_thread = threading.Thread(target=send_welcome_email, args=(email, name))
            email_thread.start()
            
            flash('email_success:Account created successfully! A welcome email is on its way.', 'success')
                
            return redirect(url_for('login'))

        except mysql.connector.Error as err:
            flash(f'Database error: {err}', 'error')
            return redirect(url_for('register'))
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve form data
        email = request.form.get('email')
        password = request.form.get('password')

        # Backend Validation
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return redirect(url_for('login'))

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Fetch user by email
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user['password'], password):
                flash('Invalid email or password.', 'error')
                return redirect(url_for('login'))

            # Store user info in session
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']

            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))

        except mysql.connector.Error as err:
            flash(f'Database error: {err}', 'error')
            return redirect(url_for('login'))
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('login.html')

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or request.form
    email = data.get('email')
    if not email:
        return jsonify({'success': False, 'message': 'Please enter your email address.'})
        
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user:
            code = str(random.randint(100000, 999999))
            session['reset_code'] = code
            session['reset_email'] = email
            
            # Send email asynchronously
            threading.Thread(target=send_reset_email, args=(email, code)).start()
            
            return jsonify({'success': True, 'message': 'A 6-digit verification code has been sent to your email.'})
        else:
            return jsonify({'success': False, 'message': 'No account found with that email address.'})
            
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/verify-code', methods=['POST'])
def verify_code():
    if 'reset_email' not in session or 'reset_code' not in session:
        return jsonify({'success': False, 'message': 'Session expired. Please request a new code.'})
        
    data = request.get_json() or request.form
    entered_code = data.get('code')
    if entered_code == session['reset_code']:
        session['reset_authorized'] = True
        session.pop('reset_code', None) # Remove code after successful verification
        return jsonify({'success': True, 'message': 'Code verified successfully.'})
    else:
        return jsonify({'success': False, 'message': 'Invalid verification code. Please try again.'})

@app.route('/reset-password', methods=['POST'])
def reset_password():
    if not session.get('reset_authorized') or 'reset_email' not in session:
        return jsonify({'success': False, 'message': 'You are not authorized to reset the password.'})
        
    data = request.get_json() or request.form
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    
    if not password or not confirm_password:
        return jsonify({'success': False, 'message': 'Please fill out all fields.'})
        
    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Passwords do not match.'})
        
    hashed_password = generate_password_hash(password)
    email = session['reset_email']
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
        conn.commit()
        
        # Clear reset session variables
        session.pop('reset_email', None)
        session.pop('reset_authorized', None)
        
        return jsonify({'success': True, 'message': 'Your password has been successfully reset. Please log in with your new password.'})
        
    except mysql.connector.Error as err:
        return jsonify({'success': False, 'message': f'Database error: {err}'})
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/products')
def products():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products ORDER BY product_id")
        products_list = cursor.fetchall()
        return render_template('products.html', products=products_list)
    except mysql.connector.Error as err:
        flash(f'Database error: {err}', 'error')
        return render_template('products.html', products=[])
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_cart_details():
    cart = session.get('cart', {})
    cart_items = []
    subtotal = 0
    total_discount = 0
    
    if not cart:
        return cart_items, subtotal, total_discount
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        product_ids = list(cart.keys())
        if product_ids:
            format_strings = ','.join(['%s'] * len(product_ids))
            cursor.execute(f"SELECT * FROM products WHERE product_id IN ({format_strings})", tuple(product_ids))
            products = cursor.fetchall()
            
            for p in products:
                pid = str(p['product_id'])
                qty = cart.get(pid, 1)
                
                price = float(p['price'])
                # Simulate a discount if original price was higher, for now original = price
                original_price = price
                discount = 0
                
                item_total = price * qty
                subtotal += item_total
                
                cart_items.append({
                    'product_id': pid,
                    'name': p['name'],
                    'category': p['category'],
                    'image_url': p['image_url'],
                    'price': price,
                    'original_price': original_price,
                    'quantity': qty,
                    'discount': discount
                })
    except Exception as e:
        print(f"Error fetching cart details: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            
    return cart_items, subtotal, total_discount

@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    product_id = str(product_id)
    if 'cart' not in session:
        session['cart'] = {}
    
    qty = 1
    if request.is_json:
        qty = request.json.get('quantity', 1)
        
    cart = session['cart']
    cart[product_id] = cart.get(product_id, 0) + int(qty)
    session['cart'] = cart
    session.modified = True
    
    return jsonify({'status': 'success', 'message': 'Added to cart', 'cart_count': sum(cart.values())})

@app.route('/update_cart/<product_id>', methods=['POST'])
def update_cart(product_id):
    product_id = str(product_id)
    if 'cart' in session and product_id in session['cart']:
        if request.is_json:
            qty = request.json.get('quantity', 1)
            if int(qty) > 0:
                session['cart'][product_id] = int(qty)
            else:
                del session['cart'][product_id]
            session.modified = True
    return jsonify({'status': 'success'})

@app.route('/remove_from_cart/<product_id>', methods=['POST'])
def remove_from_cart(product_id):
    product_id = str(product_id)
    if 'cart' in session and product_id in session['cart']:
        del session['cart'][product_id]
        session.modified = True
    return jsonify({'status': 'success'})

@app.route('/buy_now/<product_id>')
def buy_now(product_id):
    product_id = str(product_id)
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    cart[product_id] = cart.get(product_id, 0) + 1
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('checkout'))

@app.route('/cart')
def cart():
    cart_items, subtotal, total_discount = get_cart_details()
    tax = (subtotal - total_discount) * 0.08
    shipping = 15.00 if subtotal > 0 else 0
    total = subtotal - total_discount + tax + shipping
    
    return render_template('cart.html', 
                           cart_items=cart_items, 
                           subtotal=subtotal, 
                           total_discount=total_discount,
                           tax=tax,
                           shipping=shipping,
                           total=total)

@app.route('/checkout')
def checkout():
    cart_items, subtotal, total_discount = get_cart_details()
    tax = (subtotal - total_discount) * 0.08
    shipping = 15.00 if subtotal > 0 else 0
    total = subtotal - total_discount + tax + shipping
    
    if not cart_items:
        return redirect(url_for('cart'))
    
    # Fetch user data for auto-filling the form
    user_data = {}
    if 'user_id' in session:
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT name, email, phone, address, city, state, pincode FROM users WHERE user_id = %s",
                (session['user_id'],)
            )
            user_data = cursor.fetchone() or {}
            cursor.close()
        except Exception as e:
            print(f"Error fetching user data: {e}")
        finally:
            if conn:
                conn.close()
        
    return render_template('checkout.html', 
                           cart_items=cart_items, 
                           subtotal=subtotal, 
                           total_discount=total_discount,
                           tax=tax,
                           shipping=shipping,
                           total=total,
                           user=user_data)

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session:
        flash('Please login to place an order.', 'error')
        return redirect(url_for('login'))
    
    cart_items, subtotal, total_discount = get_cart_details()
    if not cart_items:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('cart'))
    
    tax = (subtotal - total_discount) * 0.08
    shipping = 15.00 if subtotal > 0 else 0
    total = subtotal - total_discount + tax + shipping
    
    # Get form data
    full_name = request.form.get('full_name', '')
    email = request.form.get('email', '')
    phone = request.form.get('phone', '')
    address = request.form.get('address', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    pincode = request.form.get('pincode', '')
    payment_method = request.form.get('payment_method', 'card')
    
    shipping_address = f"{full_name}, {address}, {city}, {state} {pincode}"
    
    # Map payment methods to DB enum values
    payment_map = {
        'card': 'card',
        'upi': 'UPI',
        'netbanking': 'card',  # Treat netbanking as card in DB
        'cod': 'COD'
    }
    db_payment_method = payment_map.get(payment_method, 'card')
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Insert into transactions table
        cursor.execute(
            "INSERT INTO transactions (user_id, total_amount, status, shipping_address) VALUES (%s, %s, %s, %s)",
            (session['user_id'], total, 'pending', shipping_address)
        )
        transaction_id = cursor.lastrowid
        
        # 2. Insert each cart item into transaction_items table
        for item in cart_items:
            cursor.execute(
                "INSERT INTO transaction_items (transaction_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                (transaction_id, item['product_id'], item['quantity'], item['price'])
            )
        
        # 3. Insert into payments table
        payment_status = 'pending' if db_payment_method == 'COD' else 'success'
        cursor.execute(
            "INSERT INTO payments (transaction_id, payment_method, payment_status, amount) VALUES (%s, %s, %s, %s)",
            (transaction_id, db_payment_method, payment_status, total)
        )
        
        conn.commit()
        
        # Clear the cart
        session.pop('cart', None)
        session.modified = True
        
        # Generate order reference
        order_ref = f"ORD-{transaction_id}-{random.randint(1000, 9999)}"
        
        return redirect(url_for('order_success', ref=order_ref))
        
    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        print(f"Database error placing order: {err}")
        flash('Something went wrong while placing your order. Please try again.', 'error')
        return redirect(url_for('checkout'))
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/order_success')
def order_success():
    order_ref = request.args.get('ref', 'N/A')
    return render_template('order_success.html', order_ref=order_ref)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please login to view your profile.', 'error')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get user details
        cursor.execute("SELECT name, email, phone FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        # Get order history (with items)
        cursor.execute("""
            SELECT t.transaction_id, t.total_amount, t.status, t.order_date, t.shipping_address
            FROM transactions t
            WHERE t.user_id = %s
            ORDER BY t.order_date DESC
        """, (user_id,))
        orders = cursor.fetchall()
        
        # For each order, fetch items
        for order in orders:
            cursor.execute("""
                SELECT ti.quantity, ti.price, p.name, p.image_url
                FROM transaction_items ti
                JOIN products p ON ti.product_id = p.product_id
                WHERE ti.transaction_id = %s
            """, (order['transaction_id'],))
            order['order_items'] = cursor.fetchall()
            
        # Get payment history
        cursor.execute("""
            SELECT p.payment_id, p.payment_method, p.payment_status, p.amount, p.payment_date, t.transaction_id
            FROM payments p
            JOIN transactions t ON p.transaction_id = t.transaction_id
            WHERE t.user_id = %s
            ORDER BY p.payment_date DESC
        """, (user_id,))
        payments = cursor.fetchall()
        
        return render_template('profile.html', user=user, orders=orders, payments=payments)
        
    except mysql.connector.Error as err:
        print(f"Error fetching profile: {err}")
        flash('Could not load profile data.', 'error')
        return redirect(url_for('home'))
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    email = request.form.get('email')
    phone = request.form.get('phone')
    user_id = session['user_id']
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET email = %s, phone = %s WHERE user_id = %s", (email, phone, user_id))
        conn.commit()
        flash('Profile updated successfully!', 'success')
    except mysql.connector.Error as err:
        print(f"Error updating profile: {err}")
        flash('Failed to update profile. Email might be in use.', 'error')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            
    return redirect(url_for('profile'))

@app.route('/submit_help', methods=['POST'])
def submit_help():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    subject = request.form.get('subject')
    description = request.form.get('description')
    transaction_id = request.form.get('transaction_id')
    user_id = session['user_id']
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if not transaction_id:
            cursor.execute("SELECT transaction_id FROM transactions WHERE user_id = %s ORDER BY order_date DESC LIMIT 1", (user_id,))
            res = cursor.fetchone()
            if res:
                transaction_id = res['transaction_id']
            else:
                flash('You must have at least one order to submit a complaint.', 'error')
                return redirect(url_for('profile'))
                
        cursor.execute("INSERT INTO complaints (user_id, transaction_id, subject, description) VALUES (%s, %s, %s, %s)",
                       (user_id, transaction_id, subject, description))
        conn.commit()
        
        # Send Email to forecasting0001@gmail.com
        cursor.execute("SELECT name, email FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        sender_email = os.environ.get('MAIL_USERNAME')
        sender_password = os.environ.get('MAIL_PASSWORD')
        admin_email = "forecasting0001@gmail.com"
        
        if sender_email and sender_password:
            msg = MIMEMultipart()
            msg['From'] = f"Forecastify <{sender_email}>"
            msg['To'] = admin_email
            msg['Subject'] = f"Help Request: {subject}"
            
            body = f"New help request from {user['name']} ({user['email']})\n\nTransaction ID: {transaction_id}\n\nDescription:\n{description}"
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, admin_email, msg.as_string())
            server.quit()
        
        flash('Your complaint has been submitted.', 'success')
    except Exception as err:
        print(f"Error submitting help: {err}")
        flash('Failed to submit complaint.', 'error')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            
    return redirect(url_for('profile'))

if __name__ == '__main__':
    app.run(debug=True)
