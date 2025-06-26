from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import re
import os
from datetime import datetime, timedelta
import base64

# create flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # set secret key for sessions

# print static directory contents for debugging
print(os.listdir('static'))

# set upload folder for user images
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'users')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# function to get a database connection
def get_db_connection():
    conn = sqlite3.connect('teepal.db')
    conn.row_factory = sqlite3.Row
    return conn

# function to check if a file is allowed based on extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from flask import session

# clear session once after server starts
def clear_session_once():
    if not hasattr(app, 'session_cleared'):
        session.clear()
        app.session_cleared = True

# run clear_session_once before every request
app.before_request(clear_session_once)

# login route for users and admin
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username_or_email = request.form['username']
        password = request.form['password']
        # check for admin login
        admin_username = 'admin'
        admin_password = 'admin123'
        if username_or_email == admin_username and password == admin_password:
            session['logged_in'] = True
            session['is_admin'] = True
            session['username'] = admin_username
            return redirect(url_for('admin_dashboard'))
        # check for user login
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

# logout route that also redirects to home
@app.route('/logout_and_home')
def logout_and_home():
    session.clear()
    return redirect(url_for('home'))

# user registration route
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

        # validate email and password
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
                    # save user profile image
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    # hash password and insert user into database
                    hashed_password = generate_password_hash(password)
                    conn.execute(
                        'INSERT INTO Users (Name, DisplayName, Email, Password, Image, SecurityQuestion, SecurityAnswer) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (username, display_name, email, hashed_password, filename, security_question, security_answer)
                    )
                    conn.commit()
                    return redirect(url_for('login'))
    return render_template('signup.html', error=error)

# home page route
@app.route('/')
def home():
    with get_db_connection() as conn:
        # get trending products based on order quantity
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

        # get most recently ordered products
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

        # get recent orders for the logged-in user
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

# shopping cart page route
@app.route('/shopping_cart')
def shopping_cart():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_id = session['user_id']
    with get_db_connection() as conn:
        # get all products in the user's cart
        cart_items = conn.execute(
            '''SELECT Products.*, CartItems.Quantity, CartItems.Size FROM CartItems
               JOIN Products ON CartItems.ProductId = Products.ProductId
               WHERE CartItems.UserId = ?''', (user_id,)
        ).fetchall()
    return render_template('shopping_cart.html', products=cart_items)

# save custom design for a product
@app.route('/save_design/<int:product_id>', methods=['POST'])
def save_design(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_id = session['user_id']
    design_data = request.form.get('design_data')
    if not design_data:
        return "No design data", 400
    # create directory for saved designs if it doesn't exist
    design_dir = os.path.join(app.root_path, 'static', 'saved_designs')
    os.makedirs(design_dir, exist_ok=True)
    # generate filename for the design image
    filename = f"user{user_id}_product{product_id}_{int(datetime.now().timestamp())}.png"
    filepath = os.path.join(design_dir, filename)
    # remove base64 header if present
    if ',' in design_data:
        design_data = design_data.split(',')[1]
    # save the image file
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(design_data))
    # save reference to the design in the SavedItems table
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO SavedItems (UserId, ProductId, Size, DesignImage) VALUES (?, ?, ?, ?)',
            (user_id, product_id, request.form.get('size', 'M'), f"saved_designs/{filename}")
        )
        conn.commit()
    return redirect(url_for('saved_items'))

# show all saved items for the user
@app.route('/saved_items')
def saved_items():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_id = session['user_id']
    with get_db_connection() as conn:
        # get all saved items for the user
        saved_items = conn.execute(
            '''SELECT Products.*, SavedItems.DesignImage FROM SavedItems
               JOIN Products ON SavedItems.ProductId = Products.ProductId
               WHERE SavedItems.UserId = ?''', (user_id,)
        ).fetchall()
    return render_template('saved_items.html', products=saved_items)

