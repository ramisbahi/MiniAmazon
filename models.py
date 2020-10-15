from sqlalchemy import sql, orm, CheckConstraint
from app import db

class Drinker(db.Model):
    __tablename__ = 'drinker'
    name = db.Column('name', db.String(20), primary_key=True)
    address = db.Column('address', db.String(20))
    likes = orm.relationship('Likes')
    frequents = orm.relationship('Frequents')
    @staticmethod
    def edit(old_name, name, address, beers_liked, bars_frequented):
        try:
            db.session.execute('DELETE FROM likes WHERE drinker = :name',
                               dict(name=old_name))
            db.session.execute('DELETE FROM frequents WHERE drinker = :name',
                               dict(name=old_name))
            db.session.execute('UPDATE drinker SET name = :name, address = :address'
                               ' WHERE name = :old_name',
                               dict(old_name=old_name, name=name, address=address))
            for beer in beers_liked:
                db.session.execute('INSERT INTO likes VALUES(:drinker, :beer)',
                                   dict(drinker=name, beer=beer))
            for bar, times_a_week in bars_frequented:
                db.session.execute('INSERT INTO frequents'
                                   ' VALUES(:drinker, :bar, :times_a_week)',
                                   dict(drinker=name, bar=bar,
                                        times_a_week=times_a_week))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

class Items(db.Model):
    __tablename__ = 'items'
    product_id = db.Column('product_id', db.Integer(), primary_key=True)
    seller_username = db.Column('seller_username', db.String(30), primary_key=True)
    category = db.Column('category', db.String(80))
    condition = db.Column('condition', db.String(30))
    item_name = db.Column('item_name', db.String(80))
    price = db.Column('price', db.Float())
    quantity = db.Column('quantity', db.Integer())
    image = db.Column('image', db.String(500))
    description = db.Column('description', db.String(2000))

class inwishlist(db.Model):
    __tablename__ = 'inwishlist'
    product_id = db.Column('product_id', db.Integer(), primary_key = True)
    seller_username = db.Column('seller_username', db.String(30), primary_key = True)
    buyer_username = db.Column('buyer_username', db.String(30), primary_key = True)
    wishlist_quantity = db.Column('wishlist_quantity', db.Integer())


class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column('id', db.Integer, autoincrement=True, primary_key=True)
    rating = db.Column('rating', db.Integer, CheckConstraint('rating >= 1 AND rating <= 5'))
    comment = db.Column('comment', db.Text)
    item_id = db.Column('item_id', db.Integer, db.ForeignKey('item.product_id'))


class Beer(db.Model):
    __tablename__ = 'beer'
    name = db.Column('name', db.String(20), primary_key=True)
    brewer = db.Column('brewer', db.String(20))

class Bar(db.Model):
    __tablename__ = 'bar'
    name = db.Column('name', db.String(20), primary_key=True)
    address = db.Column('address', db.String(20))
    serves = orm.relationship('Serves')

class Likes(db.Model):
    __tablename__ = 'likes'
    drinker = db.Column('drinker', db.String(20),
                        db.ForeignKey('drinker.name'),
                        primary_key=True)
    beer = db.Column('beer', db.String(20),
                     db.ForeignKey('beer.name'),
                     primary_key=True)

class Serves(db.Model):
    __tablename__ = 'serves'
    bar = db.Column('bar', db.String(20),
                    db.ForeignKey('bar.name'),
                    primary_key=True)
    beer = db.Column('beer', db.String(20),
                     db.ForeignKey('beer.name'),
                     primary_key=True)
    price = db.Column('price', db.Float())

class Frequents(db.Model):
    __tablename__ = 'frequents'
    drinker = db.Column('drinker', db.String(20),
                        db.ForeignKey('drinker.name'),
                        primary_key=True)
    bar = db.Column('bar', db.String(20),
                    db.ForeignKey('bar.name'),
                    primary_key=True)
    times_a_week = db.Column('times_a_week', db.Integer())

db.create_all()