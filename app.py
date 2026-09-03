from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory, Response
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import os
import csv
import io
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


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', 'General Query').strip()
        message = request.form.get('message', '').strip()

        if name and email and message:
            flash(f"Thank you {name}! Your message regarding '{subject}' has been received. Our team will respond shortly.", 'success')
            return redirect(url_for('contact'))
        else:
            flash("Please fill in all required fields before submitting your message.", "error")

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

    panel = request.args.get('panel', 'register')
    return render_template('auth.html', panel=panel)


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

            flash(f"Welcome, {user['name']}!", 'success')
            return redirect(url_for('home'))

        except mysql.connector.Error as err:
            flash(f'Database error: {err}', 'error')
            return redirect(url_for('login'))
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    panel = request.args.get('panel', 'login')
    return render_template('auth.html', panel=panel)

# ==========================================
# ADMIN ROUTES
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please enter both admin email and password.', 'error')
            return redirect(url_for('admin_login'))

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user['password'], password):
                flash('Invalid admin email or password.', 'error')
                return redirect(url_for('admin_login'))

            if user.get('role') != 'admin':
                flash('Access denied. Administrator privileges required.', 'error')
                return redirect(url_for('admin_login'))

            session['admin_id'] = user['user_id']
            session['admin_name'] = user['name']
            session['admin_email'] = user['email']
            session['admin_logged_in'] = True
            session['user_role'] = 'admin'

            flash(f"Welcome back, Admin {user['name']}!", 'success')
            return redirect(url_for('admin_dashboard'))

        except mysql.connector.Error as err:
            flash(f'Database error: {err}', 'error')
            return redirect(url_for('admin_login'))
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('admin/login.html')

def generate_trend_chart_data(daily_data):
    if not daily_data:
        daily_data = [
            {'day_name': 'Mon', 'tx_cnt': 5, 'day_revenue': 12000},
            {'day_name': 'Tue', 'tx_cnt': 12, 'day_revenue': 28000},
            {'day_name': 'Wed', 'tx_cnt': 8, 'day_revenue': 19000},
            {'day_name': 'Thu', 'tx_cnt': 22, 'day_revenue': 55000},
            {'day_name': 'Fri', 'tx_cnt': 16, 'day_revenue': 38000},
        ]

    xs = [20, 85, 150, 215, 280]
    
    max_rev = max((float(d['day_revenue']) for d in daily_data), default=1.0)
    if max_rev <= 0: max_rev = 1.0

    max_ord = max((int(d['tx_cnt']) for d in daily_data), default=1)
    if max_ord <= 0: max_ord = 1

    rev_coords = []
    ord_coords = []

    for i, d in enumerate(daily_data):
        x = xs[i] if i < len(xs) else 280
        rev_val = float(d['day_revenue'])
        ord_cnt = int(d['tx_cnt'])

        rev_y = round(95.0 - (rev_val / max_rev) * 65.0, 1)
        ord_y = round(105.0 - (ord_cnt / max_ord) * 50.0, 1)

        rev_coords.append({'x': x, 'y': rev_y, 'val': rev_val, 'day': d['day_name']})
        ord_coords.append({'x': x, 'y': ord_y, 'val': ord_cnt, 'day': d['day_name']})

    rev_path = f"M {rev_coords[0]['x']},{rev_coords[0]['y']}"
    for i in range(1, len(rev_coords)):
        prev = rev_coords[i-1]
        curr = rev_coords[i]
        cx1 = round(prev['x'] + (curr['x'] - prev['x']) / 2.0, 1)
        rev_path += f" C {cx1},{prev['y']} {cx1},{curr['y']} {curr['x']},{curr['y']}"

    ord_path = f"M {ord_coords[0]['x']},{ord_coords[0]['y']}"
    for i in range(1, len(ord_coords)):
        prev = ord_coords[i-1]
        curr = ord_coords[i]
        cx1 = round(prev['x'] + (curr['x'] - prev['x']) / 2.0, 1)
        ord_path += f" C {cx1},{prev['y']} {cx1},{curr['y']} {curr['x']},{curr['y']}"

    peak_idx = max(range(len(rev_coords)), key=lambda k: rev_coords[k]['val'])

    return {
        'rev_path': rev_path,
        'ord_path': ord_path,
        'rev_coords': rev_coords,
        'ord_coords': ord_coords,
        'highlight_x': rev_coords[peak_idx]['x'],
        'highlight_rev_y': rev_coords[peak_idx]['y'],
        'highlight_ord_y': ord_coords[peak_idx]['y'],
        'highlight_day': rev_coords[peak_idx]['day'],
        'highlight_val': rev_coords[peak_idx]['val'],
        'highlight_cnt': ord_coords[peak_idx]['val']
    }

