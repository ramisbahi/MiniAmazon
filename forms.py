from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired

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
