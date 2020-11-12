from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
import models
import forms
import sys
from numpy import dot
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer
import traceback
import datetime

#note - maiden default is "johnson"

app = Flask(__name__)
app.secret_key = 's3cr3t'
app.config.from_object('config')
db = SQLAlchemy(app, session_options={'autocommit': False})

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the username is just the primary key of our buyer table, use it in the query for the user
    return models.Buyers.query.get(user_id)

buyer = 'joshguo'

categories = ['Appliances', 'Beauty', 'Cell Phones and Accessories', 'Electronics', 'Fashion', 'Gift Cards', 'Industrial and Scientific', 'Luxury Beauty', 'Office Products', 'Pantry', 'Software', 'Video Games']

@app.route('/')
def home():
    items = {}
    username='joshguo'
    for category in categories:
        items[category] = db.session.query(models.Items).filter(models.Items.category == category).limit(10).all()
    cart = db.session.query(models.incart)\
        .filter(models.incart.buyer_username == username).all()
    if (cart is None):
        flash('Cart is empty!')
    return render_template('all-items.html', items=items)


#def all_drinkers():
#    drinkers = db.session.query(models.Drinker).all()
#    return render_template('all-drinkers.html', drinkers=drinkers)

@app.route('/item/<product_id>')
def item(product_id):
    items = db.session.query(models.Items)\
        .filter(models.Items.product_id == product_id).all()
    buyer = 'joshguo'
    return render_template('item.html', items=items, buyer=buyer)

# adds item to wishlist
@app.route('/add_wishlist/product_id=<product_id>&seller_username=<seller_username>&buyer_username=<buyer_username>')
def add_wishlist(product_id, seller_username, buyer_username):
    currItem = db.session.query(models.inwishlist).filter(models.inwishlist.product_id == product_id).filter(models.inwishlist.seller_username == models.inwishlist.seller_username).filter(models.inwishlist.buyer_username == models.inwishlist.buyer_username).all() # going to subtract quantity from this item
    if currItem:
        return redirect(url_for('add_quantity_wishlist', product_id=product_id, seller_username=seller_username, buyer_username=buyer_username)) # increase quantity by 1 if already in wish list
    else: # not in wishlist already
        db.session.execute('INSERT INTO inwishlist VALUES(:product_id, :seller_username, :buyer_username, 1)', dict(product_id=product_id, seller_username=seller_username, buyer_username=buyer_username))
        db.session.commit()
        return redirect(url_for('wishlist', username=buyer_username), code=307)

# decreases quantity by 1 for item in wishlist
@app.route('/subtract_quantity_wishlist/product_id=<product_id>&seller_username=<seller_username>&buyer_username=<buyer_username>')
def subtract_quantity_wishlist(product_id, seller_username, buyer_username):
    currItem = db.session.query(models.inwishlist).filter(models.inwishlist.product_id == product_id).filter(models.inwishlist.seller_username == models.inwishlist.seller_username).filter(models.inwishlist.buyer_username == models.inwishlist.buyer_username).one() # going to subtract quantity from this item
    currQuantity = currItem.wishlist_quantity
    if currQuantity >= 2:
        db.session.execute('UPDATE inwishlist SET wishlist_quantity = wishlist_quantity - 1 WHERE product_id = :product_id AND seller_username = :seller_username AND buyer_username =  :buyer_username', dict(product_id=product_id, seller_username=seller_username, buyer_username=buyer_username))
        db.session.commit()
        return redirect(url_for('wishlist', username=buyer_username), code=307)
    else: # delete item if only 1
        return redirect(url_for('delete_wishlist', product_id=product_id, seller_username=seller_username, buyer_username=buyer_username))

# increases quantity by 1 for item in wishlist
@app.route('/add_quantity_wishlist/product_id=<product_id>&seller_username=<seller_username>&buyer_username=<buyer_username>')
def add_quantity_wishlist(product_id, seller_username, buyer_username):
    db.session.execute('UPDATE inwishlist SET wishlist_quantity = wishlist_quantity + 1 WHERE product_id = :product_id AND seller_username = :seller_username AND buyer_username =  :buyer_username', dict(product_id=product_id, seller_username=seller_username, buyer_username=buyer_username))
    db.session.commit()
    return redirect(url_for('wishlist', username=buyer_username), code=307)

