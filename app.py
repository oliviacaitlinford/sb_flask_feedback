from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension, toolbar
from models import connect_db, db, User
from forms import RegisterForm, LoginForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config["SECRET_KEY"] = "if98yr9dwf"

connect_db(app)
db.create_all()
toolbar = DebugToolbarExtension(app)

@app.route('/')
def homepage():
    """Homepage for app."""

    return render_template('/index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Show form to register a new user, handle submission."""

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        fn = form.first_name.data
        ln = form.last_name.data
        email = form.email.data

        new_user = User.register(username, password, fn, ln, email)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account successfully created.')
        return redirect('/')

    else:
        return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Show form to login a user, handle submission."""

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)

        if user:
            return redirect('/')
        else:
            form.username.errors = ['Invalid username/password.']
            form.password.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)
