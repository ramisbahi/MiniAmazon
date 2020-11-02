from sqlalchemy import sql, orm, CheckConstraint, ForeignKeyConstraint
from app import db
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
    product_id = db.Column('product_id', db.String(30), primary_key=True)
    seller_username = db.Column('seller_username', db.String(30), primary_key=True)
    category = db.Column('category', db.String(100))
    condition = db.Column('condition', db.String(30))
    item_name = db.Column('item_name', db.String(500))
    price = db.Column('price', db.Float())
    quantity = db.Column('quantity', db.Integer())
    image = db.Column('image', db.String(1000))
    description = db.Column('description', db.String(2000))

class inwishlist(db.Model):
    __tablename__ = 'inwishlist'
    product_id = db.Column('product_id', db.Integer(), primary_key = True)
    seller_username = db.Column('seller_username', db.String(30), primary_key = True)
    buyer_username = db.Column('buyer_username', db.String(30), primary_key = True)
    wishlist_quantity = db.Column('wishlist_quantity', db.Integer())

class inorder(db.Model):
    __tablename__ = 'inorder'
    product_id = db.Column('product_id', db.Integer(), primary_key = True)
    seller_username = db.Column('seller_username', db.String(30), primary_key=True)
    order_id = db.Column('order_id', db.Integer(), primary_key = True)
    order_quantity = db.Column('order_quantity', db.Integer())

class incart(db.Model):
    __tablename__ = 'incart'
    product_id = db.Column('product_id', db.Integer(), primary_key = True)
    seller_username = db.Column('seller_username', db.String(30), primary_key = True)
    buyer_username = db.Column('buyer_username', db.String(30), primary_key = True)
    cart_quantity = db.Column('cart_quantity', db.Integer())

class Orders(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column('order_id', db.Integer(), primary_key = True)
    buyer_username = db.Column('buyer_username', db.String(30))
    tracking_num = db.Column('tracking_num', db.Integer())
    date_returned = db.Column('date_returned', db.Date())
    date_ordered = db.Column('date_ordered', db.Date())
    shipping_status = db.Column('shipping_status', db.String(30))

class Reviews(db.Model):
    __tablename__ = 'reviews'
    review_id = db.Column('review_id', db.Integer, autoincrement=True, primary_key=True)
    item_rating = db.Column('item_rating', db.Integer, CheckConstraint('rating >= 1 AND rating <= 5'))
    comments = db.Column('comments', db.Text)
    buyer_username = db.Column('buyer_username', db.Text, db.ForeignKey('buyers.username'))

    product_id = db.Column('product_id', db.Integer)
    seller_username = db.Column('seller_username', db.Integer)
    __table_args__ = (ForeignKeyConstraint((product_id, seller_username),
                                           [Items.product_id, Items.seller_username]), {})


class Buyers(db.Model):
    __tablename__ = 'buyers'
    username = db.Column('username', db.String, primary_key=True)
    is_seller = db.Column('is_seller', db.Integer)
    bio = db.Column('bio', db.Text)
    name = db.Column('name', db.String)
    password = db.Column('password', db.String)
    address = db.Column('address', db.String)
    def edit(old_username, username, bio, name, address):
            try:
                db.session.execute('UPDATE buyer SET username = :username, bio = :bio, name = :name, address = :address'
                                   ' WHERE username = :old_username',
                                   dict(old_username=old_username, username=username, bio=bio, name=name, address=address))
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e

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