# deletes item from wishlist
@app.route('/delete_wishlist/product_id=<product_id>&seller_username=<seller_username>&buyer_username=<buyer_username>')
def delete_wishlist(product_id, seller_username, buyer_username):
    db.session.execute('DELETE FROM inwishlist WHERE product_id = :product_id AND seller_username = :seller_username AND buyer_username =  :buyer_username', dict(product_id=product_id, seller_username=seller_username, buyer_username=buyer_username))
    db.session.commit()
    return redirect(url_for('wishlist', username=buyer_username), code=307)

# returns wishlist for user
@app.route('/wishlist/<username>')
def wishlist(username):
    username='joshguo'
    wishlist_items = db.session.query(models.inwishlist)\
        .filter(models.inwishlist.buyer_username == username).all()
    items = []

    for wishlist_item in wishlist_items:
        items.append(db.session.query(models.Items).filter(models.Items.product_id == wishlist_item.product_id).filter(models.Items.seller_username == wishlist_item.seller_username).one())

    item_prices = [item.price for item in items]
    wishlist_quantities = [wishlist_item.wishlist_quantity for wishlist_item in wishlist_items]
    total_price = dot(item_prices, wishlist_quantities)
    total_quantity = 0
    for quantity in wishlist_quantities:
        total_quantity += quantity
    return render_template('wishlist.html', wishlist_items=wishlist_items, items=items, username=username, total_price=total_price, total_quantity=total_quantity)

# adds item to cart
@app.route('/add_cart/product_id=<product_id>&seller_username=<seller_username>&buyer_username=<buyer_username>')
def add_cart(product_id, seller_username, buyer_username):
    currItem = db.session.query(models.incart).filter(models.incart.product_id == product_id).filter(models.incart.seller_username == models.incart.seller_username).filter(models.incart.buyer_username == models.incart.buyer_username).all() # going to subtract quantity from this item
    if currItem:
        return redirect(url_for('add_quantity_cart', product_id=product_id, seller_username=seller_username, buyer_username=buyer_username)) # increase quantity by 1 if already in wish list
    else: # not in cart already
        db.session.execute('INSERT INTO incart VALUES(:product_id, :seller_username, :buyer_username, 1)', dict(product_id=product_id, seller_username=seller_username, buyer_username=buyer_username))
        db.session.commit()
        return redirect(url_for('cart', username=buyer_username), code=307)

# decreases quantity by 1 for item in cart
@app.route('/subtract_quantity_cart/product_id=<product_id>&seller_username=<seller_username>&buyer_username=<buyer_username>')
def subtract_quantity_cart(product_id, seller_username, buyer_username):
    currItem = db.session.query(models.incart).filter(models.incart.product_id == product_id).filter(models.incart.seller_username == models.incart.seller_username).filter(models.incart.buyer_username == models.incart.buyer_username).one() # going to subtract quantity from this item
    currQuantity = currItem.cart_quantity
    if currQuantity >= 2:
        db.session.execute('UPDATE incart SET cart_quantity = cart_quantity - 1 WHERE product_id = :product_id AND seller_username = :seller_username AND buyer_username =  :buyer_username', dict(product_id=product_id, seller_username=seller_username, buyer_username=buyer_username))
        db.session.commit()
        return redirect(url_for('cart', username=buyer_username), code=307)
    else: # delete item if only 1
        return redirect(url_for('delete_cart', product_id=product_id, seller_username=seller_username, buyer_username=buyer_username))

# increases quantity by 1 for item in cart
@app.route('/add_quantity_cart/product_id=<product_id>&seller_username=<seller_username>&buyer_username=<buyer_username>')
def add_quantity_cart(product_id, seller_username, buyer_username):
    db.session.execute('UPDATE incart SET cart_quantity = cart_quantity + 1 WHERE product_id = :product_id AND seller_username = :seller_username AND buyer_username =  :buyer_username', dict(product_id=product_id, seller_username=seller_username, buyer_username=buyer_username))
    db.session.commit()
    return redirect(url_for('cart', username=buyer_username), code=307)

# deletes item from cart
@app.route('/delete_cart/product_id=<product_id>&seller_username=<seller_username>&buyer_username=<buyer_username>')
def delete_cart(product_id, seller_username, buyer_username):
    db.session.execute('DELETE FROM incart WHERE product_id = :product_id AND seller_username = :seller_username AND buyer_username =  :buyer_username', dict(product_id=product_id, seller_username=seller_username, buyer_username=buyer_username))
    db.session.commit()
    return redirect(url_for('cart', username=buyer_username), code=307)

