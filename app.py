from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import re
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = os.path.join('static', 'users')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    conn = sqlite3.connect('teepal.db')
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username_or_email = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM Users WHERE Email = ? OR Name = ?', 
            (username_or_email, username_or_email)
        ).fetchone()
        conn.close()
        if user and check_password_hash(user['Password'], password):
            session['logged_in'] = True
            session['username'] = user['Name']
            session['user_id'] = user['UserId']
            session['display_name'] = user['DisplayName']
            session['user_image'] = user['Image']
            return redirect(url_for('home'))
        else:
            error = 'Invalid credentials'
    return render_template('login.html', error=error)


@app.route('/logout_and_home')
def logout_and_home():
    session.clear()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        display_name = request.form['display_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        security_question = request.form['security_question']
        security_answer = request.form['security_answer']
        file = request.files.get('profile_image')

        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            error = "Please enter a valid email address."
        elif len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[0-9]', password):
            error = "Password must be at least 8 characters and include uppercase, lowercase, and a number."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif not file or not allowed_file(file.filename):
            error = "Please upload a valid image file."
        else:
            with get_db_connection() as conn:
                user_email = conn.execute('SELECT * FROM Users WHERE Email = ?', (email,)).fetchone()
                user_name = conn.execute('SELECT * FROM Users WHERE Name = ?', (username,)).fetchone()
                if user_email:
                    error = "Email already registered."
                elif user_name:
                    error = "Username already taken."
                else:
                    filename = secure_filename(f"{username}_{file.filename}")
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    hashed_password = generate_password_hash(password)
                    conn.execute(
                        'INSERT INTO Users (Name, DisplayName, Email, Password, Image, SecurityQuestion, SecurityAnswer) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (username, display_name, email, hashed_password, filename, security_question, security_answer)
                    )
                    conn.commit()
                    return redirect(url_for('login'))
    return render_template('signup.html', error=error)

@app.route('/')
def home():
    with get_db_connection() as conn:
        # Trending: top 3 most ordered products
        trending_orders = conn.execute(
            '''
            SELECT Products.*, SUM(OrderDetails.Quantity) as total_ordered
            FROM OrderDetails
            JOIN Products ON OrderDetails.ProductId = Products.ProductId
            GROUP BY Products.ProductId
            ORDER BY total_ordered DESC
            LIMIT 3
            '''
        ).fetchall()

        # Recent: 3 most recently ordered products
        recent_orders = conn.execute(
            '''
            SELECT Products.*, MAX(Orders.OrderedAt) as last_ordered
            FROM OrderDetails
            JOIN Products ON OrderDetails.ProductId = Products.ProductId
            JOIN Orders ON OrderDetails.OrderId = Orders.OrderId
            GROUP BY Products.ProductId
            ORDER BY last_ordered DESC
            LIMIT 3
            '''
        ).fetchall()

        my_orders = []
        if session.get('logged_in'):
            user_id = session['user_id']
            my_orders = conn.execute(
                '''
                SELECT Products.*, OrderDetails.Quantity, OrderDetails.PriceAtPurchase, Orders.OrderedAt
                FROM Orders
                JOIN OrderDetails ON Orders.OrderId = OrderDetails.OrderId
                JOIN Products ON OrderDetails.ProductId = Products.ProductId
                WHERE Orders.UserId = ?
                ORDER BY Orders.OrderedAt DESC
                LIMIT 3
                ''', (user_id,)
            ).fetchall()

    return render_template(
        'Home.html',
        trending_orders=trending_orders,
        recent_orders=recent_orders,
        my_orders=my_orders
    )

@app.route('/shopping_cart')
def shopping_cart():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_id = session['user_id']
    with get_db_connection() as conn:
        cart_items = conn.execute(
            '''SELECT Products.*, CartItems.Quantity FROM CartItems
               JOIN Products ON CartItems.ProductId = Products.ProductId
               WHERE CartItems.UserId = ?''', (user_id,)
        ).fetchall()
    return render_template('shopping_cart.html', products=cart_items)

@app.route('/saved_items')
def saved_items():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_id = session['user_id']
    with get_db_connection() as conn:
        saved_items = conn.execute(
            '''SELECT Products.* FROM SavedItems
               JOIN Products ON SavedItems.ProductId = Products.ProductId
               WHERE SavedItems.UserId = ?''', (user_id,)
        ).fetchall()
    return render_template('saved_items.html', products=saved_items)

@app.route('/orders')
def orders():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_id = session['user_id']
    with get_db_connection() as conn:
        orders = conn.execute(
            '''
            SELECT Products.*, Orders.OrderId, Orders.OrderedAt, OrderDetails.Quantity, OrderDetails.PriceAtPurchase
            FROM Orders
            JOIN OrderDetails ON Orders.OrderId = OrderDetails.OrderId
            JOIN Products ON OrderDetails.ProductId = Products.ProductId
            WHERE Orders.UserId = ?
            ORDER BY Orders.OrderedAt DESC
            ''', (user_id,)
        ).fetchall()
    return render_template('orders.html', products=orders)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    message = None
    security_question = None
    if request.method == 'POST':
        email = request.form['email']
        security_answer = request.form.get('security_answer')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')

        with get_db_connection() as conn:
            user = conn.execute('SELECT * FROM Users WHERE Email = ?', (email,)).fetchone()
            if not user:
                message = "If this email is registered, a password reset option will appear."
            elif not security_answer:
                # Show security question
                q_map = {
                    "pet": "What is the name of your first pet?",
                    "school": "What is the name of your elementary school?",
                    "city": "In what city were you born?",
                    "mother_maiden": "What is your mother's maiden name?",
                    "favorite_food": "What is your favorite food?"
                }
                security_question = q_map.get(user['SecurityQuestion'], "Security Question")
                return render_template('forgot_password.html', security_question=security_question, email=email)
            else:
                # Check answer and reset password
                if security_answer.strip().lower() != user['SecurityAnswer'].strip().lower():
                    message = "Incorrect answer to the security question."
                    security_question = {
                        "pet": "What is the name of your first pet?",
                        "school": "What is the name of your elementary school?",
                        "city": "In what city were you born?",
                        "mother_maiden": "What is your mother's maiden name?",
                        "favorite_food": "What is your favorite food?"
                    }.get(user['SecurityQuestion'], "Security Question")
                    return render_template('forgot_password.html', security_question=security_question, email=email, message=message)
                elif new_password != confirm_new_password:
                    message = "Passwords do not match."
                    security_question = {
                        "pet": "What is the name of your first pet?",
                        "school": "What is the name of your elementary school?",
                        "city": "In what city were you born?",
                        "mother_maiden": "What is your mother's maiden name?",
                        "favorite_food": "What is your favorite food?"
                    }.get(user['SecurityQuestion'], "Security Question")
                    return render_template('forgot_password.html', security_question=security_question, email=email, message=message)
                elif len(new_password) < 8 or not re.search(r'[A-Z]', new_password) or not re.search(r'[a-z]', new_password) or not re.search(r'[0-9]', new_password):
                    message = "Password must be at least 8 characters and include uppercase, lowercase, and a number."
                    security_question = {
                        "pet": "What is the name of your first pet?",
                        "school": "What is the name of your elementary school?",
                        "city": "In what city were you born?",
                        "mother_maiden": "What is your mother's maiden name?",
                        "favorite_food": "What is your favorite food?"
                    }.get(user['SecurityQuestion'], "Security Question")
                    return render_template('forgot_password.html', security_question=security_question, email=email, message=message)
                else:
                    hashed_password = generate_password_hash(new_password)
                    conn.execute('UPDATE Users SET Password = ? WHERE Email = ?', (hashed_password, email))
                    conn.commit()
                    message = "Password reset successful. You can now log in."
    return render_template('forgot_password.html', security_question=security_question, message=message)

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user_id = session['user_id']
    quantity = int(request.form.get('quantity', 1))

    with get_db_connection() as conn:
        existing = conn.execute(
            'SELECT * FROM CartItems WHERE UserId = ? AND ProductId = ?', (user_id, product_id)
        ).fetchone()

        if existing:
            conn.execute(
                'UPDATE CartItems SET Quantity = Quantity + ? WHERE UserId = ? AND ProductId = ?',
                (quantity, user_id, product_id)
            )
        else:
            conn.execute(
                'INSERT INTO CartItems (UserId, ProductId, Quantity) VALUES (?, ?, ?)',
                (user_id, product_id, quantity)
            )
        conn.commit()
    return redirect(url_for('product', product_id=product_id))


@app.route('/save_item/<int:product_id>', methods=['POST'])
def save_item(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_id = session['user_id']
    with get_db_connection() as conn:
        exists = conn.execute(
            'SELECT * FROM SavedItems WHERE UserId = ? AND ProductId = ?', (user_id, product_id)
        ).fetchone()
        if not exists:
            conn.execute(
                'INSERT INTO SavedItems (UserId, ProductId) VALUES (?, ?)',
                (user_id, product_id)
            )
            conn.commit()
    return redirect(url_for('saved_items'))

# Product page route
@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    with get_db_connection() as conn:
        product = conn.execute('SELECT * FROM Products WHERE ProductId = ?', (product_id,)).fetchone()
        if not product:
            return "Product not found", 404
        custom_text = request.form.get('custom_text', '') if request.method == 'POST' else ''
        if request.method == 'POST':
            conn.execute(
                'INSERT INTO CustomRequests (UserId, ProductId, CustomText, Status) VALUES (?, ?, ?, ?)',
                (session['user_id'], product_id, custom_text, 'pending')
            )
            conn.commit()
    return render_template('product.html', product=product, custom_text=custom_text)

if __name__ == '__main__':
    app.run(debug=True)
