from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2 as dbapi2
import os
from user import User
from event import Event

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

    def get_events(self, orderby='title', sort="ascending", title_search='%'):
        events = []
        with get_connection() as connection:
            cursor = connection.cursor()
            if(sort == "ascending"):
                cursor.execute("SELECT * FROM event_t WHERE title LIKE %s ORDER BY (values (%s)) ASC", (title_search, orderby))
            else:
                cursor.execute("SELECT * FROM event_t WHERE title LIKE %s ORDER BY (values (%s)) DESC", (title_search, orderby))
            rows = cursor.fetchall()
            for row in rows:
                e = Event(id=row[0], title=row[1], desc=row[2], team_size=row[3], team_no=row[4], start=row[5], duration=row[6], e_type=row[7], status=row[8], code=row[9], prize=row[10], xp_prize=row[11], winner=row[12], creator=row[13])
                events.append(e)
        return events
