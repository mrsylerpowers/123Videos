import flask
import flask_login, wtforms
from flask.ext.sqlalchemy import SQLAlchemy
app = flask.Flask(__name__)
app.debug = True

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


db = SQLAlchemy()

@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    return User.query.get(user_id)

class User(db.Model):
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user

    """
    __tablename__ = 'user'

    email = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

def load_user(user_id):
    return flask_login.current_user.get(user_id)

@app.after_request
def apply_caching(response):
    response.headers['Server'] = 'AWS'
    return response


class LoginForm(wtforms.Form):
    email = wtforms.StringField('Email Address', [
        wtforms.validators.Length(min=6, max=35),
        wtforms.validators.Email()])
    password = wtforms.PasswordField('New Password', [
        wtforms.validators.DataRequired(),
    ])


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate():
        # Login and validate the user.
        # user should be an instance of your `User` class
        flask_login.login_user()

        flask.flash('Logged in successfully.')

        next = flask.request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.

    return flask.render_template('home.html', form=form)


app.secret_key = '7\r\xec\xc0b\xad\xf4\xca\xdf\xd1\xc3\xc9\x03\xe7\xfdf\xc3\xbb\xc1\xbd\xa6+\xb2\xba'
