from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:beproductive@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'blaze1287'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'allpost', 'blog', 'entry', 'my_blogs'] 
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/index')
def index():
    users = User.query.all()
    return render_template('/index.html', users = users, title='All Users')

@app.route('/allpost')
def allpost():
    posts = Blog.query.all()
    users = User.query.all()
    return render_template('allpost.html', users = users, posts=posts, title='All Posts')

@app.route('/blog')
def blog():
    blog_id = request.args.get('id')
    user_id = request.args.get('users')

    if user_id:
        user = User.query.get(user_id)
        return render_template('singleuser.html', blogs=user.blogs, title='Blogz')
    else:
        post = Blog.query.get(blog_id)
        return render_template('entry.html', post=post, title='Blog Entry')

@app.route('/login', methods=['POST', 'GET'])
def login():
    username = ""
    username_error = ""
    password_error = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()

        if not user:
            username_error = "User does not exist."
            if username == "":
                username_error = "Please enter your username."

        if password == "":
            password_error = "Please enter your password."

        if user and user.password != password:
            password_error = "That is the wrong password."

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')

    return render_template('login.html', username = username, username_error = username_error, password_error = password_error)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username = ""
    username_error = ""
    password_error = ""
    verify_error = ""

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username = username).first()

        if len(username) < 3:
            username_error = "Usernames must be longer than 3 characters."
            if username == "":
                username_error = "Please enter a desired username."

        if password != verify:
            password_error = "Passwords must match."
            verify_error = "Passwords must match."
            
        if len(password) < 3:
            password_error = "Password must be longer than 3 characters."
            if password == "":
                password_error = "Please enter a valid password."

        if password != verify:
            password_error = "Passwords must match."
            verify_error = "Passwords must match."

        if not username_error and not password_error and not verify_error:
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                username_error = "Username is already claimed."

    return render_template('signup.html', username = username, username_error = username_error, password_error = password_error, verify_error = verify_error)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.route('/newpost', methods=['POST', 'GET'])

def new_post():
    if request.method == 'POST':
        blog_title = request.form['blog-title']
        blog_body = request.form['blog-entry']
        title_error = ''
        body_error = ''
        owner = User.query.filter_by(username = session['username']).first()

        if not blog_title:
            title_error = "Please enter a blog title"
        if not blog_body:
            body_error = "Please enter a blog entry"

        if not body_error and not title_error:
            new_entry = Blog(blog_title, blog_body, owner)     
            db.session.add(new_entry)
            db.session.commit()        
            return redirect('/blog?id={}'.format(new_entry.id)) 
        else:
            return render_template('newpost.html', title='New Entry', title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)
    
    return render_template('newpost.html', title='New Entry')

@app.route('/singleuser', methods=['POST', 'GET'])
def my_blogs():
    if request.method == 'GET':
        #asking for a username but there is no username when there is a viewer that hasn't signed in. How do I word this?
        user = User.query.filter_by(username = session['username']).first()
        user_id = user.id
        allblogs = Blog.query.filter_by(owner_id = user_id).all()
        return render_template('singleuser.html', blogs = allblogs)

      

if  __name__ == "__main__":
    app.run()