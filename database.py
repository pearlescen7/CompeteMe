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
            cursor.execute("INSERT INTO user_t (username, u_password, email, profile_pic) values (%s, %s, %s, %s)", (user.username, user.password, user.email, user.pfp)) 
            connection.commit()
            print(f"User inserted: {0}", user.username)
            pass
    
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
    def search_user_userid(self, userid):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user_t WHERE user_id = %s", (userid,))
            row = cursor.fetchone()
            if(row):
                return User(row[0], row[4], row[5], row[6], row[1], row[2], row[3],  row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14])
            else:
                return None 
    #def delete_user(self, user):
