from flask import Flask, render_template, request, redirect, send_from_directory, abort

from flask_login import LoginManager, login_required, login_user, current_user, logout_user

import pymysql
import pymysql.cursors

login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'something_random'

class User:
    def __init__(self, id, username, banned):
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_active = not banned

        self.username = username
        self.id = id
    
    def get_id(self):
        return str(self.id)


connection = pymysql.connect(
    host='10.100.33.60',
    user='agrenardo',
    password='220279616',
    database='agrenardo_socialmedia',
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True 
)

@login_manager.user_loader
def user_loader(user_id):
    cursor = connection.cursor()

    cursor.execute("SELECT * from `Users` WHERE `ID` = " + user_id)

    result = cursor.fetchone()

    if result is None:
        return None
    
    return User(result['ID'], result['username'], result['banned'])


@app.route("/")
def index():
    return render_template("home.html.jinja")

@app.route('/feed')
@login_required
def post_feed():

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM `Posts` ORDER BY `timestamp`")
    results = cursor.fetchall()

    return render_template(
    "posts.html.jinja",
    posts = results
)

@app.route('/post')
@login_required
def create_post():
    cursor = connection.cursor()

    photo = request.files['photo']

    file_name = photo.filename # my_photo.jpg

    file_extension = file_name.split('.')[-1]

    if file_extension in  ['jpg', 'jpeg', 'png', 'gif']:
        photo.save('media/posts/' + file_name)
    else:
        raise Exception('Invalid file type')

    user_id = current_user.id

    cursor.execute("""INSERT INTO `Posts` (`user_id`, `post_text`, `post_image`) VALUES (%s, %s, %s)""", (request.form['post_text'], file_name, user_id))

    return redirect('/feed')

@app.route('/sign-out')
def sign_out():
    logout_user()

    return redirect('/sign-in')


@app.route('/sign-in', methods = ['POST','GET'])
def sign_in():
    if current_user.is_authenticated:
        return redirect('/feed')

    if request.method == 'POST':
        cursor = connection.cursor()

        cursor.execute(f"SELECT * FROM `Users` WHERE `Username` = ' + {request.form['username']}'")

        result = cursor.fetchone()

        if result is None:
            return render_template("sign_in.html.jinja")
        
        if request.form['password'] == result ['password']:
            User = User(result['ID'], result['username'], result['banned'])

            login_user(User)

            return redirect('/feed')

        else:
            return render_template("sign_in.html.jinja")
    
    elif request.method == 'GET':
        return render_template("sign_in.html.jinja")


@app.route('/sign-up', methods=['POST', 'GET'])
def sign_up():
    if current_user.is_authenticated:
        return redirect('/feed')

    if request.method == 'POST':
       cursor = connection.cursor()

       photo = request.files['photo']

       file_name = photo.filename # my_photo.jpg

       file_extension = file_name.split('.')[-1]

       if file_extension in  ['jpg', 'jpeg', 'png', 'gif']:
           photo.save('media/users/' + file_name)
       else:
           raise Exception('Invalid file type')

       cursor.execute("""
           INSERT INTO `Users` (`birthday`, `username`, `email`, `display_name`, `password`, `bio`, `photo`)
           VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (request.form['birthday'], request.form['username'], request.form['email'], request.form['display_name'], request.form['password'], request.form['bio'], file_name))

       return redirect ('/posts')
    elif request.method == 'GET':
        return render_template("sign_up.html.jinja")
    
@app.route('/profile/<username>')
def user_profile(username):
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM `Users` WHERE `Username` = %s", (username))

    result = cursor.fetchone()

    if result is None:
        abort(404)

    cursor.close()

    cursor = connection.cursor()

    cursor.execute("SELECT * from `Posts` WHERE `user_id` = %s", (result['id']))

    post_result = cursor.fetchall()


    return render_template(
        "user_profile.html.jinja", 
        user = result,
        posts = post_result
    )

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error_status.html.jinja'),404

if __name__=='__main__':
    app.run(debug=True)