# returns cart for user
@app.route('/cart/<username>')
def cart(username):
    username='joshguo'
    cart_items = db.session.query(models.incart)\
        .filter(models.incart.buyer_username == username).all()
    items = []

    for cart_item in cart_items:
        items.append(db.session.query(models.Items).filter(models.Items.product_id == cart_item.product_id).filter(models.Items.seller_username == cart_item.seller_username).one())

    item_prices = [item.price for item in items]
    cart_quantities = [cart_item.cart_quantity for cart_item in cart_items]
    total_price = dot(item_prices, cart_quantities)
    total_quantity = 0
    for quantity in cart_quantities:
        total_quantity += quantity
    return render_template('cart.html', cart_items=cart_items, items=items, username=username, total_price=total_price, total_quantity=total_quantity)

# deletes item from cart
@app.route('/transaction_success')
def transaction_success(buyer_username):
    items = db.session.query(models.Items)
    cart_items = db.session.query(models.incart)\
        .filter(models.incart.buyer_username == buyer_username).all()
    for cart_item in cart_items:
        db.session.execute('INSERT INTO Orders VALUES(:order_id, :buyer_username, :tracking_num, :date_returned, :date_ordered)', dict(order_id=default, buyer_username=buyer_username, tracking_num=default, date_returned=null, date_ordered=GETDATE()))
        db.session.execute('INSERT INTO inorder VALUES(:product_id, :seller_username, :order_id, :order_quantity)', dict(product_id=cart_item.product_id, seller_username=cart_item.seller_username, order_id=Orders.order_id, order_quantity=cart_item.order_quantity))
        db.session.commit()
    db.session.execute('DELETE FROM incart')
    db.session.commit()
    return render_template('all-items.html', items=items)


@app.route('/<username>/order-history', methods=['GET', 'POST'])
def order_history(username):
    buyer = db.session.query(models.Buyers)\
        .filter(models.Buyers.username == username).one()
    items = []
    orders = db.session.query(models.inorder).filter(models.inorder.order_id == models.Orders.order_id).filter(models.Orders.buyer_username == username).all()
    Order = db.session.query(models.Orders).filter(models.Orders.buyer_username == username).all()
    for order in orders:
        items.append(db.session.query(models.Items).filter(models.Items.product_id == orders.product_id).one())
    return render_template('order_history.html', items=items)

@app.route('/item/<product_id>/reviews', methods=['GET', 'POST'])
def review(product_id):
    item = db.session.query(models.Items) \
        .filter(models.Items.product_id == product_id).one()

    reviews = db.session.query(models.Reviews) \
        .filter(models.Reviews.product_id == product_id) \
        .group_by(models.Reviews.review_id).all()


    form = forms.ReviewFormFactory.form()
    if form.validate_on_submit():
        try:
            new_review = models.Reviews()
            new_review.item_rating = form.item_rating.data
            new_review.comments = form.comments.data
            new_review.product_id = product_id
            new_review.seller_username = item.seller_username
            # TODO: change once buyer functionality exists
            new_review.buyer_username = 'joshguo'
            print(new_review)

            db.session.add(new_review)
            db.session.commit()

            return redirect(url_for('review', product_id=product_id))
        except BaseException as e:
            form.errors['database'] = str(e)

    avg_rating = 0
    if len(reviews):
        for review in reviews:
            avg_rating += review.item_rating
        avg_rating /= len(reviews)
        avg_rating = round(avg_rating, 2)

    return render_template('reviews.html', item=item, reviews=reviews, avg_rating=avg_rating, form=form)

# buyer profiles, based on drinker profiles
@app.route('/profile')
@login_required
def profile():
    return render_template('buyer.html', buyer=current_user)

@app.route('/edit-buyer/<username>', methods=['GET', 'POST'])
def edit_buyer(username):
    buyer = db.session.query(models.Buyers)\
        .filter(models.Buyers.username == username).one()
    form = forms.BuyerEditFormFactory.form(buyer)
    if form.validate_on_submit():
        try:
            form.errors.pop('database', None)
            models.Buyers.edit(username, form.username.data, form.bio.data, form.name.data,
                                form.address.data)
            return redirect(url_for('profile'))
        except BaseException as e:
            form.errors['database'] = str(e)
            return render_template('edit-buyer.html', buyer=buyer, form=form)
    else:
        return render_template('edit-buyer.html', buyer=buyer, form=form)



