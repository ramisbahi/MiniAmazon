from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import models
import forms
import sys

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
    wishlist_items = db.session.query(models.inwishlist)\
        .filter(models.inwishlist.buyer_username == username).all()
    items = []

    for wishlist_item in wishlist_items:
        items.append(db.session.query(models.Items).filter(models.Items.product_id == wishlist_item.product_id).filter(models.Items.seller_username == wishlist_item.seller_username).one())
    return render_template('wishlist.html', len = len(items), wishlist_items=wishlist_items, items=items, username=username)



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
