from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from wtforms import StringField, BooleanField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename

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

class PostingFormFactory:
    @staticmethod
    def form():
        class F(FlaskForm):
            item_name = StringField(default='')
            category = SelectField(u'Category', choices=[('Appliances', 'Appliances'), ('Beauty', 'Beauty'), ('Cell Phones and Accessories', 'Cell Phones and Accessories'), ('Electronics', 'Electronics'), ('Fashion', 'Fashion'), ('Gift Cards', 'Gift Cards'), ('Industrial and Scientific', 'Industrial and Scientific'), ('Luxury Beauty', 'Luxury Beauty'), ('Office Products', 'Office Products'), ('Pantry', 'Pantry'), ('Software', 'Software'), ('Tools and Home Improvement', 'Tools and Home Improvement'), ('Video Games','Video Games')])
            condition = SelectField(u'Condition', choices=[('New', 'New'), ('Used - Like New', 'Used - Like New'), ('Used - Very Good', 'Used - Very Good'), ('Used - Good', 'Used - Good'), ('Used - Acceptable', 'Used - Acceptable')])
            price = FloatField()
            quantity = IntegerField()
            image = FileField(u'Image File')
            description = StringField(default='')
        return F()

class ItemEditFormFactory:
    @staticmethod
    def form(item):
        class F(FlaskForm):
            item_name = StringField(default=item.item_name)
            category = SelectField(u'Category', choices=[('Appliances', 'Appliances'), ('Beauty', 'Beauty'), ('Cell Phones and Accessories', 'Cell Phones and Accessories'), ('Electronics', 'Electronics'), ('Fashion', 'Fashion'), ('Gift Cards', 'Gift Cards'), ('Industrial and Scientific', 'Industrial and Scientific'), ('Luxury Beauty', 'Luxury Beauty'), ('Office Products', 'Office Products'), ('Pantry', 'Pantry'), ('Software', 'Software'), ('Tools and Home Improvement', 'Tools and Home Improvement'), ('Video Games','Video Games')])
            condition = SelectField(u'Condition', choices=[('New', 'New'), ('Used - Like New', 'Used - Like New'), ('Used - Very Good', 'Used - Very Good'), ('Used - Good', 'Used - Good'), ('Used - Acceptable', 'Used - Acceptable')])
            price = FloatField(default=item.price)
            quantity = IntegerField(default=item.quantity)
            image = FileField(u'Image File')
            description = StringField(default=item.description)
        return F()

class SearchFormFactory:
    @staticmethod
    def form():
        class F(FlaskForm):
            query = StringField(default='')
            category = StringField(default='All')
        return F()
