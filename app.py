from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'  # Needed for flash messages and sessions

# --- MySQL Database Configuration ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'harshit0312',
    'database': 'sales_forecasting_db'
}

def get_db_connection():
    """Create and return a new MySQL database connection."""
    return mysql.connector.connect(**db_config)


@app.route('/')
def home():
    return render_template('index.html')


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

            flash('Account created successfully! You can now log in.', 'success')
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


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
