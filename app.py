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
    return db.search_user_id(userid)

@app.route("/landing_page")
@app.route("/")
def landing_page():
    return render_template("index.html")

@app.route("/signup", methods = ['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if request.files["file_nm"].filename != '':
            
            print("SIGNUP FILE")
            print(request.files)
            print(request.form)
            pfp = request.files["file_nm"]
            #pfp = pfp.read()
            filename = secure_filename(pfp.filename)
            filename = make_unique(filename)
        else: 
            print("NO SIGNUP FILE?")
            filename = None
        
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
            if filename:
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

@app.route("/edit_profile", methods = ['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        if "savebut" in request.form.keys():
            #print(request.form)
            #print(request.files)
            if request.files["file_nm"].filename != '':

                pfp = request.files["file_nm"]
                filename = secure_filename(pfp.filename)
                filename = make_unique(filename)
            
            else:
                filename = None

            username = request.form.get("username")
            email = request.form.get("email")
            bio = request.form.get("bio")
            curpassword = request.form.get("curpassword")
            newpassword = request.form.get("newpassword")
            newpassword2 = request.form.get("newpassword2")

            user = db.search_user_username(username)
            if user is not None:
                if (user.username != current_user.username):
                    flash("Username already exists.")
                    return render_template("edit_profile.html")
                else:
                    username = None

            user = db.search_user_email(email)
            if user is not None:
                if (user.email != current_user.email):
                    flash("Email already exists.")
                    return render_template("edit_profile.html")
                else:
                    email = None
            
            if curpassword or newpassword or newpassword2:

                if not check_password_hash(current_user.password, curpassword):
                    flash("Current password is wrong.")
                    return render_template("edit_profile.html")
                
                elif (newpassword != newpassword2):
                    flash("Passwords don't match.")
                    return render_template("edit_profile.html")
            else:
                curpassword = None
                newpassword = None
                newpassword2 = None

            try:
                #print(filename)
                db.update_user_id(current_user.id, username=username, email=email, bio=bio, password=newpassword, pfp=filename)
                if filename:
                    #print("UPDATING PFP")
                    pfp.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash("0") 
                return render_template("edit_profile.html")
            
            except:
                flash("Error occured while adding to database.")
                return render_template("edit_profile.html")

        elif "deletebut" in request.form.keys():
            filename = current_user.pfp
            db.delete_user_id(current_user.id)
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("0")
            return render_template("login.html")

        elif "photobut" in request.form.keys():
            filename = current_user.pfp
            db.delete_user_pfp(current_user.id)
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("0") 
            return render_template("edit_profile.html")
        else:
            flash("Error: Nothing is posted.")
            return render_template("edit_profile.html")
    else:    
        return render_template("edit_profile.html")

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