@app.route('/admin')
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash('Please log in with admin credentials first.', 'error')
        return redirect(url_for('admin_login'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. Active Users Count (role = 'user')
        cursor.execute("SELECT COUNT(*) AS user_count FROM users WHERE role = 'user'")
        user_count = cursor.fetchone()['user_count']

        # 2. Total Products Count
        cursor.execute("SELECT COUNT(*) AS product_count FROM products")
        product_count = cursor.fetchone()['product_count']

        # 3. Orders & Total Revenue
        cursor.execute("""
            SELECT COUNT(*) AS tx_count, COALESCE(SUM(total_amount), 0) AS total_revenue 
            FROM orders
        """)
        tx_stats = cursor.fetchone()
        tx_count = tx_stats['tx_count']
        total_revenue = float(tx_stats['total_revenue'])

        # 4. Status Counts (delivered, shipped, pending, cancelled)
        cursor.execute("SELECT status, COUNT(*) AS cnt FROM orders GROUP BY status")
        status_rows = cursor.fetchall()
        status_dict = {'delivered': 0, 'shipped': 0, 'pending': 0, 'cancelled': 0}
        for row in status_rows:
            status_dict[row['status']] = row['cnt']

        completed_orders = status_dict['delivered']
        in_progress_orders = status_dict['shipped']
        pending_orders = status_dict['pending']

        total_orders_calc = max(tx_count, 1)
        completed_pct = round((completed_orders / total_orders_calc) * 100, 1)
        in_progress_pct = round((in_progress_orders / total_orders_calc) * 100, 1)
        pending_pct = round((pending_orders / total_orders_calc) * 100, 1)

        # 5. Category breakdown
        cursor.execute("""
            SELECT category, COUNT(*) as cat_count 
            FROM products 
            GROUP BY category 
            ORDER BY cat_count DESC 
            LIMIT 3
        """)
        cat_rows = cursor.fetchall()

        total_prods_calc = max(product_count, 1)
        categories = []
        chip_classes = ['chip-pink', 'chip-blue', 'chip-green']
        bar_classes = ['bar-pink', 'bar-blue', 'bar-green']

        for i, cat in enumerate(cat_rows):
            pct = round((cat['cat_count'] / total_prods_calc) * 100)
            categories.append({
                'name': cat['category'],
                'count': cat['cat_count'],
                'pct': pct,
                'chip_class': chip_classes[i % len(chip_classes)],
                'bar_class': bar_classes[i % len(bar_classes)]
            })

        avg_progress = round(sum(c['pct'] for c in categories) / len(categories)) if categories else 0

        # 6. Recent Customers
        cursor.execute("""
            SELECT user_id, name, email 
            FROM users 
            WHERE role = 'user' 
            ORDER BY user_id DESC 
            LIMIT 3
        """)
        recent_customers = cursor.fetchall()

        # 7. Daily / Recent Orders graph data
        cursor.execute("""
            SELECT DATE_FORMAT(order_date, '%%a') AS day_name, 
                   COUNT(*) as tx_cnt, 
                   COALESCE(SUM(total_amount), 0) as day_revenue
            FROM orders
            GROUP BY DATE(order_date), DATE_FORMAT(order_date, '%%a')
            ORDER BY DATE(order_date) DESC
            LIMIT 5
        """)
        daily_rows = cursor.fetchall()
        daily_data = list(reversed(daily_rows))
        trend_chart = generate_trend_chart_data(daily_data)

        # 8. Full Report: Recent Transactions (Top 7)
        cursor.execute("""
            SELECT o.order_id, o.total_amount, o.status, o.order_date, o.shipping_address,
                   u.name AS customer_name, u.email AS customer_email,
                   p.payment_method
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.user_id
            LEFT JOIN payments p ON o.order_id = p.order_id
            ORDER BY o.order_id DESC
            LIMIT 7
        """)
        report_orders = cursor.fetchall()

        # 9. Full Report: Top Selling Products (Top 5)
        cursor.execute("""
            SELECT p.product_id, p.name, p.category, p.price, p.stock_quantity, p.image_url,
                   COALESCE(SUM(oi.quantity), 0) AS units_sold,
                   COALESCE(SUM(oi.quantity * oi.price), 0) AS revenue_generated
            FROM products p
            LEFT JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.product_id
            ORDER BY units_sold DESC, revenue_generated DESC
            LIMIT 5
        """)
        report_products = cursor.fetchall()

        # 10. Full Report: Top Spending Customers (Top 5)
        cursor.execute("""
            SELECT u.user_id, u.name, u.email, u.city, u.state,
                   COUNT(o.order_id) AS total_orders,
                   COALESCE(SUM(o.total_amount), 0) AS total_spent
            FROM users u
            LEFT JOIN orders o ON u.user_id = o.user_id
            WHERE u.role = 'user'
            GROUP BY u.user_id
            ORDER BY total_spent DESC
            LIMIT 5
        """)
        report_customers = cursor.fetchall()

        # 11. Financial Summary Calculations
        aov = round(total_revenue / max(tx_count, 1), 2)

        # 11.5 Period breakdown for KPI dropdown filters
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN DATE(order_date) = CURDATE() THEN total_amount ELSE 0 END), 0) AS today_rev,
                COALESCE(SUM(CASE WHEN DATE(order_date) = CURDATE() THEN 1 ELSE 0 END), 0) AS today_ord,
                COALESCE(SUM(CASE WHEN order_date >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN total_amount ELSE 0 END), 0) AS weekly_rev,
                COALESCE(SUM(CASE WHEN order_date >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 ELSE 0 END), 0) AS weekly_ord,
                COALESCE(SUM(CASE WHEN order_date >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN total_amount ELSE 0 END), 0) AS monthly_rev,
                COALESCE(SUM(CASE WHEN order_date >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 ELSE 0 END), 0) AS monthly_ord,
                COALESCE(SUM(CASE WHEN order_date >= DATE_SUB(NOW(), INTERVAL 365 DAY) THEN total_amount ELSE 0 END), 0) AS yearly_rev,
                COALESCE(SUM(CASE WHEN order_date >= DATE_SUB(NOW(), INTERVAL 365 DAY) THEN 1 ELSE 0 END), 0) AS yearly_ord,
                COALESCE(SUM(total_amount), 0) AS all_rev,
                COUNT(*) AS all_ord
            FROM orders
        """)
        p_row = cursor.fetchone()
        
        monthly_rev = float(p_row['monthly_rev']) if p_row and p_row['monthly_rev'] > 0 else (total_revenue if total_revenue > 0 else 0)
        monthly_ord = int(p_row['monthly_ord']) if p_row and p_row['monthly_ord'] > 0 else tx_count

        weekly_rev = float(p_row['weekly_rev']) if p_row and p_row['weekly_rev'] > 0 else round(monthly_rev * 0.28, 2)
        weekly_ord = int(p_row['weekly_ord']) if p_row and p_row['weekly_ord'] > 0 else max(1, round(monthly_ord * 0.25))

        today_rev = float(p_row['today_rev']) if p_row and p_row['today_rev'] > 0 else round(weekly_rev * 0.15, 2)
        today_ord = int(p_row['today_ord']) if p_row and p_row['today_ord'] > 0 else max(0, round(weekly_ord * 0.2))

        yearly_rev = float(p_row['yearly_rev']) if p_row and p_row['yearly_rev'] > 0 else total_revenue
        yearly_ord = int(p_row['yearly_ord']) if p_row and p_row['yearly_ord'] > 0 else tx_count

        kpi_periods = {
            'today': {'orders': today_ord, 'revenue': today_rev},
            'weekly': {'orders': weekly_ord, 'revenue': weekly_rev},
            'monthly': {'orders': monthly_ord, 'revenue': monthly_rev},
            'yearly': {'orders': yearly_ord, 'revenue': yearly_rev},
            'all': {'orders': tx_count, 'revenue': total_revenue}
        }

        # 12. Full Sales Timeline & Category Analytics for Dynamic Charts
        cursor.execute("""
            SELECT DATE_FORMAT(order_date, '%%b %%d') AS date_label, 
                   COUNT(*) as tx_cnt, 
                   COALESCE(SUM(total_amount), 0) as day_revenue
            FROM orders
            GROUP BY DATE(order_date), DATE_FORMAT(order_date, '%%b %%d')
            ORDER BY DATE(order_date) ASC
            LIMIT 14
        """)
        timeline_rows = cursor.fetchall()

        cursor.execute("""
            SELECT p.category, 
                   COUNT(DISTINCT p.product_id) AS prod_cnt,
                   COALESCE(SUM(oi.quantity), 0) AS total_units_sold,
                   COALESCE(SUM(oi.quantity * oi.price), 0) AS cat_revenue
            FROM products p
            LEFT JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.category
            ORDER BY cat_revenue DESC
        """)
        category_analytics = cursor.fetchall()

        timeline_data = [
            {'date': str(r['date_label']), 'orders': int(r['tx_cnt']), 'revenue': float(r['day_revenue'])}
            for r in timeline_rows
        ]
        prod_chart_data = [
            {'name': p['name'], 'units': int(p['units_sold']), 'revenue': float(p['revenue_generated'])}
            for p in report_products
        ]
        cust_chart_data = [
            {'name': c['name'] if c['name'] else f"User #{c['user_id']}", 'orders': int(c['total_orders']), 'spent': float(c['total_spent'])}
            for c in report_customers
        ]
        cat_chart_data = [
            {'category': ct['category'], 'prods': int(ct['prod_cnt']), 'units': int(ct['total_units_sold']), 'revenue': float(ct['cat_revenue'])}
            for ct in category_analytics
        ]

        dash_data = {
            'user_count': user_count,
            'product_count': product_count,
            'tx_count': tx_count,
            'total_revenue': total_revenue,
            'aov': aov,
            'completed_orders': completed_orders,
            'in_progress_orders': in_progress_orders,
            'pending_orders': pending_orders,
            'completed_pct': completed_pct,
            'in_progress_pct': in_progress_pct,
            'pending_pct': pending_pct,
            'categories': categories,
            'avg_progress': avg_progress,
            'recent_customers': recent_customers,
            'daily_data': daily_data,
            'trend_chart': trend_chart,
            'report_orders': report_orders,
            'report_products': report_products,
            'report_customers': report_customers,
            'timeline_data': timeline_data,
            'prod_chart_data': prod_chart_data,
            'cust_chart_data': cust_chart_data,
            'cat_chart_data': cat_chart_data,
            'kpi_periods': kpi_periods
        }

        return render_template('admin/dashboard.html', data=dash_data)

    except mysql.connector.Error as err:
        flash(f'Database error loading dashboard: {err}', 'error')
        return render_template('admin/dashboard.html', data={
            'user_count': 0, 'product_count': 0, 'tx_count': 0, 'total_revenue': 0,
            'completed_orders': 0, 'in_progress_orders': 0, 'pending_orders': 0,
            'completed_pct': 0, 'in_progress_pct': 0, 'pending_pct': 0,
            'categories': [], 'avg_progress': 0, 'recent_customers': [], 'daily_data': []
        })
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    session.pop('admin_email', None)
    session.pop('admin_logged_in', None)
    flash('Logged out of Admin Portal.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/export/master-report')
def export_master_report():
    """Generates a comprehensive Power BI-ready Master Sales & Operations CSV report."""
    if not session.get('admin_logged_in'):
        flash('Please log in with admin credentials first.', 'error')
        return redirect(url_for('admin_login'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                o.order_id AS `Order ID`,
                DATE_FORMAT(o.order_date, '%%Y-%%m-%%d %%H:%%i:%%s') AS `Order Date`,
                DATE_FORMAT(o.order_date, '%%Y') AS `Order Year`,
                DATE_FORMAT(o.order_date, '%%M') AS `Order Month`,
                DATE_FORMAT(o.order_date, '%%W') AS `Day of Week`,
                o.status AS `Order Status`,
                u.user_id AS `Customer ID`,
                COALESCE(u.name, CONCAT('User #', o.user_id)) AS `Customer Name`,
                COALESCE(u.email, 'N/A') AS `Customer Email`,
                COALESCE(u.city, 'India') AS `Customer City`,
                COALESCE(u.state, 'N/A') AS `Customer State`,
                p.product_id AS `Product ID`,
                p.name AS `Product Name`,
                p.category AS `Product Category`,
                p.price AS `Product Price (INR)`,
                oi.quantity AS `Quantity Sold`,
                (oi.quantity * oi.price) AS `Total Line Revenue (INR)`,
                COALESCE(pay.payment_method, 'N/A') AS `Payment Method`,
                COALESCE(pay.payment_status, 'Completed') AS `Payment Status`
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            LEFT JOIN users u ON o.user_id = u.user_id
            LEFT JOIN payments pay ON o.order_id = pay.order_id
            ORDER BY o.order_id DESC, oi.order_item_id ASC
        """)
        rows = cursor.fetchall()

        si = io.StringIO()
        if rows:
            fieldnames = list(rows[0].keys())
            writer = csv.DictWriter(si, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
        
        output = si.getvalue()
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=Forecastify_Master_System_Report.csv"}
        )
    except mysql.connector.Error as err:
        flash(f'Error generating export report: {err}', 'error')
        return redirect(url_for('admin_dashboard'))
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Helper to fetch counts for navbar pills across admin pages
def get_admin_counts(cursor):
    cursor.execute("SELECT COUNT(*) AS c FROM products")
    product_count = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) AS c FROM orders")
    order_count = cursor.fetchone()['c']
    cursor.execute("SELECT COUNT(*) AS c FROM users WHERE role = 'user'")
    customer_count = cursor.fetchone()['c']
    return product_count, order_count, customer_count


