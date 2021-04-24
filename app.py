from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension, toolbar
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

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

## USER ROUTES

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Show form to register a new user, handle submission."""

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        fn = form.first_name.data
        ln = form.last_name.data

        new_user = User.register(username, password, email, fn, ln)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username
        
        flash('Account successfully created.')
        return redirect(f'/users/{new_user.username}')

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
            flash('Logged in.')
            session['username'] = user.username
            return redirect(f'/users/{user.username}')

        else:
            form.username.errors = ['Invalid username/password.']
            form.password.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Logs out users, clears user ID from session."""

    session.pop('username')
    return redirect('/')


@app.route('/users/<username>')
def user_page(username):
    """Page a user goes to when account successfully created or logged in."""

    user = User.query.filter_by(username=username).first_or_404()

    if "username" not in session:
        return redirect('/')

    else:
        return render_template('user.html', user=user)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Delete user (and their feedback) from database and return to homepage."""

    user = User.query.filter_by(username=username).first_or_404()

    if session['username'] != username:
        return redirect(f'/users/{username}')

    else:
        db.session.delete(user)
        db.session.commit()
        return redirect('/')


## FEEDBACK ROUTES

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def new_feedback(username):
    """Display form to add feedback from a user, and handle submission."""

    form = FeedbackForm()

    if session['username'] != username:
        return redirect('/')
    
    else:
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data

            feedback = Feedback(title=title, content=content, username=username)
            db.session.add(feedback)
            db.session.commit()

            return redirect(f'/users/{username}')

        else:
            return render_template('newfb.html', form=form)
        

@app.route('/feedback/<int:fb_id>/update', methods=['GET', 'POST'])
def edit_feedback(fb_id):
    """Display form to edit feedback from a user, and handle submission."""

    feedback = Feedback.query.get_or_404(fb_id)
    form = FeedbackForm(obj=feedback)
    
    if session['username'] != feedback.username:
        return redirect('/')
    
    else:
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data

            db.session.commit()

            return redirect(f'/users/{feedback.username}')

        else:
            return render_template('updatefb.html', form=form, feedback=feedback)


@app.route('/feedback/<int:fb_id>/delete', methods=['POST'])
def delete_feedback(fb_id):
    """Delete feedback from DB and redirect to user page."""

    feedback = Feedback.query.get_or_404(fb_id)

    if session['username'] != feedback.username:
        return redirect(f'/users/{feedback.username}')

    else:
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f'/users/{feedback.username}')