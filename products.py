from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    # Example product data
    product = {
        'name': 'Custom T-Shirt',
        'type': 'Apparel',
        'color': 'White',
        'price': 19.99
    }

    custom_text = ""

    if request.method == 'POST':
        custom_text = request.form.get('custom_text', '')

    return render_template('Product.html', product=product, custom_text=custom_text)

if __name__ == '__main__':
    app.run(debug=True)