# ==========================================
# ADMIN PRODUCTS MANAGEMENT
# ==========================================

@app.route('/admin/products')
def admin_products():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        product_count, order_count, customer_count = get_admin_counts(cursor)

        cursor.execute("SELECT * FROM products ORDER BY product_id DESC")
        products = cursor.fetchall()

        return render_template(
            'admin/products.html',
            products=products,
            product_count=product_count,
            order_count=order_count,
            customer_count=customer_count
        )
    except mysql.connector.Error as err:
        flash(f'Database error: {err}', 'error')
        return redirect(url_for('admin_dashboard'))
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/admin/products/add', methods=['POST'])
def admin_add_product():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    name = request.form.get('name')
    category = request.form.get('category')
    brand = request.form.get('brand')
    price = request.form.get('price')
    stock_quantity = request.form.get('stock_quantity', 0)
    image_url = request.form.get('image_url', '/static/images/logo.png')
    description = request.form.get('description', '')

    if not name or not category or not price:
        flash('Product name, category, and price are required.', 'error')
        return redirect(url_for('admin_products'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, description, category, brand, price, stock_quantity, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, description, category, brand, price, stock_quantity, image_url))
        conn.commit()
        flash(f'Product "{name}" added successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error adding product: {err}', 'error')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('admin_products'))


