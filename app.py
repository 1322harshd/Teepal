from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    trending_orders = [
        {'item': 'T-shirt', 'price': 10, 'image': 'tshirt.jfif','brand':'abibas'},
        {'item': 'Mug', 'price': 7, 'image': 'mug.jfif','brand':'milton'},
        {'item': 'Cap', 'price': 5, 'image': 'cap.jfif','brand':'yankees'}
    ]
    recent_orders = [
        {'item': 'Bottle', 'price': 12, 'image': 'Unknown.jpeg','brand':'milton'},
        {'item': 'Bag', 'price': 20, 'image': 'bag.jpeg','brand':'wildcraft'},
        {'item': 'Shoes', 'price': 50, 'image': 'shoes.jpeg','brand':'nike'}
    ]
    my_orders = [
        {'item': 'Notebook', 'price': 3, 'image': 'notebook.jpeg','brand':'classmate'},
        {'item': 'Pen', 'price': 1, 'image': 'pen.png','brand':'pilot'},
        {'item': 'Watch', 'price': 100, 'image': 'watch.jpeg','brand':'casio'}
    ]
    return render_template(
        'Home.html',
        trending_orders=trending_orders,
        recent_orders=recent_orders,
        my_orders=my_orders
    )

if __name__ == '__main__':
    app.run(debug=True)
