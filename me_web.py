import flask
from flask_sqlalchemy import SQLAlchemy
import datetime

app = flask.Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/me-web.db'
db = SQLAlchemy(app)


@app.route('/onetime', methods=['GET'])
def onetime():

    return ''

@app.route('/', methods=['GET'])
def login():
    return flask.render_template('home.html', url=flask.request.host,
                                 movies=MovieCarousel.query.order_by(MovieCarousel.dateadded.desc()))


class MovieCarousel(db.Model):
    # Columns

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(128))

    imgurl = db.Column(db.String(500))

    dateadded = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, title, imgurl):
        self.title = title
        self.imgurl = imgurl


if __name__ == "__main__":
    app.run()
