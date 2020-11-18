from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, func

import os
import models
import forms
import sys
from numpy import dot
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer
import traceback
import datetime
import random
import string
import urllib.request
import requests
import base64
import json


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



categories = ['Appliances', 'Beauty', 'Cell Phones and Accessories', 'Electronics', 'Fashion', 'Gift Cards', 'Industrial and Scientific', 'Luxury Beauty', 'Office Products', 'Pantry', 'Software', 'Tools and Home Improvement', 'Video Games']

@app.route('/')
@login_required
def home():
    items = {}
    recs = []
    for category in categories:
        items[category] = db.session.query(models.Items).filter(models.Items.category == category).filter(models.Items.quantity > 0).limit(10).all()
    cart = db.session.query(models.incart)\
        .filter(models.incart.buyer_username == current_user.username).all()
    if (cart is None):
        flash('Cart is empty!')

    # Find latest order/purchase to generate recommendations off of
    latest_order = db.session.query(models.Orders) \
        .filter(models.Orders.buyer_username == current_user.username).order_by(desc(models.Orders.date_ordered)).first()

    # Get any item_id from that order
    latest_item_id = db.session.query(models.inorder) \
        .filter(models.inorder.order_id == latest_order.order_id).first() if latest_order is not None else None

    # Get actual item from item_id
    latest_item = db.session.query(models.Items) \
        .filter(models.Items.product_id == latest_item_id.product_id).first() if latest_item_id is not None else None

    # Get the first word in the item name
    first_word = latest_item.item_name.split(' ', 1)[0] if latest_item is not None else None

    # Get recommended products based on that first word
    recs = db.session.query(models.Items) \
        .filter(models.Items.item_name.like('%{}%'.format(first_word))).filter(models.Items.quantity > 0).limit(5).all() if first_word is not None else []

    return render_template('all-items.html', items=items, form=forms.SearchFormFactory.form(), recs=recs)


#def all_drinkers():
#    drinkers = db.session.query(models.Drinker).all()
#    return render_template('all-drinkers.html', drinkers=drinkers)

@app.route('/item/<product_id>')
@login_required
def item(product_id):
    items = db.session.query(models.Items)\
        .filter(models.Items.product_id == product_id).filter(models.Items.quantity > 0).all()
    return render_template('item.html', items=items)


# adds item to wishlist
@app.route('/add_wishlist/product_id=<product_id>&seller_username=<seller_username>')
def add_wishlist(product_id, seller_username):
    currItem = db.session.query(models.inwishlist).filter(models.inwishlist.product_id == product_id).filter(models.inwishlist.seller_username == seller_username).filter(models.inwishlist.buyer_username == current_user.username).all() # going to subtract quantity from this item
    if currItem:
        return redirect(url_for('add_quantity_wishlist', product_id=product_id, seller_username=seller_username)) # increase quantity by 1 if already in wish list
    # not in wishlist already
    db.session.execute('INSERT INTO inwishlist VALUES(:product_id, :seller_username, :buyer_username, 1)', dict(product_id=product_id, seller_username=seller_username, buyer_username=current_user.username))
    db.session.commit()
    return redirect(url_for('wishlist'), code=307)

# decreases quantity by 1 for item in wishlist
@app.route('/subtract_quantity_wishlist/product_id=<product_id>&seller_username=<seller_username>')
def subtract_quantity_wishlist(product_id, seller_username):
    currItem = db.session.query(models.inwishlist).filter(models.inwishlist.product_id == product_id).filter(models.inwishlist.seller_username == seller_username).filter(models.inwishlist.buyer_username == current_user.username).one() # going to subtract quantity from this item
    currQuantity = currItem.wishlist_quantity
    if currQuantity >= 2:
        db.session.execute('UPDATE inwishlist SET wishlist_quantity = wishlist_quantity - 1 WHERE product_id = :product_id AND seller_username = :seller_username AND buyer_username =  :buyer_username', dict(product_id=product_id, seller_username=seller_username, buyer_username=current_user.username))
        db.session.commit()
        return redirect(url_for('wishlist'), code=307)
    else: # delete item if only 1
        return redirect(url_for('delete_wishlist', product_id=product_id, seller_username=seller_username))

