from sqlalchemy import sql, orm, CheckConstraint, ForeignKeyConstraint
from app import db
from sqlalchemy import sql, orm, CheckConstraint
from app import db
from flask_login import UserMixin

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
    def edit(product_id, seller_username, category, condition, item_name, price, quantity, image, description):
            try:
                db.session.execute('UPDATE items SET seller_username = :seller_username, category = :category, condition = :condition, item_name = :item_name, price = :price, quantity = :quantity, image = :image, description = :description'
                                   ' WHERE product_id = :product_id',
                                   dict(seller_username=seller_username, category=category, condition=condition, item_name=item_name, price=price, quantity=quantity, image=image, description=description, product_id=product_id))
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e

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
    date_returned = db.Column('date_returned', db.Date())

class incart(db.Model):
    __tablename__ = 'incart'
    product_id = db.Column('product_id', db.Integer(), primary_key = True)
    seller_username = db.Column('seller_username', db.String(30), primary_key = True)
    buyer_username = db.Column('buyer_username', db.String(30), primary_key = True)
    cart_quantity = db.Column('cart_quantity', db.Integer())

class Orders(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column('order_id', db.Integer(), autoincrement=True, primary_key = True)
    buyer_username = db.Column('buyer_username', db.String(30))
    tracking_num = db.Column('tracking_num', db.Integer(), autoincrement=True)
    date_ordered = db.Column('date_ordered', db.Date())

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


class Buyers(UserMixin, db.Model):
    __tablename__ = 'buyers'
    username = db.Column('username', db.String, primary_key=True)
    is_seller = db.Column('is_seller', db.Integer)
    bio = db.Column('bio', db.Text)
    name = db.Column('name', db.String)
    password = db.Column('password', db.String)
    address = db.Column('address', db.String)
    maiden = db.Column('maiden', db.String)
    def edit(username, bio, name, address):
            try:
                db.session.execute('UPDATE buyers SET bio = :bio, name = :name, address = :address'
                                   ' WHERE username = :username',
                                   dict(username=username, bio=bio, name=name, address=address))
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e
    def get_id(self):
        return (self.username)
