from flask import Flask, render_template, request, url_for, redirect, flash, send_file, send_from_directory
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import Database
from user import User
from uuid import uuid4
import os
import psycopg2 as dbapi2


UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
db = Database()
app.config["db"] = db
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

def make_unique(string):
    ident = uuid4().__str__()[:8]
    return f"{ident}-{string}"

@login_manager.user_loader
def load_user(userid):
    return db.search_user_userid(userid)

@app.route("/landing_page")
@app.route("/")
def landing_page():
    return render_template("index.html")

@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if request.files:
            
            pfp = request.files["file_nm"]
            #pfp = pfp.read()
            filename = secure_filename(pfp.filename)
            filename = make_unique(filename)
            
        user = User(0,username=request.form.get("mem_name"), password=generate_password_hash(request.form.get("password"), method='sha256'), email=request.form.get("emailid"), pfp=filename)
           
        #if passwords don't match
        if (request.form.get("password") != request.form.get("cpassword")):
            flash("Passwords don't match")
            return render_template("signup.html")

        #if any of the fields are empty except pfp
        elif (request.form.get("mem_name") == ""):
            flash("Username field can't be empty")
            return render_template("signup.html")
        
        elif (request.form.get("password") == ""):
            flash("Password field can't be empty")
            return render_template("signup.html")

        elif (request.form.get("emailid") == ""):
            flash("Email field can't be empty")
            return render_template("signup.html")
        
        #if user already exists
        elif db.search_user_username(user.username) is not None:
            flash("Username already exists")
            return render_template("signup.html")
        
        elif db.search_user_email(user.email) is not None:
            flash("Email already exists")
            return render_template("signup.html")

        try:
            db.add_user(user)
            pfp.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        except:
            flash("Error occured while adding to database.")
            return render_template("signup.html")

        return redirect(url_for("signup_success"))

    else:
        return render_template("signup.html")

@app.route("/signup_success")
def signup_success():
    return render_template("signup_success.html")

@app.route("/login", methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember")
        user = db.search_user_username(username)

        if not user or not check_password_hash(user.password, password):
            flash("Please check your login details.")
            return redirect(url_for("login"))
        
        login_user(user, remember=remember)
        return redirect(url_for("profile"))
    else:
        return render_template("login.html")


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("landing_page"))


if __name__ == "__main__":
    app.run(debug=True)