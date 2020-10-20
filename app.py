from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import models
import forms
import sys
from numpy import dot

app = Flask(__name__)
app.secret_key = 's3cr3t'
app.config.from_object('config')
db = SQLAlchemy(app, session_options={'autocommit': False})

buyer = 'joshguo'

@app.route('/')
def home():
    items = db.session.query(models.Items).all()
    return render_template('all-items.html', items=items)


#def all_drinkers():
#    drinkers = db.session.query(models.Drinker).all()
#    return render_template('all-drinkers.html', drinkers=drinkers)

@app.route('/item/<product_id>')
def item(product_id):
    item = db.session.query(models.Items)\
        .filter(models.Items.product_id == product_id).one()
    buyer = 'joshguo'
    return render_template('item.html', item=item, buyer=buyer)

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
@app.route('/buyer/<username>')
def buyer(username):
    buyer = db.session.query(models.Buyers)\
        .filter(models.Buyers.username == username).one()
    return render_template('buyer.html', buyer=buyer)

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
            return redirect(url_for('buyer', username=form.username.data))
        except BaseException as e:
            form.errors['database'] = str(e)
            return render_template('edit-buyer.html', buyer=buyer, form=form)
    else:
        return render_template('edit-buyer.html', buyer=buyer, form=form)

# seller profiles, based on drinker profiles
@app.route('/seller/<username>')
def seller(username):
    seller = db.session.query(models.Buyers)\
        .filter(models.Buyers.username == username).filter(models.Buyers.is_seller).one()
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

@app.template_filter('pluralize')
def pluralize(number, singular='', plural='s'):
    return singular if number == 1 else plural

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