# increases quantity by 1 for item in wishlist
@app.route('/add_quantity_wishlist/product_id=<product_id>&seller_username=<seller_username>')
def add_quantity_wishlist(product_id, seller_username):
    db.session.execute('UPDATE inwishlist SET wishlist_quantity = wishlist_quantity + 1 WHERE product_id = :product_id AND seller_username = :seller_username AND buyer_username =  :buyer_username', dict(product_id=product_id, seller_username=seller_username, buyer_username=current_user.username))
    db.session.commit()
    return redirect(url_for('wishlist'), code=307)

# deletes item from wishlist
@app.route('/delete_wishlist/product_id=<product_id>&seller_username=<seller_username>')
def delete_wishlist(product_id, seller_username):
    db.session.execute('DELETE FROM inwishlist WHERE product_id = :product_id AND seller_username = :seller_username AND buyer_username =  :buyer_username', dict(product_id=product_id, seller_username=seller_username, buyer_username=current_user.username))
    db.session.commit()
    return redirect(url_for('wishlist'), code=307)

# returns wishlist for user
@app.route('/wishlist')
@login_required
def wishlist():
    wishlist_items = db.session.query(models.inwishlist)\
        .filter(models.inwishlist.buyer_username == current_user.username).all()
    items = []

    for wishlist_item in wishlist_items:
        items.append(db.session.query(models.Items).filter(models.Items.product_id == wishlist_item.product_id).filter(models.Items.seller_username == wishlist_item.seller_username).one())

    item_prices = [item.price for item in items]
    wishlist_quantities = [wishlist_item.wishlist_quantity for wishlist_item in wishlist_items]
    total_price = dot(item_prices, wishlist_quantities)
    total_quantity = 0
    for quantity in wishlist_quantities:
        total_quantity += quantity
    return render_template('wishlist.html', wishlist_items=wishlist_items, items=items, current_user=current_user, username=current_user.username, total_price=total_price, total_quantity=total_quantity)


@app.route('/wishlist_to_cart/product_id=<product_id>&seller_username=<seller_username>')
def wishlist_to_cart(product_id, seller_username):
    db.session.execute('DELETE FROM inwishlist WHERE product_id = :product_id AND seller_username = :seller_username AND buyer_username =  :buyer_username', dict(product_id=product_id, seller_username=seller_username, buyer_username=current_user.username))
    db.session.execute('INSERT INTO incart VALUES(:product_id, :seller_username, :buyer_username, 1)', dict(product_id=product_id, seller_username=seller_username, buyer_username=current_user.username))
    db.session.commit()
    return redirect(url_for('wishlist'), code=307)

# adds item to cart
@app.route('/add_cart/product_id=<product_id>&seller_username=<seller_username>')
def add_cart(product_id, seller_username):
    currItem = db.session.query(models.incart).filter(models.incart.product_id == product_id).filter(models.incart.seller_username == seller_username).filter(models.incart.buyer_username == current_user.username).all() #  item
    if currItem: # in cart already
        return redirect(url_for('add_quantity_cart', product_id=product_id, seller_username=seller_username)) # increase quantity by 1 if already in wish list
    else: # not in cart already
        db.session.execute('INSERT INTO incart VALUES(:product_id, :seller_username, :buyer_username, 1)', dict(product_id=product_id, seller_username=seller_username, buyer_username=current_user.username))
        db.session.commit()
        return redirect(url_for('cart'), code=307)

# decreases quantity by 1 for item in cart
@app.route('/subtract_quantity_cart/product_id=<product_id>&seller_username=<seller_username>')
def subtract_quantity_cart(product_id, seller_username):
    currItem = db.session.query(models.incart).filter(models.incart.product_id == product_id).filter(models.incart.seller_username == models.incart.seller_username).filter(models.incart.buyer_username == models.incart.buyer_username).one() # going to subtract quantity from this item
    currQuantity = currItem.cart_quantity
    if currQuantity >= 2:
        db.session.execute('UPDATE incart SET cart_quantity = cart_quantity - 1 WHERE product_id = :product_id AND seller_username = :seller_username AND buyer_username =  :buyer_username', dict(product_id=product_id, seller_username=seller_username, buyer_username=current_user.username))
        db.session.commit()
        return redirect(url_for('cart', username=current_user.username), code=307)
    else: # delete item if only 1
        return redirect(url_for('delete_cart', product_id=product_id, seller_username=seller_username, buyer_username=current_user.username))

