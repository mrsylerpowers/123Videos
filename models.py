from me_web import app
from flask_sqlalchemy import SQLAlchemy

import datetime

db = SQLAlchemy(app)
tags = db.Table('tags',
                db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')),
                db.Column('actor_id', db.Integer, db.ForeignKey('actor.id')),
                db.Column('director_id', db.Integer, db.ForeignKey('director.id')),
                db.Column('country_id', db.Integer, db.ForeignKey('country.id')),
                db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'))
                )


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(128))

    url = db.Column(db.String(800))

    decription = db.Column(db.String(1000) ,default='')

    upvotes = db.Column(db.Integer, default=0)

    rateing = db.Column(db.Integer, default=0)

    coverimageurl = db.Column(db.String(500) ,default='')

    imdburl = db.Column(db.String(100),default='')

    datecreated = db.Column(db.Date)

    dateadded = db.Column(db.DateTime, default=datetime.datetime.now())

    country = db.relationship('Country', secondary=tags,
                              backref=db.backref('movie', lazy='dynamic'))

    genre = db.relationship('Genre', secondary=tags,
                            backref=db.backref('movie', lazy='dynamic'),uselist=True)
    actors = db.relationship('Actor', secondary=tags,
                             backref=db.backref('movie', lazy='dynamic'))
    directors = db.relationship('Director', secondary=tags,
                                backref=db.backref('movie', lazy='dynamic'))

    def __init__(self, title, url, datecreated):
        self.title = title
        self.url = url
        self.datecreated = datecreated


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))

    def __init__(self, name):
        self.name = name


class Actor(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(70))

    def __init__(self, name):
        self.name = name


class Director(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))

    def __init__(self, name):
        self.name = name


class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30))

    def __init__(self, name):
        self.name = name




class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(128))

    dateadded = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, title):
        self.title = title


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    pub_date = db.Column(db.DateTime, default=datetime.datetime.now())
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    blog = db.relationship('Blog',
                           backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, blog, title, body):
        self.title = title
        self.body = body
        self.blog = blog