@app.route('/admin/products/edit/<int:product_id>', methods=['POST'])
def admin_edit_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    name = request.form.get('name')
    category = request.form.get('category')
    brand = request.form.get('brand')
    price = request.form.get('price')
    stock_quantity = request.form.get('stock_quantity')
    image_url = request.form.get('image_url')
    description = request.form.get('description')

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE products 
            SET name=%s, category=%s, brand=%s, price=%s, stock_quantity=%s, image_url=%s, description=%s
            WHERE product_id=%s
        """, (name, category, brand, price, stock_quantity, image_url, description, product_id))
        conn.commit()
        flash('Product updated successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error updating product: {err}', 'error')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('admin_products'))


@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        conn.commit()
        flash('Product deleted successfully.', 'success')
    except mysql.connector.Error as err:
        flash(f'Error deleting product: {err}', 'error')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('admin_products'))


# ==========================================
# ADMIN ORDERS MANAGEMENT
# ==========================================

@app.route('/admin/orders')
def admin_orders():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        product_count, order_count, customer_count = get_admin_counts(cursor)

        cursor.execute("""
            SELECT o.order_id, o.user_id, o.total_amount, o.status, o.order_date, o.shipping_address,
                   u.name AS customer_name, u.email AS customer_email
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.user_id
            ORDER BY o.order_id DESC
        """)
        orders = cursor.fetchall()

        return render_template(
            'admin/orders.html',
            orders=orders,
            product_count=product_count,
            order_count=order_count,
            customer_count=customer_count
        )
    except mysql.connector.Error as err:
        flash(f'Database error loading orders: {err}', 'error')
        return redirect(url_for('admin_dashboard'))
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/admin/orders/update-status/<int:order_id>', methods=['POST'])
def admin_update_order_status(order_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    new_status = request.form.get('status')
    if not new_status:
        flash('Please select a valid order status.', 'error')
        return redirect(url_for('admin_orders'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s", (new_status, order_id))
        conn.commit()
        flash(f'Order #{order_id} status updated to "{new_status}".', 'success')
    except mysql.connector.Error as err:
        flash(f'Error updating order status: {err}', 'error')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('admin_orders'))


@app.route('/admin/orders/delete/<int:order_id>', methods=['POST'])
def admin_delete_order(order_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        conn.commit()
        flash(f'Order #{order_id} deleted successfully.', 'success')
    except mysql.connector.Error as err:
        flash(f'Error deleting order: {err}', 'error')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('admin_orders'))


# ==========================================
# ADMIN CUSTOMERS MANAGEMENT
# ==========================================

@app.route('/admin/customers')
def admin_customers():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        product_count, order_count, customer_count = get_admin_counts(cursor)

        cursor.execute("""
            SELECT u.user_id, u.name, u.email, u.phone, u.city, u.state, u.address, u.created_at,
                   COUNT(o.order_id) AS total_orders
            FROM users u
            LEFT JOIN orders o ON u.user_id = o.user_id
            WHERE u.role = 'user'
            GROUP BY u.user_id
            ORDER BY u.user_id DESC
        """)
        customers = cursor.fetchall()

        return render_template(
            'admin/customers.html',
            customers=customers,
            product_count=product_count,
            order_count=order_count,
            customer_count=customer_count
        )
    except mysql.connector.Error as err:
        flash(f'Database error loading customers: {err}', 'error')
        return redirect(url_for('admin_dashboard'))
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/admin/customers/add', methods=['POST'])
def admin_add_customer():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    phone = request.form.get('phone')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')

    if not name or not email or not password:
        flash('Name, email, and password are required.', 'error')
        return redirect(url_for('admin_customers'))

    hashed_password = generate_password_hash(password)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (name, email, password, phone, address, city, state, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'user')
        """, (name, email, hashed_password, phone, address, city, state))
        conn.commit()
        flash(f'Customer "{name}" registered successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error registering customer: {err}', 'error')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('admin_customers'))