# increases quantity by 1 for item in cart
@app.route('/add_quantity_cart/product_id=<product_id>&seller_username=<seller_username>')
def add_quantity_cart(product_id, seller_username):
    db.session.execute('UPDATE incart SET cart_quantity = cart_quantity + 1 WHERE product_id = :product_id AND seller_username = :seller_username AND buyer_username =  :buyer_username', dict(product_id=product_id, seller_username=seller_username, buyer_username=current_user.username))
    db.session.commit()
    return redirect(url_for('cart'), code=307)

# deletes item from cart
@app.route('/delete_cart/product_id=<product_id>&seller_username=<seller_username>')
def delete_cart(product_id, seller_username):
    db.session.execute('DELETE FROM incart WHERE product_id = :product_id AND seller_username = :seller_username AND buyer_username =  :buyer_username', dict(product_id=product_id, seller_username=seller_username, buyer_username=current_user.username))
    db.session.commit()
    return redirect(url_for('cart'), code=307)

# returns cart for user
@app.route('/cart')
def cart():
    cart_items = db.session.query(models.incart)\
        .filter(models.incart.buyer_username == current_user.username).all()
    items = []

    for cart_item in cart_items:
        items.append(db.session.query(models.Items).filter(models.Items.product_id == cart_item.product_id).filter(models.Items.seller_username == cart_item.seller_username).one())

    item_prices = [item.price for item in items]
    cart_quantities = [cart_item.cart_quantity for cart_item in cart_items]
    total_price = dot(item_prices, cart_quantities)
    total_quantity = 0
    for quantity in cart_quantities:
        total_quantity += quantity
    return render_template('cart.html', cart_items=cart_items, items=items, username=current_user.username, total_price=total_price, total_quantity=total_quantity)

@app.route('/checkout')
def checkout():
    cart_items = db.session.query(models.incart)\
        .filter(models.incart.buyer_username == current_user.username).all()
    items = []

    for cart_item in cart_items:
        items.append(db.session.query(models.Items).filter(models.Items.product_id == cart_item.product_id).filter(models.Items.seller_username == cart_item.seller_username).one())

    item_prices = [item.price for item in items]
    cart_quantities = [cart_item.cart_quantity for cart_item in cart_items]
    total_price = dot(item_prices, cart_quantities)
    total_quantity = 0
    for quantity in cart_quantities:
        total_quantity += quantity
    return render_template('checkout.html', cart_items=cart_items, items=items, username=current_user.username, total_price=total_price, total_quantity=total_quantity, address=current_user.address)

# deletes item from cart
@app.route('/transaction_success')
def transaction_success():
    items = db.session.query(models.Items)
    cart_items = db.session.query(models.incart)\
        .filter(models.incart.buyer_username == current_user.username).all()
    date = str(datetime.date.today())
    db.session.execute('INSERT INTO Orders VALUES(DEFAULT, :buyer_username, DEFAULT, :date_bought)', dict(buyer_username=current_user.username, date_bought=date))
    for cart_item in cart_items:
        orderID = db.session.query(func.max(models.Orders.order_id)).scalar()
        # decrement number of items below
        try:
            db.session.execute('UPDATE items SET quantity=quantity-:order_quantity WHERE product_id=:product_id AND seller_username=:seller_username', dict(order_quantity=cart_item.cart_quantity, product_id=cart_item.product_id, seller_username=cart_item.seller_username))
        except:
            flash('Insufficient number of copies for this item. Please decrease order quantity or buy from other sellers.', 'error')
            return redirect(url_for('cart'))
        db.session.execute('INSERT INTO inorder VALUES(:product_id, :seller_username, :order_id, :order_quantity)', dict(product_id=cart_item.product_id, seller_username=cart_item.seller_username, order_id=orderID, order_quantity=cart_item.cart_quantity))
    db.session.execute(('DELETE FROM incart WHERE buyer_username = :buyer_username'), dict(buyer_username=current_user.username))
    db.session.commit()
    return redirect(url_for('home'), code=307)


@app.route('/order-history', methods=['GET', 'POST'])
@login_required
def order_history():
    items = []
    orders = db.session.query(models.Orders).filter(models.Orders.buyer_username == current_user.username).all()
    for order in orders:
        currItems = []
        itemList = db.session.query(models.inorder).filter(models.inorder.order_id == order.order_id).all()
        for item in itemList:
            itemInfo = db.session.query(models.Items).filter(models.Items.product_id == item.product_id).filter(models.Items.seller_username==item.seller_username).one()
            currItems.append(itemInfo)
        items.append(currItems)

    return render_template('order_history.html', items=items, orders=orders)

