from flask_wtf import FlaskForm
from wtforms import PasswordField, TextAreaField, SubmitField, StringField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    address = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    description = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')