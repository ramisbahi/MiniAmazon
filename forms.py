from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from wtforms import StringField, BooleanField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename

class DrinkerEditFormFactory:
    @staticmethod
    def form(drinker, beers, bars):
        class F(FlaskForm):
            name = StringField(default=drinker.name)
            address = StringField(default=drinker.address)
            @staticmethod
            def beer_field_name(index):
                return 'beer_{}'.format(index)
            def beer_fields(self):
                for i, beer in enumerate(beers):
                    yield beer.name, getattr(self, F.beer_field_name(i))
            def get_beers_liked(self):
                for beer, field in self.beer_fields():
                    if field.data:
                        yield beer
            @staticmethod
            def bar_field_name(index):
                return 'bar_{}'.format(index)
            def bar_fields(self):
                for i, bar in enumerate(bars):
                    yield bar.name, getattr(self, F.bar_field_name(i))
            def get_bars_frequented(self):
                for bar, field in self.bar_fields():
                    if field.data != 0:
                        yield bar, field.data
        beers_liked = [like.beer for like in drinker.likes]
        for i, beer in enumerate(beers):
            field_name = F.beer_field_name(i)
            default = 'checked' if beer.name in beers_liked else None
            setattr(F, field_name, BooleanField(default=default))
        bars_frequented = {frequent.bar: frequent.times_a_week\
                           for frequent in drinker.frequents}
        for i, bar in enumerate(bars):
            field_name = F.bar_field_name(i)
            default = bars_frequented[bar.name] if bar.name in bars_frequented else 0
            setattr(F, field_name, IntegerField(default=default))
        return F()

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
            quantity = IntegerField(defaut=item.quantity)
            image = FileField(u'Image File')
            description = StringField(default=item.description)
        return F()

class SearchFormFactory:
    @staticmethod
    def form():
        class F(FlaskForm):
            query = StringField(default='')
        return F()
