from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Column, db.ForeignKey('user.id'))
    

    def __init__(self, name, body, owner):
        self.name = name
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

    def __repr__(self):
        return str(self.username)

@app.before_request
def require_login():
    allowed_routes = ('login', 'blog', 'signup', 'singleblog', 'index', 'home',
        'oneblog', 'userpage', 'userposts')
    if 'user' not in session and request.endpoint not in allowed_routes:
        return redirect('login')

@app.route("/")
def index():
    return redirect("/blog")

@app.route( "/blog" )
def home():
    blogs = Blog.query.all()
    welcome = "Not logged in"
    if 'user' in session:
        welcome = "logged in as: " + session['user']

    return render_template('home.html', title = "Simple blog by Kay", blogs= blogs, 
    welcome= welcome)


@app.route('/add', methods = ['POST', 'GET'])
def AddBlog():
    error = {"name_blank": "", "body_blank": "" }
    new_name = ""
    new_body = ""

welcome = "Logged in as: " = session['user']
existing_user = user.query.filter_by(username= sesssion['user']) .first()

if request.method == 'POST':
    new_name = request.form["name"]
    new_body = request.form["body"]

    if new_name == "" : 
        error["name_blank"] = "Enter a name for your blog"

    if new_body == "" :
        error["body_blank"] = "Enter some text for your blog's body"

    if error["name_blank"] == "" and error["body_blank"] == "":
        new_blog = Blog(new_name, new_body, existing_user) 
        db.session.add(new_blog) 
        db.session.add(new_blog) 
        author = user.query.filter_by(id= new_blog.owner_id) .first()
        return redirect("/singleblog?blog_name="+new_name)

    return render_template('add.html', name="Add a blog post",
        add_body= new_body, add_name= new_name,
        name_blank= error["name_blank"], body_blank= error["body_blank"],
        welcome= welcome

@app.route("/singleblog")
def oneblog(): 
    welcome = "Not logged in"
    if 'user' in session:
        welcome = "Logged in as: " + session['user']

    name = request.args.get('blog_name')
    if name:
        existing_blog = Blog.query.filter_by(name= name).first()
        author = User.query.filter_by(id = existing_blog.owner_id) .first()
        return render_template("singleblog.html",
            name= existing_blog.title, body= existing_blog.body,
            author= author.username, welcome= welcome)


@app.route("/userpage")
def Userposts():
    welcome = "Not logged in"
    if 'user' in session:
        welcome = " Logged in as: " + session['user']

    user = request.args.get('user_link')
    if user:
        existing_user = User.query.filter_by(username= user) .first()
        user_posts = existing_user.blogs
        return render_template("Userpage.html", welcome= welcome,
        name= user+" 's posts", blogs= user_posts)


    user_list = User.query.all()
    return render_template("Allusers.hmtl", title= "All Users",
        welcome= welcome, user_list= user_list)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    error = {"name_error": "", "pass_error": "", "verify_error": ""}
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if username == "":
            error["name_error"] = "Username cannot be blank"
        if password == "":
            error["pass_error"] = "Password cannot be blank"
        elif len(password) <3:
            error["pass_error"] = "Password must be more than three characters long"
        else:
            if password != verify:
                error["verify_error"] = "Password and Verify must match"

        existing_user = User.query.filter_by(username= username).first()
        if existing_user:
            error["name_error"] = "There is already someone with that username"

        if error["name_error"] == "" and error["pass_error"] == "" and error["verify"]:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['user'] = new_user.username
            return redirect("/blog")

@app.route("/login", methods=['POST', 'GET'])
def login():
    error = {"name_error": "", "pass_error": ""}
    username = ""

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username= username) first()
        if existing_user:
            if password == "":
                error["pass_error"] = "Password cannot be blank."

            elif existing_user.password == password:
                session['user'] existing_user.username
                return redirect("/blog")
            else:
                error["pass_error"] = "Invalid password"
        else:
            error["name_error"] = "Invalid username. Try again or Signup."
    return render_template("signup.html", name="Signup",
        name_error= error["name_error"], pass_error= error["pass_error"],
        username = username)

@app.route("/logout", methods = ['POST, GET'])
def logout():
    if 'user' in session:
        del session['user']
    return redirect('/blog')


if __name__ == "__main__":
    app.run()