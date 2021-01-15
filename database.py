from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2 as dbapi2
import os
from user import User

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
            print(f"User inserted: {0}", user.username)
    
    def search_user_username(self, username):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user_t WHERE username = %s", (username,))
            row = cursor.fetchone()
            if(row):
                return User(row[0], row[4], row[5], row[6], row[1], row[2], row[3],  row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14])
            else:
                return None

    def search_user_email(self, email):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user_t WHERE email = %s", (email,))
            row = cursor.fetchone()
            if(row):
                return User(row[0], row[4], row[5], row[6], row[1], row[2], row[3],  row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14])
            else:
                return None 

    def search_user_id(self, userid):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user_t WHERE user_id = %s", (userid,))
            row = cursor.fetchone()
            if(row):
                return User(row[0], row[4], row[5], row[6], row[1], row[2], row[3],  row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14])
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
    #def delete_user(self, user):
