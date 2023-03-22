from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return "<p>Hello, World!</p>"

@app.route("/post")
def post():
    return render_template("<p>Current Post</p>")

@app.route("/hello/<name>")
def hello(name):
    return f"<p>Hello, {name}!</p>"

@app.route("/")
def index():
    return render_template(
        "home.html.jinja", 
    )