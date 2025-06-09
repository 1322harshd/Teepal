from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('teepal.db')
    conn.row_factory = sqlite3.Row
    return conn

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
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']


        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            error = "Please enter a valid email address."

        elif len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[0-9]', password):
            error = "Password must be at least 8 characters and include uppercase, lowercase, and a number."
        elif password != confirm_password:
            error = "Passwords do not match."
        else:
            conn = get_db_connection()
            user_email = conn.execute('SELECT * FROM Users WHERE Email = ?', (email,)).fetchone()
            user_name = conn.execute('SELECT * FROM Users WHERE Name = ?', (username,)).fetchone()
            if user_email:
                error = "Email already registered."
            elif user_name:
                error = "Username already taken."
            else:
                hashed_password = generate_password_hash(password)
                conn.execute(
                    'INSERT INTO Users (Name, Email, Password) VALUES (?, ?, ?)',
                    (username, email, hashed_password)
                )
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
            conn.close()
    return render_template('signup.html', error=error)

@app.route('/')
def home():
    trending_orders = [
        {'item': 'T-shirt', 'price': 10, 'image': 'products/tshirt.jfif', 'brand': 'abibas'},
        {'item': 'Mug', 'price': 7, 'image': 'products/mug.jfif', 'brand': 'milton'},
        {'item': 'Cap', 'price': 5, 'image': 'products/cap.jfif', 'brand': 'yankees'}
    ]
    recent_orders = [
        {'item': 'Bottle', 'price': 12, 'image': 'products/Unknown.jpeg', 'brand': 'milton'},
        {'item': 'Bag', 'price': 20, 'image': 'products/bag.jpeg', 'brand': 'wildcraft'},
        {'item': 'Shoes', 'price': 50, 'image': 'products/shoes.jpeg', 'brand': 'nike'}
    ]
    my_orders = [
        {'item': 'Notebook', 'price': 3, 'image': 'products/notebook.jpeg', 'brand': 'classmate'},
        {'item': 'Pen', 'price': 1, 'image': 'products/pen.png', 'brand': 'pilot'},
        {'item': 'Watch', 'price': 100, 'image': 'products/watch.jpeg', 'brand': 'casio'}
    ]
    return render_template(
        'Home.html',
        trending_orders=trending_orders,
        recent_orders=recent_orders,
        my_orders=my_orders
    )

@app.route('/shopping_cart')
def shopping_cart():
    cart_items = [
        {'item': 'T-shirt', 'price': 10, 'image': 'products/tshirt.jfif', 'brand': 'abibas'},
        {'item': 'Mug', 'price': 7, 'image': 'products/mug.jfif', 'brand': 'milton'},
        {'item': 'Cap', 'price': 5, 'image': 'products/cap.jfif', 'brand': 'yankees'}
    ]
    return render_template('shopping_cart.html', products=cart_items)

@app.route('/saved_items')
def saved_items():
    saved_items = [
        {'item': 'T-shirt', 'price': 10, 'image': 'products/tshirt.jfif', 'brand': 'abibas'},
        {'item': 'Mug', 'price': 7, 'image': 'products/mug.jfif', 'brand': 'milton'},
        {'item': 'Cap', 'price': 5, 'image': 'products/cap.jfif', 'brand': 'yankees'}
    ]
    return render_template('saved_items.html', products=saved_items)

@app.route('/orders')
def orders():
    orders = [
        {'item': 'T-shirt', 'price': 10, 'image': 'products/tshirt.jfif', 'brand': 'abibas'},
        {'item': 'Mug', 'price': 7, 'image': 'products/mug.jfif', 'brand': 'milton'},
        {'item': 'Cap', 'price': 5, 'image': 'products/cap.jfif', 'brand': 'yankees'}
    ]
    return render_template('orders.html', products=orders)

if __name__ == '__main__':
    app.run(debug=True)
