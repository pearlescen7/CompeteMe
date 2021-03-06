from flask import Flask, render_template, request, url_for, redirect, flash, send_file, send_from_directory
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import Database
from user import User
from event import Event
from team import Team
from uuid import uuid4
from datetime import datetime
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

@app.route("/landing_page/")
@app.route("/")
def landing_page():
    return render_template("index.html")

@app.route("/signup/", methods = ['GET', 'POST'])
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
        
        elif (len(request.form.get("mem_name")) > 32) or (len(request.form.get("mem_name")) < 4):
            flash("Username must be between 4-32 characters.")
            return render_template("signup.html")
        
        elif (request.form.get("password") == ""):
            flash("Password field can't be empty")
            return render_template("signup.html")

        elif (request.form.get("emailid") == ""):
            flash("Email field can't be empty")
            return render_template("signup.html")
        
        elif (len(request.form.get("password")) < 8):
            flash("Password should be at least 8 characters.")
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

@app.route("/signup_success/")
def signup_success():
    return render_template("signup_success.html")

@app.route("/login/", methods = ['GET', 'POST'])
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

@app.route("/delete/<commentid>")
@login_required
def delete_comment(commentid):
    db.delete_comment_id(commentid)
    return redirect(url_for("profile"))

@app.route("/profile/", methods = ['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        db.send_comment(current_user, current_user.username, request.form.get("commentfield"))
        
    comments = db.get_comments_id(current_user.id)
    return render_template("profile.html", comments=comments)

@app.route("/profile/<username>", methods = ['GET', 'POST'])
@login_required
def anon_profile(username):
    if request.method == 'POST':
        db.send_comment(current_user, username, request.form.get("commentfield"))
    user = db.search_user_username(username)
    if user is None:
        return render_template("error.html")
    if user.id == current_user.id:
        return redirect(url_for("profile"))
    comments = db.get_comments_id(user.id)
    return render_template("anon_profile.html", user=user, comments=comments)

@app.route("/edit_profile/", methods = ['GET', 'POST'])
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
                elif len(username) < 4 or len(username) > 32:
                    flash("Username must be between 4-32 characters")
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
                
                elif (len(newpassword) < 8):
                    flash("New password should be at least 8 characters.")
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
                return redirect(url_for("edit_profile"))
            
            except:
                flash("Error occured while adding to database.")
                return render_template("edit_profile.html")

        elif "deletebut" in request.form.keys():
            filename = current_user.pfp
            db.delete_user_id(current_user.id)
            if filename:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("0")
            logout_user()
            return render_template("login.html")

        elif "photobut" in request.form.keys():
            filename = current_user.pfp
            db.delete_user_pfp(current_user.id)
            if filename:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("0") 
            return redirect(url_for("edit_profile"))
        else:
            flash("Error: Nothing is posted.")
            return render_template("edit_profile.html")
    else:    
        return render_template("edit_profile.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/search_events/', methods=['GET', 'POST'])
@login_required
def search_events():
    if request.method == 'POST':
        orderby = request.form.get("orderby")
        sort = request.form.get("sort")
        title_search = request.form.get("title_search")
        if orderby == "Title":
            orderby = "title"
        elif orderby == "Team Size":
            orderby = "team_size"
        elif orderby == "Starting Time":
            orderby = "starting_date"
        elif orderby == "Type":
            orderby = "event_type"
        elif orderby == "Status":
            orderby = "event_status"
        elif orderby == "XP Prize":
            orderby = "xp_prize"
        elif orderby == "Prize":
            orderby = "prize"
        elif orderby == "Teams Filled":
            orderby = "teams_filled"
        #print(sort)
        events = db.get_events(orderby=orderby, sort=sort, title_search=title_search)
        #print(events[0].title)
        #print(events[1].title)
        #print(events[2].title)
        #print(events[3].title)
        return render_template("search_events.html", events=events)
        #post method to search different criterias
    else:
        events = db.get_events()
        return render_template("search_events.html", events=events)

@app.route('/search_users/', methods=['GET', 'POST'])
@login_required
def search_users():
    if request.method == 'POST':
        username = request.form.get("username")
        return redirect(url_for("anon_profile", username=username))
    else:
        return render_template("search_users.html")

@app.route("/create_events/", methods=['POST', 'GET'])
@login_required
def create_events():
    if request.method == 'POST':
        title = request.form.get("title")
        desc = request.form.get("desc")
        team_size = request.form.get("team_size")
        no_teams = request.form.get("no_teams")
        daytime = request.form.get("daytime")
        e_type = request.form.get("type")
        if title == "":
            flash("Event title can't be empty.")
            return render_template("create_events.html")
        if team_size == "":
            flash("Team size can't be empty.")
            return render_template("create_events.html")
        if no_teams == "":
            flash("Number of teams can't be empty.")
            return render_template("create_events.html")
        if daytime == "":
            flash("Starting time can't be empty.")
            return render_template("create_events.html")
        if datetime.fromisoformat(daytime) < datetime.now() :
            flash("Starting time can't be before now.")
            return render_template("create_events.html")
        if e_type == "Leaderboard":
            e_type = 0
        #map event types to numbers
        code = db.create_event(title=title, desc=desc, team_size=team_size, no_teams=no_teams, daytime=daytime, e_type=e_type, creator_id=current_user.id)
        return redirect(url_for("show_event", eventcode=code))
        #when you create a new event go to manage page
    else:
        return render_template("create_events.html")

@app.route("/<eventcode>", methods=['POST', 'GET'])
@login_required
def show_event(eventcode):
    event = db.search_event_code(eventcode) 
    if event is not None:
        isadmin = db.search_adminship(current_user.id, event.id)
        teams = db.search_teams(event.id)
        winnerteam = event.winner
        admin_ids = db.get_admin_list(event.id)
        admins = []
        for admin_id in admin_ids:
            admins.append(db.search_user_id(admin_id).username)
    else:
        return render_template("error.html")

    if request.method == 'POST':
        if "editbut" in request.form.keys():
            return redirect(url_for("edit_event", ecode=eventcode))
        elif "managebut" in request.form.keys():
            return redirect(url_for("manage_results", eventcode=eventcode))
        elif "joinbut" in request.form.keys():
            try:
                db.fix_team_id(current_user.username, request.form.get("joinbut"))
                db.inc_team_filled(request.form.get("joinbut"))
                flash("0")
            except:
                flash("1")
            finally:
                return redirect(url_for("show_event", eventcode=event.code))
        elif "leavebut" in request.form.keys():
            db.leave_team(current_user.id, current_user.team_id)
            flash("2")
            return redirect(url_for("show_event", eventcode=event.code))
        elif "delbut" in request.form.keys():
            db.delete_team(event.id, current_user.team_id)
            flash("3")
            return redirect(url_for("show_event", eventcode=event.code))
    else:
        return render_template("show_event.html", event=event, isadmin=isadmin, teams=teams, admins=admins, winnerteam=winnerteam)
        

@app.route("/edit_event/<ecode>", methods=['POST', 'GET'])
@login_required
def edit_event(ecode):
    event = db.search_event_code(ecode)
    if event:
        isadmin = db.search_adminship(current_user.id, event.id)
        if not isadmin:
            return "You are not allowed to visit this page."
    else:
        return render_template("error.html")
    
    if request.method == 'POST':
        if "deletebut" in request.form.keys():
            #delete event
            db.delete_event_id(event.id)
            flash("Event deleted successfully.")
            return redirect(url_for("manage_events"))
        
        elif "savebut" in request.form.keys():
            title = request.form.get("title")
            desc = request.form.get("desc")
            no_teams = request.form.get("no_teams")
            daytime = request.form.get("daytime")
            add_admin = request.form.get("add_admin")
            del_admin = request.form.get("del_admin")

            if title == '':
                flash("Title can't be empty.")
                return render_template("edit_event.html", event=event, del_ad=None, add_ad=None)
            elif no_teams != '':
                if int(no_teams) < event.teams_filled:
                    flash("New number of teams can't be smaller than the number of teams that are already signed up for the event.")
                    return render_template("edit_event.html", event=event, del_ad=None, add_ad=None)
                elif (int(no_teams) < 2) or (int(no_teams) > 128):
                    flash("Number of teams must be between 2 and 128.")
                    return render_template("edit_event.html", event=event, del_ad=None, add_ad=None)
            elif len(desc) > 255:
                flash("Description can't be longer than 255 characters")
                return render_template("edit_event.html", event=event, del_ad=None, add_ad=None)
            elif daytime != '':
                if datetime.fromisoformat(daytime) < datetime.now():
                    flash("Starting time can't be before now.")
                    return render_template("edit_event.html", event=event, del_ad=None, add_ad=None)

            try:
                add_admin = add_admin.split(",")
                del_admin = del_admin.split(",")

                print(add_admin)
                print(del_admin)
                
                added_admins=[]
                deleted_admins=[]
                
                for admin in add_admin:
                    user = db.search_user_username(admin)
                    if user:
                        res = db.add_admin(user.id, event.id)
                        if res:
                            added_admins.append(admin)
                        else:
                            flash("1")
            
                for admin in del_admin:
                    user = db.search_user_username(admin)
                    if user:
                        res = db.del_admin(user.id, event.id)
                        if res:
                            deleted_admins.append(admin)
                        else:
                            flash("2")
                
                event = db.update_event_id(id=event.id, title=title, desc=desc, no_teams=no_teams, daytime=daytime)
                flash("0")
                return render_template("edit_event.html", event=event, del_ad=deleted_admins, add_ad=added_admins)
            except:
                flash("3")
                return render_template("edit_event.html", event=event, del_ad=None, add_ad=None)
    
    return render_template("edit_event.html", event=event, del_ad=None, add_ad=None)

@app.route("/create_team/<eventcode>", methods=['POST','GET'])
@login_required
def create_team(eventcode):
    event = db.search_event_code(eventcode)
    isadmin = db.search_adminship(current_user.id, event.id)
    if (event.teams_filled < event.team_no) and (not isadmin) and ((current_user.team_id == '') or (current_user.team_id == None)):
        if request.method == 'POST':
            team_name = request.form.get("team_name")
            user_list = request.form.get("user_list")
            is_private = request.form.get("is_private")
            user_list = user_list.split(",")
            valid_user = 0
            for user in user_list:
                if db.search_user_username(user):
                    valid_user += 1
            if(valid_user >= int(event.team_size)):
                flash("User list too long.")
                return render_template("create_team.html", event=event)
            elif (valid_user != event.team_size-1) and (is_private is not None):
                flash("You selected private but didn't give enough valid usernames.")
                return render_template("create_team.html", event=event)
            elif (len(team_name) < 3) or (len(team_name) > 32):
                flash("Team name must be between 3-32 characters.")
                return render_template("create_team.html", event=event)
            if is_private is not None:
                is_private = 1
            else:
                is_private = 0

            db.add_team(event_id=event.id, team_name=team_name, team_size=event.team_size, score=0, is_private=is_private, creator_id=current_user.id, team_filled=1)
            db.fix_team_id(current_user.username, db.get_team_id(current_user.id))
            validnum = 1
            for username in user_list:
                if (username != '') and (username != None):
                    user = db.search_user_username(username)
                    admin = db.search_adminship(user.id, event.id)
                    if not admin:
                        db.fix_team_id(username, db.get_team_id(current_user.id))
                        validnum += 1
                    else:
                        flash("Admins can't be added to teams.")
            db.fix_team_filled(validnum, current_user.username)
            return redirect(url_for("show_event", eventcode=event.code))

        else:
            return render_template("create_team.html", event=event)
    else:
        return render_template("error.html")

@app.route("/manage_events/")
@login_required
def manage_events():
    events = db.get_admin_events(current_user.id)
    curteam = db.search_team_id(current_user.team_id)
    curevent = None
    if curteam:
        curevent = db.search_event_id(curteam.event_id)
    return render_template("manage_events.html", events=events, curteam=curteam, curevent=curevent)

@app.route("/team/<teamid>", methods=['POST', 'GET'])
@login_required
def show_team(teamid):
    if request.method == 'POST':    
        if "leavebut" in request.form.keys():
            db.leave_team(current_user.id, current_user.team_id)
            flash("You left your current team.")
            return redirect(url_for("manage_events"))
        elif "delbut" in request.form.keys():
            team = db.search_team_id(teamid)
            event = db.search_event_id(team.event_id)
            db.delete_team(event.id, current_user.team_id)
            flash("You deleted your team.")
            return redirect(url_for("manage_events"))
    team = db.search_team_id(teamid)
    if team:
        event = db.search_event_id(team.event_id)
        users = db.search_usernames_team_id(teamid)
        return render_template("show_team.html", team=team, users=users, event=event)
    else:
        return render_template("error.html")

@app.route("/manage_results/<eventcode>", methods=['POST', 'GET'])
@login_required
def manage_results(eventcode):
    event = db.search_event_code(eventcode)
    if (event != None):
        isadmin = db.search_adminship(current_user.id, event.id)
        if (isadmin):
            teams = db.search_teams(event.id)
        else:
            return render_template("error.html")       
    else:
        return render_template("error.html")

    if request.method == 'POST':
        if "update" in request.form.keys():
            teams = db.search_teams(event.id)
            scores = []
            if teams:
                for team in teams:
                    scores.append(request.form.get("score-"+str(team.id)))
            if not scores:
                flash("5")
                return redirect(url_for("show_event", eventcode=event.code))
            db.update_event_scores(teams, scores)
            return redirect(url_for("show_event", eventcode=event.code))
        elif "winner" in request.form.keys():
            db.select_event_winner(event.id, request.form.get("winner"), event.xp_prize)
            return redirect(url_for("show_event", eventcode=event.code))
        else:
            return render_template("error.html")
    else:
        return render_template("manage_results.html", teams=teams, event=event)

@app.route("/hall_of_fame")
def hall_of_fame():
    cu = db.get_max_created()
    ju = db.get_max_joined()
    wu = db.get_max_winner()
    sum_e = db.get_count_events()
    open_e = db.get_open_events()
    on_e = db.get_on_events()
    cl_e = db.get_closed_events()
    avg_exp = int(db.get_avg_exp())
    return render_template("hall_of_fame.html", cu=cu, ju=ju, wu=wu, sum_e=sum_e, open_e=open_e, on_e=on_e, cl_e=cl_e, avg_exp=avg_exp)


@app.route("/close_event/<eventcode>")
@login_required
def close_event(eventcode):
    event = db.search_event_code(eventcode)
    if (event != None):
        isadmin = db.search_adminship(current_user.id, event.id)
        if not isadmin:
            return render_template("error.html")
    else:
        return render_template("error.html")

    db.close_event_no_teams(event)
    return redirect(url_for("manage_events"))

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("landing_page"))

@app.errorhandler(404)
def error(e):
    return render_template("error.html")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)