from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm, DeleteForm
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def root():
    """root route that redirects to registration page"""
    
    return render_template("home.html")

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Page with form to register user"""
    
    if "username" in session:
        return redirect(f"/users/{session['username']}")
    
    
    form = UserForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        
        #create new user from data collected from form
        
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.username
        return redirect(f"/users/{new_user.username}")
        #if new_user passes, redirects to secret page
        
        
    return render_template('users/register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_user():
    """Login form or handle login"""

    if "username" in session:
        return redirect(f"users/{session['username']}")
    
    # render login form
        
    form = LoginForm()
        
    #submit and get data from form
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
            
        #verify username/password
        user = User.authenticate(username, password)
        if user:
            session['user_id'] = user.username
            return redirect(f"users/{user.username}")
        else:
            flash("Invalid username/password")
            return render_template("users/login.html", form=form)
        
    return render_template('users/login.html', form=form)
    
@app.route('/users/<username>')
def show_secret(username):
    #verify user is logged in before seeing secret.html
    if "user_id" not in session:
        flash("Please login first")
        return redirect('/login')
    
    user = User.query.get(username)
    
    
    return render_template("/users/list.html", user=user)
 
@app.route('/logout')
def logout_user():
    """logout of app"""
    session.pop('user_id')
    return redirect('/')        

@app.route('/users/<username>/delete')
def delete_user(username):
    if "user_id" not in session:
        flash("Please login first")
        return redirect('/login')
    form = UserForm()
    
    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('user_id')
    
    return render_template('/users/register.html', user=user, form=form)

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    
    if "user_id" not in session or username != session["user_id"]:
        raise Unauthorized()
    
    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        
    
        feedback = Feedback(title=title, content=content, username=username)

        db.session.add(feedback)
        db.session.commit()
        
        return redirect(f"/users/{feedback.username}")

    else:
        return render_template("feedback/add.html", form=form)
    
@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):
    
    feedback = Feedback.query.get(feedback_id)
    
    if "user_id" not in session or feedback.username != session['user_id']:
        raise Unauthorized()
    
    form = FeedbackForm(obj=feedback)
    
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")
    
    return render_template('/feedback/edit.html', form=form, feedback=feedback)

@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_post(feedback_id):
    
    feedback = Feedback.query.get(feedback_id)
    
    if "user_id" not in session or feedback.username != session['user_id']:
        raise Unauthorized()
    
    
    form = DeleteForm()
    
    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()
        
    return redirect(f"/users/{feedback.username}")   
    
    
    