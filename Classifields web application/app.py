from flask import Flask, render_template, request, redirect, session
from models import db, User, Product
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'classifieds_secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///classifieds.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.before_request
def setup():
    db.create_all()

@app.route('/')
def index():
    products = Product.query.order_by(Product.timestamp.desc()).all()
    return render_template('index.html', products=products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.id
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    products = Product.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', products=products)

@app.route('/new', methods=['GET', 'POST'])
def new_listing():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        product = Product(title=title, description=description, price=price, user_id=user_id, timestamp=datetime.now())
        db.session.add(product)
        db.session.commit()
        return redirect('/dashboard')
    return render_template('new_listing.html')

@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    seller = User.query.get(product.user_id)
    return render_template('product.html', product=product, seller=seller)

if __name__ == '__main__':
    app.run(debug=True)
