import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('journal.db')


class User(UserMixin, Model):
    email = CharField(unique=True)
    password = CharField(unique=True)

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, email, password):
        try:
            with DATABASE.transaction():
                cls.create(
                    email=email,
                    password=generate_password_hash(password))
        except IntegrityError:
            raise ValueError('User already exists')


class Tags(Model):
    tag = CharField()

    class Meta:
        database = DATABASE


class Entry(Model):
    title = CharField()
    time_spent = IntegerField()
    date_created = DateField(default=datetime.date.today())
    content = TextField()
    resources = TextField()
    tag = ForeignKeyField(
        model=Tags,
        related_name='entries')
    user = ForeignKeyField(
        model=User,
        related_name='entries')

    class Meta:
        database = DATABASE
        order_by = ('tag',)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Tags, Entry], safe=True)
    DATABASE.close()
