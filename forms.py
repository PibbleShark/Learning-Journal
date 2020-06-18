from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, HiddenField
from wtforms.validators import InputRequired, ValidationError, Email, Length, EqualTo
from wtforms.fields.html5 import IntegerField, DateField

from models import User, Entry, Tags


def email_exists(form, field):
    """Custom validator to ensure no duplicate users"""
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('A user with that E-mail already exists.')


def title_exists(form, field):
    """Make sure entered title does not already exist"""
    if Entry.select().where(Entry.title ** field.data).exists():
        raise ValidationError('That title is already in use.')


def tag_exists(form, field):
    """Make sure a duplicate tag is not created"""
    if Tags.select().where(Entry.tag ** field.data).exists():
        raise ValidationError('That tag already exists.')


class RegisterForm(FlaskForm):
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


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        InputRequired(message='You must enter and email address'),
        Email()
    ])
    password = PasswordField('Password', validators=[
        InputRequired(message='You must enter your password')
    ])


class EntryForm(FlaskForm):
    title = StringField('Title', validators=[
        InputRequired(message='You must give your entry a title'),
        title_exists
    ])
    time_spent = IntegerField('Number of Hours Spent')
    date_created = DateField('Date')
    content = TextAreaField('What I Learned', validators=[
        InputRequired(message='You must have learned something')
    ])
    resources = TextAreaField('Resources to Remember')


class TagForm(FlaskForm):
    tag = StringField('Name of Your New Tag', validators=[
        InputRequired(message='You must give your tag a title'),
        tag_exists
    ])
