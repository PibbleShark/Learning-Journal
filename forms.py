from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, ValidationError, Email, Length, EqualTo, Optional
from wtforms.fields.html5 import EmailField, IntegerField, DateField

from models import User


def email_exists(form, field):
    """Custom validator to ensure no duplicate users"""
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('A user with that E-mail already exists.')


class RegisterForm(Form):
    email = EmailField('Email', validators=[
        InputRequired(),
        Email(),
        email_exists
    ])
    password = PasswordField('Password', validators=[
        InputRequired(),
        Length(min=2),
        EqualTo('password2', message='Passwords must match')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        InputRequired()
    ])


class LoginForm(Form):
    email = EmailField('Email', validators=[
        InputRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        InputRequired()
    ])


class EntryForm(Form):
    title = StringField('Title', validators=[
        InputRequired(),
    ])
    time_spent = IntegerField('Time Spent', validators=[
        Optional()
    ])
    date_created = DateField('Date', validators=[
        InputRequired()
    ])
    content = TextAreaField('What have you learned?', validators=[
        InputRequired()
    ])
    resources = TextAreaField('Additional resources to remember', validators=[
        Optional()
    ])
