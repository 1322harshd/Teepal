from flask import Flask, render_template

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
