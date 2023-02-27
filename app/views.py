import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm
from .form import UploadForm


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
@login_required 
def upload():
    if not session.get('logged_in'):
        abort(401)

    # Instantiate your form class
    form = UploadForm()

    # Validate file upload on submit
    if request.method == 'POST':
        if form.validate_on_submit():
        # Get file data and save to your uploads folder
            image - form.image.data
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            flash('File Saved', 'success')
            return redirect(url_for('home')) # Update this to redirect the user to a route that displays all uploaded image files
        else:
            flash_errors(form)
    if request.method == 'GET':
        return render_template('upload.html', form=form)

def get_uploaded_images():
    lst=[]
    rootdir = os.getcwd()
    for subdir, dirs, files in os.walk(rootdir + '/uploads/'):
         for file in files[1:]:
             lst.append(file)
    return lst

@app.route('/uploads/<filename>')
def get_image(filename):
    rootdir = os.getcwd()
    return send_from_directory(os.path.join(rootdir,app.config['UPLOAD_FOLDER']), filename)

@app.route('/files',methods=['GET'])
@login_required 
def files():
    if not session.get('logged_in'):
        abort(401)
    return render_template('files.html',filenames=get_uploaded_images())

@app.route('/login', methods=['POST', 'GET'])
def login():

    if current_user.is_authenticated:
            # if user is already logged in, just redirect them to our secure page
        # or some other page like a dashboard
        return redirect(url_for('secure_page'))

    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    # Login and validate the user.
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Query our database to see if the username and password entered
        # match a user that is in the database.
        user = db.session.execute(db.select(UserProfile).filter_by(username=username)).scalar()

        if user is not None and check_password_hash(user.password, password):
            remember_me = False

            if 'remember_me' in request.form:
                remember_me = True

            # If the user is not blank, meaning if a user was actually found,
            # then login the user and create the user session.
            # user should be an instance of your `User` class
            login_user(user, remember=remember_me)

            flash('Logged in successfully.', 'success')

            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
        else:
            flash('Username or Password is incorrect.', 'danger')

    flash_errors(form)
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    # Logout the user and end the session
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


     # form = LoginForm()

    # change this to actually validate the entire form submission
    # and not just one field
     # if form.username.data:
        # Get the username and password values from the form.

        # Using your model, query database for a user based on the username
        # and password submitted. Remember you need to compare the password hash.
        # You will need to import the appropriate function to do so.
        # Then store the result of that query to a `user` variable so it can be
        # passed to the login_user() method below.

        # Gets user id, load into session
        #  login_user(user)

        # Remember to flash a message to the user
         # return redirect(url_for("home"))  # The user should be redirected to the upload form instead
    #  return render_template("login.html", form=form)

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