# seller profiles, based on drinker profiles
@app.route('/seller/<username>')
def seller(username):
    seller = db.session.query(models.Buyers)\
        .filter(models.Buyers.username == username).filter(models.Buyers.is_seller == '1').one()
    seller_items = db.session.query(models.Items)\
        .filter(models.Items.seller_username == username).all()
    return render_template('seller.html', seller=seller, items=seller_items)


@app.route('/drinker/<name>')
def drinker(name):
    drinker = db.session.query(models.Drinker)\
        .filter(models.Drinker.name == name).one()
    return render_template('drinker.html', drinker=drinker)

@app.route('/edit-drinker/<name>', methods=['GET', 'POST'])
def edit_drinker(name):
    drinker = db.session.query(models.Drinker)\
        .filter(models.Drinker.name == name).one()
    beers = db.session.query(models.Beer).all()
    bars = db.session.query(models.Bar).all()
    form = forms.DrinkerEditFormFactory.form(drinker, beers, bars)
    if form.validate_on_submit():
        try:
            form.errors.pop('database', None)
            models.Drinker.edit(name, form.name.data, form.address.data,
                                form.get_beers_liked(), form.get_bars_frequented())
            return redirect(url_for('drinker', name=form.name.data))
        except BaseException as e:
            form.errors['database'] = str(e)
            return render_template('edit-drinker.html', drinker=drinker, form=form)
    else:
        return render_template('edit-drinker.html', drinker=drinker, form=form)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    buyer = models.Buyers.query.filter_by(username=username).first()

    # take the user-supplied password, hash it, and compare it to hashed password in the database
    if not buyer or not check_password_hash(buyer.password, password):
        flash('Incorrect username/password combination.')
        return redirect(url_for('login')) # user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(buyer, remember=remember)
    return redirect(url_for('profile'))

@app.route('/forgot', methods=['POST'])
def forgot_post():
    username = request.form.get('username')
    maiden = request.form.get('maiden')

    buyer = models.Buyers.query.filter_by(username=username).first()

    # take the user-supplied password, hash it, and compare it to hashed password in the database
    if not buyer or not check_password_hash(buyer.maiden, maiden):
        flash('Incorrect username/security answer combination.')
        return redirect(url_for('forgot')) # user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials

    password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    password_reset_url = url_for(
        'reset_with_token',
        token = password_reset_serializer.dumps(username, salt='password-reset-salt'),
        _external=True)

    return redirect(password_reset_url)

@app.route('/reset/<token>')
def reset_with_token(token):
    password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        username = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('login'))

    return render_template('reset_with_token.html', token=token)


@app.route('/reset/<token>', methods=['POST'])
def reset_post(token):
    password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    password = request.form.get('password')

    try:
        username = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)
        buyer = models.Buyers.query.filter_by(username=username).first()
    except:
        traceback.print_exc()
        flash('Invalid username!', 'error')
        return redirect(url_for('login'))

    hashedPassword = generate_password_hash(password, method='sha256')
    print("BUYER", buyer)
    db.session.execute('UPDATE buyers SET password=:password WHERE username=:username', dict(password=hashedPassword, username=username))
    db.session.commit()
    flash('Your password has been updated!', 'success')
    return redirect(url_for('login'))


@app.route('/forgot')
def forgot():
    return render_template('forgot.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods = ['POST'])
def register_post():
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')
    address = request.form.get('address')
    bio = request.form.get('bio')
    maiden = request.form.get('maiden')

    existing = models.Buyers.query.filter_by(username=username).first()
    if existing:
        flash('There already exists an account with this username. Please register with a different username.')
        return redirect(url_for('register')) # username already in use

    new_buyer = models.Buyers(username=username, is_seller='0', bio=bio, name=name, password=generate_password_hash(password, method='sha256'), address=address, maiden=generate_password_hash(maiden, method='sha256'))
    db.session.add(new_buyer)
    db.session.commit()
    return redirect(url_for('login'))


@app.route('/tracking/<tracking_num>')
def tracking(tracking_num):
    order = db.session.query(models.Orders).filter(models.Orders.tracking_num == tracking_num).one()



    status = "Processing"
    delta = datetime.date.today() - order.date_ordered
    if delta.days > 2:
        status = "Delivered"
    elif delta.days > 0:
        status = "Shipped"

    if order.date_returned:
        status = "Returned"

    return render_template('tracking.html', status=status, order=order)


@app.template_filter('pluralize')
def pluralize(number, singular='', plural='s'):
    return singular if number == 1 else plural

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