# show all orders for the user
@app.route('/orders')
def orders():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_id = session['user_id']
    with get_db_connection() as conn:
        # get all orders and their details for the user
        orders = conn.execute(
            '''SELECT Orders.OrderId, Orders.OrderedAt, Orders.ArrivalDate, Orders.Status, 
                      Products.Brand, Products.Item, Products.Image, OrderDetails.Quantity, OrderDetails.PriceAtPurchase
               FROM Orders
               JOIN OrderDetails ON Orders.OrderId = OrderDetails.OrderId
               JOIN Products ON OrderDetails.ProductId = Products.ProductId
               WHERE Orders.UserId = ?
               ORDER BY Orders.OrderedAt DESC''', (user_id,)
        ).fetchall()
    return render_template('orders.html', products=orders)

# forgot password route with security question and password reset
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
                # show security question if answer not provided yet
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
                # check security answer and password requirements
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
                    # update password in database
                    hashed_password = generate_password_hash(new_password)
                    conn.execute('UPDATE Users SET Password = ? WHERE Email = ?', (hashed_password, email))
                    conn.commit()
                    message = "Password reset successful. You can now log in."
    return render_template('forgot_password.html', security_question=security_question, message=message)

# add a product to the shopping cart, or increase quantity if it already exists
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_id = session['user_id']
    size = request.form.get('size', 'M')  # default size is 'M'
    with get_db_connection() as conn:
        # check if item already exists in cart for this user and size
        existing = conn.execute(
            'SELECT * FROM CartItems WHERE UserId = ? AND ProductId = ? AND (Size = ? OR Size IS NULL)',
            (user_id, product_id, size)
        ).fetchone()
        if existing:
            # increase quantity by 1 if already exists
            conn.execute(
                'UPDATE CartItems SET Quantity = Quantity + 1 WHERE UserId = ? AND ProductId = ? AND (Size = ? OR Size IS NULL)',
                (user_id, product_id, size)
            )
        else:
            # add new item to cart
            conn.execute(
                'INSERT INTO CartItems (UserId, ProductId, Quantity, Size) VALUES (?, ?, ?, ?)',
                (user_id, product_id, 1, size)
            )
        conn.commit()
    return redirect(url_for('shopping_cart'))

