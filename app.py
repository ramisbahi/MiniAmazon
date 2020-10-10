from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import models
import forms

app = Flask(__name__)
app.secret_key = 's3cr3t'
app.config.from_object('config')
db = SQLAlchemy(app, session_options={'autocommit': False})

@app.route('/')
def all_items():
    items = db.session.query(models.Item).all()
    return render_template('all-items.html', items=items)

@app.route('/item/<product_id>')
def item(product_id):
    item = db.session.query(models.Item)\
        .filter(models.Item.product_id == product_id).one()
    return render_template('item.html', item=item)

@app.route('/item/<product_id>/reviews', methods=['GET', 'POST'])
def review(product_id):
    item = db.session.query(models.Item) \
        .filter(models.Item.product_id == product_id).one()

    reviews = db.session.query(models.Review) \
        .filter(models.Review.item_id == product_id) \
        .group_by(models.Review.id).all()

    form = forms.ReviewFormFactory.form()
    if form.validate_on_submit():
        try:
            new_review = models.Review()
            new_review.rating = form.rating.data
            new_review.comment = form.comment.data
            new_review.item_id = product_id
            db.session.add(new_review)
            db.session.commit()

            return redirect(url_for('review', product_id=product_id))
        except BaseException as e:
            form.errors['database'] = str(e)

    avg_rating = 0
    if len(reviews):
        for review in reviews:
            avg_rating += review.rating
        avg_rating /= len(reviews)
        avg_rating = round(avg_rating, 2)

    return render_template('reviews.html', item=item, reviews=reviews, avg_rating=avg_rating, form=form)


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
    return singular if number in (0, 1) else plural

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
