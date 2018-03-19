import os
import logging

import flask

from flask_sqlalchemy import SQLAlchemy

from flask_inputs import Inputs
from wtforms import validators
from wtforms import ValidationError
from werkzeug.utils import secure_filename
from flask_wtf import file
import datetime

import json

import requests

import model

app = flask.Flask(__name__)
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/me-web.db'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = 'static/temp/images'
db = SQLAlchemy(app)

app.secret_key = 'yhuhjuibyu'


# noinspection PyUnusedLocal
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


# noinspection PyUnusedLocal
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
        'videodecryption': [validators.Length(max=1000, message='Video Description must be at max 1000 charters')],

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


def get_or_create_tag(mod):
    """
    :type mod: db.Model

    """
    my_object = db.session.query(mod.__class__).filter(mod.__class__.name == mod.name).first()

    if my_object is None:
        my_object = mod

    return my_object


def submitmovie(form):
    m_actors = form.getlist('actors[]')
    m_directors = form.getlist('director[]')
    m_genres = form.getlist('genre[]')
    m_country = form.getlist('country[]')
    m_title = form.get('title')
    m_url = form.get('videourl')
    m_description = form.get('videodecryption')
    m_imdburl = form.get('imdburl')
    m_date = form.get('date')
    # Actors
    mv = model.Movie(m_title, m_url, datetime.datetime.strptime(m_date, "%Y-%m-%d").date())
    mv.decription = m_description
    mv.imdburl = m_imdburl
    for actor_n in m_actors:
        mv.actors.append(get_or_create_tag(model.Actor(actor_n)))

    for directors_n in m_directors:
        mv.directors.append(get_or_create_tag(model.Director(directors_n)))

    for country_n in m_country:
        mv.country.append(get_or_create_tag(model.Country(country_n)))

    for genres_n in m_genres:
        mv.genre.append(get_or_create_tag(model.Genre(genres_n)))

    db.session.add(mv)
    db.session.commit()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/img/upload', methods=['POST'])
def upload_file():
    if flask.request.method == 'POST':
        # check if the post request has the file part

        filer = flask.request.files.get('videoinput')
        if not filer :
            filer = flask.request.files.get('coverinput')

        if filer and allowed_file(filer.filename):
            filename = secure_filename(filer.filename)
            basedir = os.path.abspath(os.path.dirname(__file__))
            filer.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
            return filename


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    inputs = MovieValidator(flask.request)
    if flask.request.method == 'POST':
        if inputs.validate():

            submitmovie(flask.request.form)
            flask.flash('Submitted', 'Success')
        else:
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
    return flask.render_template("home.html", url=flask.request.host,
                                 movies=model.Movie.query.order_by(model.Movie.dateadded.desc()))



if __name__ == "__main__":
    app.run()
