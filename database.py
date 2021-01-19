from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2 as dbapi2
import os, uuid
from user import User
from event import Event
from team import Team
from datetime import datetime

POSTGRES_URL = os.getenv('DATABASE_URL')

def get_connection():
    con = dbapi2.connect(POSTGRES_URL)
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

    def get_events(self, orderby="event_status", sort="ascending", title_search='%'):
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
                    cursor.execute("SELECT * FROM team WHERE event_id = %s", (row[0], ))
                    teams = cursor.fetchall()
                    if teams:
                        for team in teams:
                            if(team[7] != row[3]):
                                cursor.execute("UPDATE user_t SET team_id = NULL WHERE team_id = %s", (team[0], ))
                                cursor.execute("DELETE FROM team WHERE team_id = %s", (team[0], ))

                username = self.search_user_id(row[13]).username
                team_name_temp = self.search_team_id(row[12])
                if team_name_temp:
                    team_name_temp = team_name_temp.team_name
                e = Event(id=row[0], title=row[1], desc=row[2], team_size=row[3], team_no=row[4], start=row[5], e_type=row[6], status=row[7], code=row[8], prize=row[9], xp_prize=row[10], winner=team_name_temp, creator=username, teams_filled=row[11])
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
            cursor.execute("UPDATE user_t SET no_events_created = no_events_created + 1 WHERE user_id = %s", (creator_id, ))
            connection.commit()
        return str(event_code)

    def search_event_code(self, event_code):
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM event_t WHERE event_code = %s", (event_code, ))
            row = cursor.fetchone()
            if row:
                time_now = datetime.now()
                print(row[5])
                if (time_now > row[5]) and (row[7] == 0):
                    cursor.execute("UPDATE event_t SET event_status = 1 WHERE event_code = %s", (event_code, ))
                    connection.commit()
                    cursor.execute("SELECT * FROM team WHERE event_id = %s", (row[0], ))
                    teams = cursor.fetchall()
                    if teams:
                        for team in teams:
                            if(team[7] != row[3]):
                                cursor.execute("UPDATE user_t SET team_id = NULL WHERE team_id = %s", (team[0], ))
                                cursor.execute("DELETE FROM team WHERE team_id = %s", (team[0], ))

            cursor.execute("SELECT * FROM event_t WHERE event_code = %s", (event_code,))
            row = cursor.fetchone()
            if row:
                username = self.search_user_id(row[13]).username
                team_name_temp = self.search_team_id(row[12])
                if team_name_temp:
                    team_name_temp = team_name_temp.team_name
                e = Event(id=row[0], title=row[1], desc=row[2], team_size=row[3], team_no=row[4], start=row[5], e_type=row[6], status=row[7], code=row[8], prize=row[9], xp_prize=row[10], winner=team_name_temp, creator=username, teams_filled=row[11])
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
            e = self.search_event_id(event_id)
            cursor.execute("UPDATE user_t SET no_events_created = no_events_created - 1 WHERE username = %s", (e.creator, ))
            cursor.execute("DELETE FROM adminship WHERE event_id = %s", (event_id, ))
            cursor.execute("SELECT * FROM team WHERE event_id = %s", (event_id, ))
            teams = cursor.fetchall()
            if teams:
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
                cursor.execute("SELECT team_id FROM user_t WHERE user_id = %s", (user_id, ))
                teamid  = cursor.fetchone()
                team = self.search_team_id(teamid)
                if team.event_id == event_id:
                    cursor.execute("UPDATE user_t SET team_id = NULL WHERE user_id = %s", (user_id, ))
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

            cursor.execute("SELECT * FROM event_t WHERE event_id = %s", (id, ))
            row = cursor.fetchone()
            if row:
                time_now = datetime.now()
                print(row[5])
                if (time_now > row[5]) and (row[7] == 0):
                    cursor.execute("UPDATE event_t SET event_status = 1 WHERE event_id = %s", (id, ))
                    connection.commit()
                    cursor.execute("SELECT * FROM team WHERE event_id = %s", (row[0], ))
                    teams = cursor.fetchall()
                    for team in teams:
                        if(team[7] != row[3]):
                            cursor.execute("UPDATE user_t SET team_id = NULL WHERE team_id = %s", (team[0], ))
                            cursor.execute("DELETE FROM team WHERE team_id = %s", (team[0], ))
                            cursor.execute("UPDATE event_t SET teams_filled = teams_filled - 1 WHERE event_id = %s", (id, ))

            cursor.execute("SELECT * FROM event_t WHERE event_id = %s", (id, ))
            row = cursor.fetchone()
            if row:
                username = self.search_user_id(row[13]).username
                team_name_temp = self.search_team_id(row[12])
                if team_name_temp:
                    team_name_temp = team_name_temp.team_name
                e = Event(id=row[0], title=row[1], desc=row[2], team_size=row[3], team_no=row[4], start=row[5], e_type=row[6], status=row[7], code=row[8], prize=row[9], xp_prize=row[10], winner=team_name_temp, creator=username, teams_filled=row[11])
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
            cursor.execute("SELECT * FROM team WHERE event_id = %s ORDER BY score DESC", (event_id, ))
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    user = self.search_user_id(row[5])
                    teams.append(Team(row[0], row[1], row[2], row[3], row[4], row[6], user.username, row[7]))
            
        return teams

    def get_team_id(self, creator_id):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM team WHERE creator_id = %s", (creator_id, ))
            team = cursor.fetchone()
            if team:
                return team[0]
            else:
                return None

    def fix_team_id(self, username, team_id):
        user = self.search_user_username(username)
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE user_t SET team_id = %s, no_events_joined = no_events_joined + 1 WHERE user_id = %s", (team_id, user.id))
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
            print("increasing")
            cursor.execute("UPDATE team SET team_filled = team_filled + 1 WHERE team_id = %s", (team_id, ))
            connection.commit()

    def leave_team(self, user_id, team_id):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE user_t SET no_events_joined = no_events_joined - 1 WHERE user_id = %s", (user_id, ))
            cursor.execute("UPDATE team SET team_filled = team_filled - 1 WHERE team_id = %s", (team_id, ))
            cursor.execute("UPDATE user_t SET team_id = NULL WHERE user_id = %s", (user_id, ))
            connection.commit()

    def delete_team(self, event_id, team_id):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE user_t SET team_id = NULL, no_events_joined = no_events_joined - 1 WHERE team_id = %s", (team_id, ))
            cursor.execute("UPDATE event_t SET teams_filled = teams_filled - 1 WHERE event_id = %s", (event_id, ))
            cursor.execute("DELETE FROM team WHERE team_id = %s", (team_id, ))
            connection.commit()
    
    def get_admin_events(self, user_id):
        events=[]
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT event_id FROM adminship WHERE user_id = %s", (user_id, ))
            event_ids = cursor.fetchall()
            for event_id in event_ids:
                cursor.execute("SELECT * FROM event_t WHERE event_id = %s", (event_id, ))
                row = cursor.fetchone()
                if row:
                    username = self.search_user_id(row[13]).username
                    team_name_temp = self.search_team_id(row[12])
                    if team_name_temp:
                        team_name_temp = team_name_temp.team_name
                    e = Event(id=row[0], title=row[1], desc=row[2], team_size=row[3], team_no=row[4], start=row[5], e_type=row[6], status=row[7], code=row[8], prize=row[9], xp_prize=row[10], winner=team_name_temp, creator=username, teams_filled=row[11])
                    events.append(e)
        return events
    
    def search_team_id(self, team_id):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM team WHERE team_id = %s", (team_id, ))
            row = cursor.fetchone()
            if row:
                user = self.search_user_id(row[5])
                return Team(row[0], row[1], row[2], row[3], row[4], row[6], user.username, row[7])
            else:
                return None
    
    def search_usernames_team_id(self, team_id):
        usernames=[]
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user_t WHERE team_id = %s", (team_id, ))
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    usernames.append(User(row[0], row[3], row[4], row[5], row[1], row[2], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))
        return usernames
    
    def close_event_no_teams(self, event):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE event_t SET event_status = 2 WHERE event_id = %s", (event.id, ))
            connection.commit()

    def get_admin_list(self, event_id):
        admins = []
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT user_id FROM adminship WHERE event_id = %s", (event_id, ))
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    admins.append(row[0])
        return admins
    
    def select_event_winner(self, event_id, team_id, xp_prize):
        with get_connection() as connection:
            cursor = connection.cursor()
            team = self.search_team_id(team_id)
            cursor.execute("UPDATE event_t SET winner = %s, event_status = 2 WHERE event_id = %s", (team.id, event_id))
            cursor.execute("UPDATE user_t SET no_events_won = no_events_won + 1, experience = experience + %s WHERE team_id = %s", (xp_prize, team.id))
            cursor.execute("SELECT team_id FROM team WHERE event_id = %s", (event_id, ))
            team_ids = cursor.fetchall()
            if team_ids:
                for team_id in team_ids:
                    cursor.execute("UPDATE user_t SET team_id = NULL WHERE team_id = %s", (team_id, ))
            connection.commit()
    
    def update_event_scores(self, teams, scores):
        with get_connection() as connection:
            cursor = connection.cursor()
            for i in range(len(teams)):
                cursor.execute("UPDATE team SET score = %s WHERE team_id = %s", (scores[i], teams[i].id))
            connection.commit()

    def get_max_created(self):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT username, no_events_created FROM user_t WHERE no_events_created = (SELECT MAX(no_events_created) FROM user_t)")
            row = cursor.fetchone()
            if row:
                return row
            else:
                return None
    
    def get_max_joined(self):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT username, no_events_joined FROM user_t WHERE no_events_joined = (SELECT MAX(no_events_joined) FROM user_t)")
            row = cursor.fetchone()
            if row:
                return row
            else:
                return None
    
    def get_max_winner(self):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT username, no_events_won FROM user_t WHERE no_events_won = (SELECT MAX(no_events_won) FROM user_t)")
            row = cursor.fetchone()
            if row:
                return row
            else:
                return None

    def get_count_events(self):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM event_t")
            row = cursor.fetchone()
            return row[0]

    def get_open_events(self):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT event_id FROM event_t EXCEPT SELECT event_id FROM event_t WHERE ((event_status = 1) OR (event_status = 2))")
            row = cursor.fetchall()
            return len(row)
    
    def get_on_events(self):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT event_id FROM event_t EXCEPT SELECT event_id FROM event_t WHERE ((event_status = 0) OR (event_status = 2))")
            row = cursor.fetchall()
            return len(row)

    def get_closed_events(self):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT event_id FROM event_t EXCEPT SELECT event_id FROM event_t WHERE ((event_status = 0) OR (event_status = 1))")
            row = cursor.fetchall()
            return len(row)

    def get_avg_exp(self):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT AVG(experience) FROM user_t")
            return cursor.fetchone()[0]