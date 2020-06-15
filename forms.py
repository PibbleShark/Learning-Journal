from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, ValidationError, Email, Length, EqualTo, Optional
from wtforms.fields.html5 import IntegerField, DateTimeField

from models import User


def email_exists(form, field):
    """Custom validator to ensure no duplicate users"""
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('A user with that E-mail already exists.')


class RegisterForm(Form):
    email = StringField('Email', validators=[
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
    email = StringField('Email', validators=[
        InputRequired(message='You must enter and email address'),
        Email()
    ])
    password = PasswordField('Password', validators=[
        InputRequired(message='You must enter your password')
    ])


class EntryForm(Form):
    title = StringField('Title', validators=[
        InputRequired(),
    ])
    time_spent = IntegerField('Time Spent')
    date_created = DateTimeField('Date', validators=[
        InputRequired()
    ])
    content = TextAreaField('What I Learned', validators=[
        InputRequired()
    ])
    resources = TextAreaField('Resources to Remember')
