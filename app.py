from flask import (Flask, g, render_template, flash, redirect, url_for, abort,)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user, current_user, login_required)


import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
# noinspection SpellCheckingInspection
app.secret_key = 'qpowienf;aklnv;woinpwivao;vkls/dvna;oind8i'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    try:
        return models.User.get(models.User.id == user_id)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    "Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    """Page for user registration."""
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("You are ready to use the learning journal", "success")
        models.User.create_user(
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """Page for user login."""
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("You need to register before accessing this knowledge", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Get ready to learn!", "success")
                return redirect(url_for('index'))
            else:
                flash("No tacos for you!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Page for user logout."""
    logout_user()
    flash("You have been logged out", "success")
    return redirect(url_for('index'))


@app.route('/')
def index():
    """Index page is also a list of entries"""
    entries = models.Entry.select().limit(8)
    return render_template('index.html', entries=entries)


@app.route('/entries')
def entries():
    """Page to view a list of entries.  More entries are viewed"""
    entries = models.Entry.select().limit(24)
    return render_template('index.html', entries=entries)


@app.route('/entries/<tag>')
@login_required
def entries_by_tag(tag):
    """Shows all entries with a selected tag"""
    #adapted from code suggestion by Charles Leifer
    tagged_entries = (models.Entry
                      .select()
                      .join(models.EntryTags)
                      .join(models.Tags)
                      .where(models.Tags.tag == tag)
                      .order_by(models.Entry.date_created.desc()))
    return render_template('index.html', entries=tagged_entries)


@app.route('/entries/<int:id>')
@login_required
def view_entry(id):
    """View a journal entry with detail."""
    current_entry = models.Entry.get_by_id(id)
    return render_template('detail.html', entry=current_entry)


@app.route('/entries/new', methods=('GET', 'POST'))
@login_required
def create_new():
    """Create a new journal entry."""
    form = forms.EntryForm()
    if form.validate_on_submit():
        try:
            models.Entry.create(user=g.user.get_id(),
                                title=form.title.data.strip(),
                                time_spent=form.time_spent.data,
                                date_created=form.date_created.data,
                                content=form.content.data.strip(),
                                resources=form.resources.data.strip()
                                )
            flash("Entry created", "success")
            models.EntryTags.tag_new_entry(models.Entry.get(title=form.title.data.strip()))
            return redirect(url_for('entries'))
        except models.IntegrityError:
            flash("An entry with that title already exists")
            return redirect(url_for('view_entry', id=models.Entry.get(title=form.title.data.strip())))
    return render_template('new.html', form=form)


@app.route('/entries/<int:id>/edit', methods=('GET', 'POST'))
@login_required
def edit_entry(id):
    """Edit a journal entry"""
    entry = models.Entry.get_by_id(id)
    form = forms.EntryForm(
        title=entry.title,
        time_spent=entry.time_spent,
        date_created=entry.date_created,
        content=entry.content,
        resources=entry.resources
    )
    if form.validate_on_submit():
        entry.title = form.title.data.strip()
        entry.time_spent = form.time_spent.data
        entry.date_created = form.date_created.data
        entry.content = form.content.data.strip()
        entry.resources = form.resources.data.strip()
        entry.save()
        flash("Entry has been updated", "success")
        return redirect(url_for('entries'))
    return render_template('edit.html', form=form, entry=entry)


@app.route('/entries/new_tag', methods=('GET', 'POST'))
@login_required
def create_tag():
    """create a tag to organize your journal entries."""
    form = forms.TagForm()
    if form.validate_on_submit():
        try:
            models.Tags.create(tag=form.tag.data.strip())
            flash('Tag Created', 'success')
            models.EntryTags.tag_current_entries(models.Tags.get(tag=form.tag.data.strip()))
            return redirect(url_for('entries'))
        except models.IntegrityError:
            flash('That tag has already been made')
            return redirect(url_for('entries'))
    return render_template('tag.html', form=form)


@app.route('/entries/<int:id>/delete', methods=('GET', 'POST'))
@login_required
def delete_entry(id):
    """Delete a journal entry"""
    entry = models.Entry.get_by_id(id)
    if entry.count() == 0:
        abort(404)
    else:
        entry.delete_instance()
        flash("Entry has been deleted", "success")
        return redirect(url_for('entries'))


#@app.errorhandler(404)
#def not_found():
    #return render_template('404.html'), 404


if __name__ == '__main__':
    models.initialize()
    try:
        with models.DATABASE.transaction():
            models.User.create_user(
                email='email@email.com',
                password='password',
            )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)
