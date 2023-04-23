from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField
from wtforms.validators import DataRequired


class AdvertForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField("Описание")
    price = StringField('Цена', validators=[DataRequired()])
    submit = SubmitField('Сохранить')