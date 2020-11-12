from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired

class BuyerEditFormFactory:
    @staticmethod
    def form(buyer):
        class F(FlaskForm):
            username = StringField(default=buyer.username)
            name = StringField(default=buyer.name)
            address = StringField(default=buyer.address)
            bio = StringField(default=buyer.bio)
        return F()

class ReviewFormFactory:
    @staticmethod
    def form():
        class F(FlaskForm):
            item_rating = IntegerField(default=5)
            comments = StringField(default='')
        return F()
