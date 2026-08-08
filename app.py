from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
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

# --- MySQL Database Configuration ---
db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'Rudra@1001'),
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


if __name__ == '__main__':
    app.run(debug=True)