@app.route('/sales-history', methods=['GET', 'POST'])
@login_required
def sales_history():
    if not current_user.is_seller:
        return render_template('not_seller_sales_history.html')
    itemsSelling = db.session.query(models.Items).filter(models.Items.seller_username == current_user.username).all()
    itemsSold = db.session.query(models.inorder, models.Items, models.Orders).filter(models.inorder.seller_username == current_user.username)\
        .filter(models.inorder.order_id == models.Orders.order_id).filter(models.inorder.product_id == models.Items.product_id).all()
    return render_template('sales_history.html', itemsSelling=itemsSelling, itemsSold=itemsSold)

@app.route('/edit-item/<product_id>', methods=['GET', 'POST'])
@login_required
def edit_item(product_id):
    item = db.session.query(models.Items).filter(models.Items.product_id == product_id).one()
    form = forms.ItemEditFormFactory.form(item)
    if form.validate_on_submit():
        form.errors.pop('database', None)

        if (request.files['image']):
            image = request.files['image']
            apiUrl = 'https://api.imgur.com/3/image'
            b64_image = base64.standard_b64encode(image.read())
            params = {'image' : b64_image}
            headers = {'Authorization' : 'Client-ID 12aa250c79dba8d'}
            #client_id = '12aa250c79dba8d'
            #client_secret = '0e132c4d82850eda1d2a172903f5a85bcea10a0b'
            response = requests.post(apiUrl, headers=headers, data=params)
            result = json.loads(response.text)
            edit_posting = models.Items()
            edit_posting.image = result['data']['link']
            models.Items.edit(product_id, current_user.username, form.category.data, form.condition.data, form.item_name.data, form.price.data, form.quantity.data, edit_posting.image, form.description.data)
        else:
            models.Items.edit(product_id, current_user.username, form.category.data, form.condition.data, form.item_name.data, form.price.data, form.quantity.data, item.image, form.description.data)

        flash('Item been modified successfully')
        return redirect(url_for('sales_history'))
    return render_template('edit-item.html', item=item, form=form)


@app.route('/post-item', methods=['GET', 'POST'])
@login_required
def post_item():
    form = forms.PostingFormFactory.form()
    if form.validate_on_submit():
        randomString = ''.join(random.choices(string.ascii_uppercase +
                         string.digits, k = 30))
        new_posting = models.Items()
        new_posting.product_id = randomString
        new_posting.seller_username = current_user.username
        new_posting.category = form.category.data
        new_posting.condition = form.condition.data
        new_posting.item_name = form.item_name.data
        new_posting.price = form.price.data
        new_posting.quantity = form.quantity.data
        new_posting.description = form.description.data

        image = request.files['image']
        apiUrl = 'https://api.imgur.com/3/image'
        b64_image = base64.standard_b64encode(image.read())
        params = {'image' : b64_image}
        headers = {'Authorization' : 'Client-ID 12aa250c79dba8d'}
        #client_id = '12aa250c79dba8d'
        #client_secret = '0e132c4d82850eda1d2a172903f5a85bcea10a0b'
        response = requests.post(apiUrl, headers=headers, data=params)
        result = json.loads(response.text)
        new_posting.image = result['data']['link']

        db.session.add(new_posting)
        db.session.execute('UPDATE buyers SET is_seller=\'1\' WHERE username=:username', dict(username=current_user.username))

        db.session.commit()

        current_user.is_seller = '1'

        flash('Item posted successfully')
        return redirect(url_for('post_item'))

    return render_template('post_item.html', form=form)

@app.route('/item/<product_id>/reviews', methods=['GET', 'POST'])
def review(product_id):
    item = db.session.query(models.Items) \
        .filter(models.Items.product_id == product_id).first()

    reviews = db.session.query(models.Reviews) \
        .filter(models.Reviews.product_id == product_id) \
        .group_by(models.Reviews.review_id).all()

    form = forms.ReviewFormFactory.form()
    if form.validate_on_submit():
        num_reviews = len([r for r in reviews if r.buyer_username == current_user.username])
        num_purchases = len(db.session.query(models.Orders, models.inorder)
                            .filter(models.Orders.buyer_username == current_user.username)
                            .filter(models.Orders.order_id == models.inorder.order_id)
                            .filter(models.inorder.product_id == product_id).all())

        if num_reviews >= num_purchases:
            flash('You can only review an item once for each purchase')
            return redirect(url_for('review', product_id=product_id))

        try:
            new_review = models.Reviews()
            new_review.item_rating = form.item_rating.data
            new_review.comments = form.comments.data
            new_review.product_id = product_id
            new_review.seller_username = item.seller_username
            new_review.buyer_username = current_user.username
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