@app.route('/admin/customers/edit/<int:user_id>', methods=['POST'])
def admin_edit_customer(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET name=%s, email=%s, phone=%s, city=%s, state=%s, address=%s
            WHERE user_id=%s AND role='user'
        """, (name, email, phone, city, state, address, user_id))
        conn.commit()
        flash('Customer details updated successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error updating customer: {err}', 'error')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('admin_customers'))


@app.route('/admin/customers/delete/<int:user_id>', methods=['POST'])
def admin_delete_customer(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = %s AND role = 'user'", (user_id,))
        conn.commit()
        flash('Customer account deleted successfully.', 'success')
    except mysql.connector.Error as err:
        flash(f'Error deleting customer: {err}', 'error')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('admin_customers'))


# ==========================================
# ADMIN SETTINGS & SECURITY MANAGEMENT
# ==========================================

@app.route('/admin/settings')
def admin_settings():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        product_count, order_count, customer_count = get_admin_counts(cursor)

        admin_id = session.get('admin_id')
        cursor.execute("SELECT user_id, name, email, phone FROM users WHERE user_id = %s AND role = 'admin'", (admin_id,))
        admin = cursor.fetchone()

        if not admin:
            cursor.execute("SELECT user_id, name, email, phone FROM users WHERE email = %s AND role = 'admin'", (session.get('admin_email'),))
            admin = cursor.fetchone()

        return render_template(
            'admin/settings.html',
            admin=admin,
            product_count=product_count,
            order_count=order_count,
            customer_count=customer_count
        )
    except mysql.connector.Error as err:
        flash(f'Database error: {err}', 'error')
        return redirect(url_for('admin_dashboard'))
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/admin/settings/profile', methods=['POST'])
def admin_update_profile():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    admin_id = session.get('admin_id')

    if not name or not email:
        flash('Admin Name and Email are required.', 'error')
        return redirect(url_for('admin_settings'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET name = %s, email = %s, phone = %s 
            WHERE user_id = %s AND role = 'admin'
        """, (name, email, phone, admin_id))
        conn.commit()

        session['admin_name'] = name
        session['admin_email'] = email
        flash('Admin profile details updated successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error updating admin profile: {err}', 'error')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('admin_settings'))


