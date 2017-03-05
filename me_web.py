import flask
from wtforms import ValidationError
import datetime

from models import *

import warnings
from flask.exthook import ExtDeprecationWarning

warnings.simplefilter('ignore', ExtDeprecationWarning)

from flask_sqlalchemy import SQLAlchemy
from flask_inputs import Inputs
from wtforms import validators


def validate_url(form, field):
    accepted_ext = {
        '.mp4', '.acc', 'mp3', '.wav', '.webm'
    }
    for ext in accepted_ext:
        if ext not in str(field.data):
            raise ValidationError("Url must be in format: " + str(list(accepted_ext)))


def validate_imdb_url(form, field):
    if 'www.imdb.com/title/' not in str(field.data):
        raise ValidationError("Url must be in format: 'www.imdb.com/title/<id>' ")


class movievalidator(Inputs):
    rule = {
        'url': [validators.DataRequired(), validators.URL(), validate_url],
        'imdburl': [validators.DataRequired(), validators.URL(), validate_imdb_url]
    }


app = flask.Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/me-web.db'
db = SQLAlchemy(app)


@app.route('/onetime', methods=['GET'])
def onetime():

    gernes = {Genre('Comedy'), Genre('Crime'), Genre("Drama")}
    actors = {Actor('Billy Bob Thornton'), Actor("Kathy Bates"), Actor('Tony Cox')}
    direcctors = Director('Mark Waters')
    countrys = Country('United States')
    date = datetime.datetime.now().date()
    mv = Movie('Bad Santa',
               'https://r3---sn-hjoj-gq0e.googlevideo.com/videoplayback?id=72cd19f9c21d9d8b&itag=22&source=webdrive&requiressl=yes&ttl=transient&pl=13&ei=84S6WKPsEdbgqQWk46Mw&mime=video/mp4&lmt=1486580102304772&ip=152.8.31.191&ipbits=0&expire=1488633139&sparams=ei,expire,id,ip,ipbits,itag,lmt,mime,mm,mn,ms,mv,pcm2cms,pl,requiressl,source,ttl&signature=3C9F7D0F5D2B38037DA10A5B0D78F3A2BF34934D.49087E27F886348C3C797EA63799A23CD049D831&key=cms1&app=explorer&cms_redirect=yes&mm=31&mn=sn-hjoj-gq0e&ms=au&mt=1488621266&mv=m&pcm2cms=yes',
               date)


    for gn in gernes:
        mv.genre.append(gn)
    for gn in actors:
        mv.actors.append(gn)
    mv.directors.append(direcctors)
    mv.country.append(countrys)
    mv.datecreated = date
    db.session.add(mv)

    return ''


@app.route('/submit', methods=['GET'])
def submit():
    return flask.render_template('submit.html', url=flask.request.host)


@app.route('/news/submit', methods=['POST'])
def newssubmit():
    body = flask.request.get_json()
    print (body)
    blg = Blog.query.filter_by(title='News')[0]
    db.session.add(
        Post(blg, title=body['title'], body=body['body'])
    )
    db.session.commit()
    return ''


@app.route('/r/<blog>', methods=['GET'])
def Blogs(blog):
    user = Blog.query.filter_by(title=blog).first_or_404()
    return flask.render_template('show_user.html', blogs=user)


@app.route('/news/edit', methods=['GET'])
def newsedit():
    return flask.render_template('newsedit.html', url=flask.request.host)


@app.route('/', methods=['GET'])
def login():
    return flask.render_template('home.html', url=flask.request.host,
                                 movies=Movie.query.order_by(Movie.dateadded.desc()))


if __name__ == "__main__":
    app.run()
