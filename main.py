from flask import Flask, render_template, request, redirect
import pymysql
import pymysql.cursors

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("home.html.jinja")

connection = pymysql.connect(
    host='10.100.33.60',
    user='agrenardo',
    password='220279616',
    database='agrenardo_todo',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True 
)

if __name__=='__main__':
    app.run(debug=True)

@app.route('/feed')
def post_feed():

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM `posts` ORDER BY `timestamp`")

    results = cursor.fetchall()

return render_template(
    "feed.html.jinja",
    posts = results
)