@app.route('/edit-buyer', methods=['GET', 'POST'])
@login_required
def edit_buyer():
    form = forms.BuyerEditFormFactory.form(current_user)
    if form.validate_on_submit():
        try:
            form.errors.pop('database', None)
            models.Buyers.edit(current_user.username, form.username.data, form.bio.data, form.name.data,
                                form.address.data)
            return redirect(url_for('profile'))
        except BaseException as e:
            form.errors['database'] = str(e)
            return render_template('edit-buyer.html', buyer=current_user, form=form)
    else:
        return render_template('edit-buyer.html', buyer=current_user, form=form)

# seller profiles, based on drinker profiles
@app.route('/seller/<username>')
def seller(username):
    rating = db.session.execute('SELECT AVG(item_rating) FROM reviews WHERE seller_username=:seller_username', dict(seller_username=username)).first()[0]

    seller = db.session.query(models.Buyers)\
        .filter(models.Buyers.username == username).filter(models.Buyers.is_seller == '1').one()
    seller_items = db.session.query(models.Items)\
        .filter(models.Items.seller_username == username).filter(models.Items.quantity > 0).all()
    return render_template('seller.html', seller=seller, items=seller_items, rating=rating)


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
    if delta.days > 2: # delivers after 3 days
        status = "Delivered"
    elif delta.days > 0:
        status = "Shipped"



    return render_template('tracking.html', status=status, order=order)

@app.route('/return_item/product_id=<product_id>&seller_username=<seller_username>&order_id=<order_id>')
def return_item(product_id, seller_username, order_id):
    item_inorder = db.session.query(models.inorder).filter(models.inorder.product_id == product_id).filter(models.inorder.seller_username == seller_username).filter(models.inorder.order_id == order_id).one()
    # check if already returned
    if item_inorder.date_returned:
        # notify
        flash('This item has already been returned', 'error')
        return redirect(url_for('order-history'), code=307)

    # change date_returned in inorder
    date_returned = datetime.date.today().strftime('%Y-%m-%d')
    db.session.execute('UPDATE inorder SET date_returned=:date_returned WHERE product_id=:product_id AND seller_username=:seller_username AND order_id=:order_id', dict(date_returned=date_returned, product_id=product_id, seller_username=seller_username, order_id=order_id))

    # increase quantity of item with product_id and seller_username by order_quantity
    additional_quantity = item_inorder.order_quantity
    db.session.execute('UPDATE Items SET quantity=quantity+:additional_quantity WHERE product_id=:product_id AND seller_username=:seller_username', dict(additional_quantity=additional_quantity, product_id=product_id, seller_username=seller_username))

    db.session.commit()


    return redirect(url_for('order-history'), code=307)


@app.route('/search', methods=['GET'])
def search_page(items=None):
    items = [] if items is None else items
    return render_template('search-items.html', items=items, form=forms.SearchFormFactory.form(), categories=categories)


@app.route('/search', methods=['POST'])
def search():
    items = []

    form = forms.SearchFormFactory.form()
    if form.validate_on_submit():
        print('###############')
        print(form.category.data)
        try:
            if form.category.data == 'All' or form.category.data is None:
                items = db.session.query(models.Items) \
                    .filter(models.Items.item_name.like('%{}%'.format(form.query.data))).filter(models.Items.quantity > 0).limit(10).all()
            else:
                items = db.session.query(models.Items) \
                    .filter(models.Items.item_name.like('%{}%'.format(form.query.data))) \
                    .filter(models.Items.category == form.category.data).filter(models.Items.quantity > 0).limit(10).all()

            print(items)

        except BaseException as e:
            form.errors['database'] = str(e)
            return redirect(url_for('home'))

    return render_template('search-items.html', items=items, form=form, categories=categories)




@app.template_filter('pluralize')
def pluralize(number, singular='', plural='s'):
    return singular if number == 1 else plural

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
