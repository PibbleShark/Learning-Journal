import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase('journal.db')


class User(UserMixin, Model):
    email = CharField(unique=True)
    password = CharField()

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


class BaseModel(Model):
    class Meta:
        database = DATABASE


class Entry(BaseModel):
    user = ForeignKeyField(
        User,
        related_name='entries')
    title = CharField(unique=True)
    time_spent = IntegerField(default=0)
    date_created = DateField(default=datetime.date.today())
    content = TextField()
    resources = TextField()


class Tags(BaseModel):
    tag = CharField()


class EntryTags(Model):
    entry = ForeignKeyField(Entry)
    tag = ForeignKeyField(Tags)

    class Meta:
        database = DATABASE
        indexes = (
            (('entry', 'tag'), True),
        )


    @classmethod
    def tag_current_entries(cls, tag):
        try:
            tag_entries = Entry.select().where(Entry.content.contains(tag.tag))
        except DoesNotExist:
            pass
        else:
            try:
                for entry in tag_entries:
                    cls.create(
                        entry=entry,
                        tag=tag)
            except IntegrityError:
                pass


    @classmethod
    def tag_new_entry(cls, entry):
        try:
            associated_tags = Tags.select().where(Tags.tag.in_(entry.content.split(' ')))
        except DoesNotExist:
            pass
        else:
            try:
                for tag in associated_tags:
                    cls.create(
                        entry=entry,
                        tag=tag)
            except IntegrityError:
                pass

    @classmethod
    def remove_existing_tag(cls, entry):
        try:
            associated_tags = Tags.select().where(Tags.tag.not_in(entry.content.split(' ')))
        except DoesNotExist:
            pass
        else:
            for tag in associated_tags:
                unwanted_association = cls.get(tag=tag, entry=entry)
                unwanted_association.delete_instance()


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Tags, Entry, EntryTags], safe=True)
    DATABASE.close()
