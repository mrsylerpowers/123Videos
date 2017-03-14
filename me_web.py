import flask

from flask_sqlalchemy import SQLAlchemy
from flask_inputs import Inputs
from wtforms import validators
from wtforms import ValidationError

import json
import requests

import model

app = flask.Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/me-web.db'
app.config['UPLOAD_FOLDER'] = 'ststic/temp/'
db = SQLAlchemy(app)

app.secret_key = 'yhuhjuibyu'


def validate_url(form, field):
    accepted_ext = {
        '.mp4', '.acc', 'mp3', '.wav', '.webm'
    }
    try:
        ct = requests.head(field.data, allow_redirects=True).headers['content-type']
    except:
        raise ValidationError("Not valid url")
    if 'video' not in str(ct):
        raise ValidationError("Url must resolve directly to a video: " + str(list(accepted_ext)))


def validate_imdb_url(form, field):
    if 'www.imdb.com/title/' not in str(field.data):
        raise ValidationError("Url must be in format: 'www.imdb.com/title/<id>' ")


class MovieValidator(Inputs):
    form = {
        'videourl': [validators.DataRequired(),
                     validators.Length(max=800, message='Video Url must be at max 800 charters'), validate_url],
        'imdburl': [validators.DataRequired(),
                    validators.Length(max=100, message='Imdb url must be at max 100 charcters'), validate_imdb_url],
        'title': [validators.DataRequired(),
                  validators.Length(max=128, message='Video Title must be at max 128 charters')],
        'videodecryption': [validators.Length(max=1000, message='Video Description must be at max 1000 charters')]
        # TODO: Author validator
    }


@app.route('/tag/<name>', methods=['POST'])
def tags(name):
    query = flask.request.form.get('query')

    if name in 'genre':
        qval = model.Genre.query.filter(model.Genre.name.contains(query))
    elif name in 'actor':
        qval = model.Actor.query.filter(model.Actor.name.contains(query))
    elif name in 'director':
        qval = model.Director.query.filter(model.Director.name.contains(query))
    elif name in 'country':
        qval = model.Country.query.filter(model.Country.name.contains(query))
    else:
        qval = None
    ret = []
    if qval:
        for ppt in qval:
            ret.append(ppt.name)
        return json.dumps(ret)
    else:
        return '', 404


@app.route('/onetime', methods=['GET'])
def onetime():
    return ''


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    inputs = MovieValidator(flask.request)
    if flask.request.method == 'POST':
        if inputs.validate():

            flask.flash('Submitted', 'Success')

        else:
            print (flask.request.form.getlist('authors[]'))
            flask.flash('<br/>'.join(['%s'] * len(inputs.errors)) % tuple(inputs.errors), 'Error')

    return flask.render_template('submit.html', url=flask.request.host, form=inputs)


@app.route('/news/submit', methods=['POST'])
def newssubmit():
    body = flask.request.get_json()
    print (body)
    blg = db.session.query(model.Blog).filter_by(title='news')[0]

    pst = model.Post(blg, title=body['title'], body=body['body'])

    db.session.add(pst)
    db.session.commit()
    return ''


@app.route('/r/<blog>', methods=['GET'])
def blogs(blog):
    user = model.Blog.query.filter_by(title=blog).first_or_404()
    return flask.render_template('show_user.html', blogs=user)


@app.route('/news/edit', methods=['GET'])
def newsedit():
    return flask.render_template('newsedit.html', url=flask.request.host)


@app.route('/', methods=['GET'])
def homepage():
    flask.flash('Submitted', 'Success')
    return flask.render_template("home.html", url=flask.request.host,
                                 movies=model.Movie.query.order_by(model.Movie.dateadded.desc()))


if __name__ == "__main__":
    app.run()
