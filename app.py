from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    trending_orders = [
        {'item': 'T-shirt', 'price': 10, 'image': 'tshirt.jfif','brand':'abibas'},
        {'item': 'Mug', 'price': 7, 'image': 'mug.jfif','brand':'milton'},
        {'item': 'Cap', 'price': 5, 'image': 'cap.jfif','brand':'yankees'}
    ]
    return render_template('Home.html', trending_orders=trending_orders)

if __name__ == '__main__':
    app.run(debug=True)
