import flask



from flask_sqlalchemy import SQLAlchemy
from flask_inputs import Inputs
from wtforms import validators
from wtforms import ValidationError
import wtforms
import json

import requests

app = flask.Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/me-web.db'
app.config['UPLOAD_FOLDER'] = 'ststic/temp/'
db = SQLAlchemy(app)

app.secret_key = 'yhuhjuibyu'


from models import *


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


class movievalidator(Inputs):
    form = {
        'videourl': [validators.DataRequired(),
                     validators.Length(max=800, message='Video Url must be at max 800 charters'), validate_url],
        'imdburl': [validators.DataRequired(),
                    validators.Length(max=100, message='Imdb url must be at max 100 charcters'), validate_imdb_url],
        'title': [validators.DataRequired(),
                  validators.Length(max=128, message='Video Title must be at max 128 charters')],
        'videodecryption': [validators.Length(max=1000, message='Video Description must be at max 1000 charters')]

    }


@app.route('/tags')
def authors():
    query = flask.request.args.get('q')
    ans = Actor.query.filter(Actor.name.contains(query)).first()
    return json.dumps(ans)


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

@app.errorhandler(500)
def page_not_found(e):
    return flask.render_template('500.html'), 500

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    inputs = movievalidator(flask.request)
    if flask.request.method == 'POST':
        if inputs.validate():

            flask.flash('Submitted', 'Success')

        else:
            flask.flash('<br/>'.join(['%s'] * len(inputs.errors)) % tuple(inputs.errors), 'Error')

    return flask.render_template('submit.html', url=flask.request.host, form=inputs)


@app.route('/news/submit', methods=['POST'])
def newssubmit():
    body = flask.request.get_json()
    print (body)
    blg = db.session.query(Blog).filter_by(title='news')[0]

    pst = Post(blg, title=body['title'], body=body['body'])

    db.session.add(pst)
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
def Homepage():
    flask.flash('Submitted', 'Success')
    return flask.render_template('home.html', url=flask.request.host,
                                 movies=Movie.query.order_by(Movie.dateadded.desc()))


if __name__ == "__main__":
    app.run()
