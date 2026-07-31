from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_super_secret_key' # Needed for flash messages

# Simple in-memory dict for demo purposes (replace with a real DB later)
users_db = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve form data
        fullname = request.form.get('fullname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Backend Validation
        if not fullname or not email or not password or not confirm_password:
            flash('Please fill out all required fields.', 'error')
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('register'))
            
        if email in users_db:
            flash('Email is already registered. Please log in.', 'error')
            return redirect(url_for('register'))
        
        # Save user to database
        users_db[email] = {
            'fullname': fullname,
            'phone': phone,
            'password': password # Note: In production, always hash passwords!
        }
        
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
        
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
            
        user = users_db.get(email)
        
        if not user or user['password'] != password:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))
            
        # Redirect to home/dashboard page after successful login
        flash('Logged in successfully!', 'success')
        return redirect(url_for('home'))
        
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