# save an item to the user's saved items
@app.route('/save_item/<int:product_id>', methods=['POST'])
def save_item(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_id = session['user_id']
    size = request.form.get('size', 'M')
    with get_db_connection() as conn:
        # check if item is already saved
        exists = conn.execute(
            'SELECT * FROM SavedItems WHERE UserId = ? AND ProductId = ? AND (Size = ? OR Size IS NULL)',
            (user_id, product_id, size)
        ).fetchone()
        if not exists:
            # save item if not already saved
            conn.execute(
                'INSERT INTO SavedItems (UserId, ProductId, Size) VALUES (?, ?, ?)',
                (user_id, product_id, size)
            )
            conn.commit()
    return redirect(url_for('saved_items'))

# remove an item from the shopping cart
@app.route('/remove_item/<int:product_id>', methods=['POST'])
def remove_item(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_id = session['user_id']
    with get_db_connection() as conn:
        # delete item from cart
        conn.execute(
            'DELETE FROM CartItems WHERE UserId = ? AND ProductId = ?', (user_id, product_id)
        )
        conn.commit()
    return redirect(url_for('shopping_cart'))

# remove an item from saved items
@app.route('/remove_saved_item/<int:product_id>', methods=['POST'])
def remove_saved_item(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_id = session['user_id']
    with get_db_connection() as conn:
        # delete item from saved items
        conn.execute(
            'DELETE FROM SavedItems WHERE UserId = ? AND ProductId = ?', (user_id, product_id)
        )
        conn.commit()
    return redirect(url_for('saved_items'))

# search for products by item name or brand
@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    products = []

    if query:
        with get_db_connection() as conn:
            products = conn.execute(
                '''
                SELECT * FROM Products
                WHERE Item LIKE ? OR Brand LIKE ?
                ''',
                (f'%{query}%', f'%{query}%')
            ).fetchall()

    return render_template('search_results.html', query=query, products=products)

# admin dashboard route
@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))
    with get_db_connection() as conn:
        # get all custom requests, orders, products, and users for admin
        custom_requests = conn.execute('SELECT * FROM CustomRequests').fetchall()
        orders = conn.execute('SELECT * FROM Orders').fetchall()
        products = conn.execute('SELECT * FROM Products').fetchall()
        users = conn.execute('SELECT * FROM Users').fetchall()
    return render_template('admin.html', custom_requests=custom_requests, orders=orders, products=products, users=users)

# approve a custom request (admin only)
@app.route('/admin/approve/<int:request_id>')
def approve_request(request_id):
    if not session.get('logged_in') or session.get('username') != 'admin':
        return redirect(url_for('login'))
    with get_db_connection() as conn:
        conn.execute('UPDATE CustomRequests SET Status = ? WHERE RequestId = ?', ('approved', request_id))
        conn.commit()
    return redirect(url_for('admin_dashboard'))

# reject a custom request (admin only)
@app.route('/admin/reject/<int:request_id>')
def reject_request(request_id):
    if not session.get('logged_in') or session.get('username') != 'admin':
        return redirect(url_for('login'))
    with get_db_connection() as conn:
        conn.execute('UPDATE CustomRequests SET Status = ? WHERE RequestId = ?', ('rejected', request_id))
        conn.commit()
    return redirect(url_for('admin_dashboard'))

# product details and custom request route
@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def product(product_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    design_image = request.args.get('design')
    with get_db_connection() as conn:
        product = conn.execute('SELECT * FROM Products WHERE ProductId = ?', (product_id,)).fetchone()
        if not product:
            return "Product not found", 404
        custom_text = request.form.get('custom_text', '') if request.method == 'POST' else ''
        if request.method == 'POST':
            # save custom request for the product
            conn.execute(
                'INSERT INTO CustomRequests (UserId, ProductId, CustomText, Status) VALUES (?, ?, ?, ?)',
                (session['user_id'], product_id, custom_text, 'pending')
            )
            conn.commit()
    return render_template('product.html', product=product, custom_text=custom_text, design_image=design_image)

# checkout route to place an order from cart
@app.route('/checkout', methods=['POST'])
def checkout():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_id = session['user_id']
    with get_db_connection() as conn:
        # get all items in the user's cart
        cart_items = conn.execute(
            '''SELECT Products.ProductId, Products.Price, CartItems.Quantity 
               FROM CartItems 
               JOIN Products ON CartItems.ProductId = Products.ProductId 
               WHERE CartItems.UserId = ?''', (user_id,)
        ).fetchall()
        if not cart_items:
            return redirect(url_for('shopping_cart'))

        # create new order with arrival date and status
        ordered_at = datetime.now()
        arrival_date = (ordered_at + timedelta(days=5)).strftime('%Y-%m-%d')
        status = 'Arriving'

        conn.execute(
            'INSERT INTO Orders (UserId, OrderedAt, ArrivalDate, Status) VALUES (?, ?, ?, ?)',
            (user_id, ordered_at, arrival_date, status)
        )
        order_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]

        # add order details for each item in cart
        for item in cart_items:
            conn.execute(
                'INSERT INTO OrderDetails (OrderId, ProductId, Quantity, PriceAtPurchase) VALUES (?, ?, ?, ?)',
                (order_id, item['ProductId'], item['Quantity'], item['Price'])
            )
        # clear the user's cart after order is placed
        conn.execute('DELETE FROM CartItems WHERE UserId = ?', (user_id,))
        conn.commit()

    return render_template('order_confirmation.html', arrival_date=arrival_date)

# product catalogue page and add to cart from catalogue
@app.route('/product_catalogue', methods=['GET', 'POST'])
def product_catalogue():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    user_id = session['user_id']
    with get_db_connection() as conn:
        products = conn.execute('SELECT * FROM Products').fetchall()
    # handle add to cart POST request
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        with get_db_connection() as conn:
            existing = conn.execute(
                'SELECT * FROM CartItems WHERE UserId = ? AND ProductId = ?', (user_id, product_id)
            ).fetchone()
            if existing:
                # increase quantity if already in cart
                conn.execute(
                    'UPDATE CartItems SET Quantity = Quantity + 1 WHERE UserId = ? AND ProductId = ?',
                    (user_id, product_id)
                )
            else:
                # add new item to cart
                conn.execute(
                    'INSERT INTO CartItems (UserId, ProductId, Quantity) VALUES (?, ?, ?)',
                    (user_id, product_id, 1)
                )
            conn.commit()
        return redirect(url_for('product_catalogue'))
    return render_template('product_catalogue.html', products=products)

from flask import flash

# admin route to edit a product's price
@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
def admin_edit_product(product_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))
    with get_db_connection() as conn:
        product = conn.execute('SELECT * FROM Products WHERE ProductId = ?', (product_id,)).fetchone()
        if not product:
            flash('Product not found.', 'danger')
            return redirect(url_for('admin_dashboard'))
        if request.method == 'POST':
            new_price = request.form.get('price')
            try:
                new_price = float(new_price)
                conn.execute('UPDATE Products SET Price = ? WHERE ProductId = ?', (new_price, product_id))
                conn.commit()
                flash('Price updated successfully.', 'success')
            except Exception:
                flash('Invalid price.', 'danger')
            return redirect(url_for('admin_dashboard'))
    return render_template('edit_product.html', product=product)

