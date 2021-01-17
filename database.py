from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2 as dbapi2
import os, uuid
from user import User
from event import Event
from team import Team
from datetime import datetime

#POSTGRES_URL = os.getenv('POSTGRES_URL')
#POSTGRES_USER = os.getenv('POSTGRES_USER')
#POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
#POSTGRES_DB = os.getenv('POSTGRES_DB')

def get_connection():
    #con = dbapi2.connect(dbname=POSTGRES_DB, user=POSTGRES_USER, host=POSTGRES_URL, password=POSTGRES_PASSWORD)
    con = dbapi2.connect(dbname='appdb', user='postgres', host='localhost', password='196638609*')
    return con

class Database:
    def __init__(self):
        pass
    
    def add_user(self, user):
        with get_connection() as connection:
            cursor = connection.cursor()
            if user.pfp is not None:
                cursor.execute("INSERT INTO user_t (username, u_password, email, profile_pic) values (%s, %s, %s, %s)", (user.username, user.password, user.email, user.pfp)) 
            else:
                cursor.execute("INSERT INTO user_t (username, u_password, email) values (%s, %s, %s)", (user.username, user.password, user.email))
            connection.commit()
            #print("ADDING HOLDER")
            user_id = self.search_user_username(user.username).id
            cursor.execute("INSERT INTO holder (user_id) values (%s)", (user_id, ))
            #TODO: CREATE INVENTORY FOR USER 
            connection.commit()
            print(f"User inserted: {0}", user.username)
    
    def search_user_username(self, username):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user_t WHERE username = %s", (username,))
            row = cursor.fetchone()
            if(row):
                return User(row[0], row[3], row[4], row[5], row[1], row[2], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13])
            else:
                return None

    def search_user_email(self, email):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user_t WHERE email = %s", (email,))
            row = cursor.fetchone()
            if(row):
                return User(row[0], row[3], row[4], row[5], row[1], row[2], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13])
            else:
                return None 

    def search_user_id(self, userid):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user_t WHERE user_id = %s", (userid,))
            row = cursor.fetchone()
            if(row):
                return User(row[0], row[3], row[4], row[5], row[1], row[2], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13])
            else:
                return None 
    
    def update_user_id(self, id, username=None, password=None, email=None, bio=None, pfp=None):
        with get_connection() as connection:
            cursor = connection.cursor()
            if username:
                cursor.execute("UPDATE user_t SET username = %s WHERE user_id = %s", (username, id))
            if email:
                cursor.execute("UPDATE user_t SET email = %s WHERE user_id = %s", (email, id))
            if password:
                cursor.execute("UPDATE user_t SET u_password = %s WHERE user_id = %s", (generate_password_hash(password, method='sha256'), id))
            if bio:
                cursor.execute("UPDATE user_t SET biography = %s WHERE user_id = %s", (bio, id))
            if pfp:
                cursor.execute("UPDATE user_t SET profile_pic = %s WHERE user_id = %s", (pfp, id)) 
            connection.commit()

    def delete_user_pfp(self, id):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE user_t SET profile_pic = '' WHERE user_id = %s", (id,))
            connection.commit()

    def delete_user_id(self, id):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM comment WHERE writer_id = %s OR holder_id = %s", (id, id))
            cursor.execute("DELETE FROM holder WHERE user_id = %s", (id, ))
            cursor.execute("DELETE FROM user_t WHERE user_id = %s", (id,))
            connection.commit()
    
    def delete_comment_id(self, id):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM comment WHERE comment_id = %s", (id,))
            connection.commit()

    def get_comments_id(self, user_id):
        holder_id = self.get_holder_id(user_id)
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT comment.content, comment.comment_date, user_t.username, comment.comment_id FROM comment INNER JOIN user_t ON comment.writer_id = user_t.user_id WHERE comment.holder_id = %s", (holder_id, ))
            comments = cursor.fetchall()
        return comments
    
    def get_holder_id(self, user_id):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM holder WHERE user_id = %s", (user_id, ))
            row = cursor.fetchone()
        return row[0]

    def send_comment(self, current_user, holder_user, content):
        holder = self.search_user_username(holder_user)
        holder_id = self.get_holder_id(holder.id)
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO comment (writer_id, holder_id, content) values (%s, %s, %s)", (current_user.id, holder_id, content))
            connection.commit()
        return None

    def get_events(self, orderby="event_status", sort="descending", title_search='%'):
        events = []
        if(title_search == ''):
            title_search = '%'
        with get_connection() as connection:
            cursor = connection.cursor()

            if(sort == "ascending"):
                cursor.execute("SELECT * FROM event_t WHERE title LIKE %s ORDER BY $ ASC".replace("$", orderby), (title_search, ))
            else:
                cursor.execute("SELECT * FROM event_t WHERE title LIKE %s ORDER BY $ DESC".replace("$", orderby), (title_search, ))
            rows = cursor.fetchall()
            for row in rows:
                
                time_now = datetime.now()
                print(row[5])
                if (time_now > row[5]) and (row[7] == 0):
                    cursor.execute("UPDATE event_t SET event_status = 1 WHERE event_id = %s", (row[0], ))
                    connection.commit() 

                username = self.search_user_id(row[11]).username
                e = Event(id=row[0], title=row[1], desc=row[2], team_size=row[3], team_no=row[4], start=row[5], e_type=row[6], status=row[7], code=row[8], prize=row[9], xp_prize=row[10], winner=row[13], creator=username, teams_filled=row[12])
                events.append(e)
        return events

    def create_event(self, title, desc, team_size, no_teams, daytime, e_type, creator_id):
        event_code = uuid.uuid4().hex[:6].upper()
        while (self.search_event_code(event_code)):
            event_code = uuid.uuid4().hex[:6].upper()

        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO event_t (title, event_desc, team_size, no_of_teams, starting_date, event_type, event_status, event_code, prize, xp_prize, creator) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (title, desc, team_size, no_teams, daytime, e_type, 0, event_code, 200, 500, creator_id))
            connection.commit()
            event = self.search_event_code(event_code)
            cursor.execute("INSERT INTO adminship (user_id, event_id) values (%s, %s)", (creator_id, event.id))
            connection.commit()
        return str(event_code)

    def search_event_code(self, event_code):
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT starting_date FROM event_t WHERE event_code = %s", (event_code, ))
            row = cursor.fetchone()
            if row:
                time_now = datetime.now()
                print(row[0])
                if (time_now > row[0]) and (row[7] == 0):
                    cursor.execute("UPDATE event_t SET event_status = 1 WHERE event_code = %s", (event_code, ))
                    connection.commit()

            cursor.execute("SELECT * FROM event_t WHERE event_code = %s", (event_code,))
            row = cursor.fetchone()
            if row:
                username = self.search_user_id(row[11]).username
                e = Event(id=row[0], title=row[1], desc=row[2], team_size=row[3], team_no=row[4], start=row[5], e_type=row[6], status=row[7], code=row[8], prize=row[9], xp_prize=row[10], winner=row[13], creator=username, teams_filled=row[12])
                return e
            else:
                return None

    def search_adminship(self, user_id, event_id):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM adminship WHERE user_id = %s AND event_id = %s", (user_id, event_id))
            row = cursor.fetchone()
            if row:
                return True
            else:
                return False
    
    def delete_event_id(self, event_id):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM adminship WHERE event_id = %s", (event_id, ))
            cursor.execute("SELECT * FROM team WHERE event_id = %s", (event_id, ))
            teams = cursor.fetchall()
            for team in teams:
                cursor.execute("UPDATE user_t SET team_id NULL WHERE team_id = %s", (team[0], ))

            cursor.execute("DELETE FROM team WHERE event_id = %s", (event_id, ))
            cursor.execute("DELETE FROM event_t WHERE event_id = %s", (event_id, ))
            connection.commit()

    def add_admin(self, user_id, event_id):
        with get_connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute("INSERT INTO adminship (user_id, event_id) values (%s, %s)", (user_id, event_id))
                connection.commit()
                return True
            except:
                print("COULD NOT ADD")
                return False

    def del_admin(self, user_id, event_id):
        with get_connection() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute("DELETE FROM adminship WHERE user_id = %s", (user_id, ))
                connection.commit()
                return True
            except:
                print("COULD NOT DEL")
                return False
    
    def search_event_id(self, id):
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT starting_date FROM event_t WHERE event_id = %s", (id, ))
            row = cursor.fetchone()
            if row:
                time_now = datetime.now()
                print(row[0])
                if (time_now > row[0]) and (row[7] == 0):
                    cursor.execute("UPDATE event_t SET event_status = 1 WHERE event_id = %s", (id, ))
                    connection.commit()

            cursor.execute("SELECT * FROM event_t WHERE event_id = %s", (id, ))
            row = cursor.fetchone()
            if row:
                username = self.search_user_id(row[11]).username
                e = Event(id=row[0], title=row[1], desc=row[2], team_size=row[3], team_no=row[4], start=row[5], e_type=row[6], status=row[7], code=row[8], prize=row[9], xp_prize=row[10], winner=row[13], creator=username, teams_filled=row[12])
                return e
            else:
                return None

    def update_event_id(self, id, title, no_teams, desc, daytime):
        with get_connection() as connection:
            cursor = connection.cursor()
            if title:
                cursor.execute("UPDATE event_t SET title = %s WHERE event_id = %s", (title, id))
            if no_teams:
                cursor.execute("UPDATE event_t SET no_of_teams = %s WHERE event_id = %s", (no_teams, id))
            if desc:
                cursor.execute("UPDATE event_t SET event_desc = %s WHERE event_id = %s", (desc, id))
            if daytime:
                cursor.execute("UPDATE event_t SET starting_date = %s WHERE event_id = %s", (daytime, id))
            connection.commit()
        return self.search_event_id(id)

    def add_team(self, event_id, team_name, team_size, score, is_private, creator_id, team_filled):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO team (event_id, team_name, team_size, score, creator_id, is_private, team_filled) values (%s, %s, %s, %s, %s, %s, %s)", (event_id, team_name, team_size, score, creator_id, is_private, team_filled))
            cursor.execute("UPDATE event_t SET teams_filled = teams_filled + 1 WHERE event_id = %s", (event_id, ))
            connection.commit()
    
    def search_teams(self, event_id):
        teams = []
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM team WHERE event_id = %s", (event_id, ))
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    user = self.search_user_id(row[6])
                    teams.append(Team(row[0], row[1], row[2], row[3], row[4], row[5], user.username, row[7]))
            
        return teams

    def get_team_id(self, creator_id):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM team WHERE creator_id = %s", (creator_id, ))
            team = cursor.fetchone()
            return team[0]

    def fix_team_id(self, username, team_id):
        user = self.search_user_username(username)
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE user_t SET team_id = %s WHERE user_id = %s", (team_id, user.id))
            connection.commit()

    def fix_team_filled(self, validnum, username):
        user = self.search_user_username(username)
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE team SET team_filled = %s WHERE creator_id = %s", (validnum, user.id))
            connection.commit()
    
    def inc_team_filled(self, team_id):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE team SET team_filled = team_filled + 1 WHERE team_id = %s", (team_id, ))
            connection.commit()