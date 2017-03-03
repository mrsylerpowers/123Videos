import flask
import flask_login

from sqlalchemy.orm import sessionmaker

app = flask.Flask(__name__)
app.debug = True


@app.route('/', methods=['GET'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.

    return flask.render_template('home.html', url=flask.request.host)


app.secret_key = '7\r\xec\xc0b\xad\xf4\xca\xdf\xd1\xc3\xc9\x03\xe7\xfdf\xc3\xbb\xc1\xbd\xa6+\xb2\xba'

app.run()