# admin route to edit a user's details
@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def admin_edit_user(user_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))
    with get_db_connection() as conn:
        user = conn.execute('SELECT * FROM Users WHERE UserId = ?', (user_id,)).fetchone()
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('admin_dashboard'))
        if request.method == 'POST':
            display_name = request.form.get('display_name')
            email = request.form.get('email')
            password = request.form.get('password')
            updates = []
            params = []
            if display_name:
                updates.append('DisplayName = ?')
                params.append(display_name)
            if email:
                updates.append('Email = ?')
                params.append(email)
            if password:
                hashed = generate_password_hash(password)
                updates.append('Password = ?')
                params.append(hashed)
            if updates:
                params.append(user_id)
                conn.execute(f'UPDATE Users SET {", ".join(updates)} WHERE UserId = ?', params)
                conn.commit()
                flash('User updated successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
    return render_template('edit_user.html', user=user)

# admin route to add a new product
@app.route('/admin/add_product', methods=['POST'])
def admin_add_product():
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))
    item = request.form.get('item')
    brand = request.form.get('brand')
    price = request.form.get('price')
    image_file = request.files.get('image')
    image_path = None
    if image_file and image_file.filename:
        filename = secure_filename(image_file.filename)
        image_folder = os.path.join(app.root_path, 'static', 'products')
        os.makedirs(image_folder, exist_ok=True)
        image_path = os.path.join('products', filename)
        image_file.save(os.path.join(image_folder, filename))
    with get_db_connection() as conn:
        # insert new product into database
        conn.execute(
            'INSERT INTO Products (Item, Brand, Price, Image) VALUES (?, ?, ?, ?)',
            (item, brand, price, image_path)
        )
        conn.commit()
    return redirect(url_for('admin_dashboard'))

# admin route to delete a product
@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    if not session.get('logged_in') or not session.get('is_admin'):
        return redirect(url_for('login'))
    with get_db_connection() as conn:
        # delete product from database
        conn.execute('DELETE FROM Products WHERE ProductId = ?', (product_id,))
        conn.commit()
    return redirect(url_for('admin_dashboard'))

# run the flask app in debug mode
if __name__ == '__main__':
    app.run(debug=True)