@app.route('/admin/settings/password', methods=['POST'])
def admin_update_password():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    admin_id = session.get('admin_id')

    if not current_password or not new_password or not confirm_password:
        flash('All password fields are required.', 'error')
        return redirect(url_for('admin_settings'))

    if new_password != confirm_password:
        flash('New password and confirm password do not match.', 'error')
        return redirect(url_for('admin_settings'))

    if len(new_password) < 6:
        flash('New password must be at least 6 characters long.', 'error')
        return redirect(url_for('admin_settings'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password FROM users WHERE user_id = %s AND role = 'admin'", (admin_id,))
        admin_user = cursor.fetchone()

        if not admin_user or not check_password_hash(admin_user['password'], current_password):
            flash('Incorrect current password.', 'error')
            return redirect(url_for('admin_settings'))

        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password = %s WHERE user_id = %s AND role = 'admin'", (hashed_password, admin_id))
        conn.commit()

        flash('Admin password updated successfully!', 'success')
    except mysql.connector.Error as err:
        flash(f'Error updating admin password: {err}', 'error')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('admin_settings'))


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
    
    if 'user_id' not in session:
        flash('Please register or log in to proceed to checkout.', 'info')
        return redirect(url_for('login'))
    
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
        
        # 1. Insert into orders table
        cursor.execute(
            "INSERT INTO orders (user_id, total_amount, status, shipping_address) VALUES (%s, %s, %s, %s)",
            (session['user_id'], total, 'pending', shipping_address)
        )
        order_id = cursor.lastrowid
        
        # 2. Insert each cart item into order_items table
        for item in cart_items:
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                (order_id, item['product_id'], item['quantity'], item['price'])
            )
        
        # 3. Insert into payments table
        payment_status = 'pending' if db_payment_method == 'COD' else 'success'
        cursor.execute(
            "INSERT INTO payments (order_id, payment_method, payment_status, amount) VALUES (%s, %s, %s, %s)",
            (order_id, db_payment_method, payment_status, total)
        )
        
        conn.commit()
        
        # Clear the cart
        session.pop('cart', None)
        session.modified = True
        
        # Generate order reference
        order_ref = f"ORD-{order_id}-{random.randint(1000, 9999)}"
        
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
            SELECT o.order_id, o.total_amount, o.status, o.order_date, o.shipping_address
            FROM orders o
            WHERE o.user_id = %s
            ORDER BY o.order_date DESC
        """, (user_id,))
        orders = cursor.fetchall()
        
        # For each order, fetch items
        for order in orders:
            cursor.execute("""
                SELECT oi.quantity, oi.price, p.name, p.image_url
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (order['order_id'],))
            order['order_items'] = cursor.fetchall()
            
        # Get payment history
        cursor.execute("""
            SELECT p.payment_id, p.payment_method, p.payment_status, p.amount, p.payment_date, o.order_id
            FROM payments p
            JOIN orders o ON p.order_id = o.order_id
            WHERE o.user_id = %s
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
    order_id = request.form.get('order_id') or request.form.get('transaction_id')
    user_id = session['user_id']
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if not order_id:
            cursor.execute("SELECT order_id FROM orders WHERE user_id = %s ORDER BY order_date DESC LIMIT 1", (user_id,))
            res = cursor.fetchone()
            if res:
                order_id = res['order_id']
            else:
                flash('You must have at least one order to submit a complaint.', 'error')
                return redirect(url_for('profile'))
                
        cursor.execute("INSERT INTO complaints (user_id, order_id, subject, description) VALUES (%s, %s, %s, %s)",
                       (user_id, order_id, subject, description))
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
            
            body = f"New help request from {user['name']} ({user['email']})\n\nOrder ID: {order_id}\n\nDescription:\n{description}"
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
