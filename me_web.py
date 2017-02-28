from flask import Flask, request, make_response, redirect, url_for, render_template

app = Flask(__name__)
app.debug = True

@app.after_request
def apply_caching(response):
    response.headers['Server'] = 'AWS'
    return response

@app.route("/")
def hello():
    resp = make_response(render_template('home.html'))
    return resp

app.secret_key = '7\r\xec\xc0b\xad\xf4\xca\xdf\xd1\xc3\xc9\x03\xe7\xfdf\xc3\xbb\xc1\xbd\xa6+\xb2\xba'
