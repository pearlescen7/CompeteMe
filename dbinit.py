import psycopg2 as dbapi2
import os 

INIT_STATEMENTS = [

"""CREATE TABLE IF NOT EXISTS holder (
    holder_id serial PRIMARY KEY
)""",

"""CREATE TABLE IF NOT EXISTS event_t (
    event_id serial PRIMARY KEY,
    title VARCHAR(32) NOT NULL,
    event_desc VARCHAR(255),
    team_size integer NOT NULL,
    no_of_teams integer NOT NULL,
    starting_date TIMESTAMP NOT NULL,
    event_type integer NOT NULL,
    event_status integer NOT NULL,
    event_code VARCHAR(6) UNIQUE NOT NULL,
    prize integer CHECK(prize > 0) NOT NULL,
    xp_prize integer CHECK(xp_prize > 0) NOT NULL
)""", 

"""CREATE TABLE IF NOT EXISTS inventory (
    inventory_id serial PRIMARY KEY,
    size integer NOT NULL DEFAULT 0
)""",

"""CREATE TABLE IF NOT EXISTS team (
    team_id serial PRIMARY KEY, 
    event_id integer REFERENCES event_t (event_id),
    team_name VARCHAR(32) NOT NULL,
    team_size integer,
    score integer CHECK(score >= 0)
)""",
    
"""CREATE TABLE IF NOT EXISTS user_t (
    user_id serial PRIMARY KEY,
    team_id integer REFERENCES team (team_id),
    inventory_id integer REFERENCES inventory (inventory_id),
    username VARCHAR(32) UNIQUE NOT NULL,
    u_password text NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    profile_pic VARCHAR(128),
    biography VARCHAR(255),
    no_events_created integer DEFAULT 0,
    no_events_joined integer DEFAULT 0,
    no_events_won integer DEFAULT 0,
    rep_points integer DEFAULT 0,
    experience integer DEFAULT 0,
    currency integer CHECK(currency >= 0) DEFAULT 0
)""",

"""CREATE TABLE IF NOT EXISTS adminship (
    user_id integer REFERENCES user_t (user_id), 
    event_id integer REFERENCES event_t (event_id),
    PRIMARY KEY (user_id, event_id)
)""",

"""CREATE TABLE IF NOT EXISTS reputation (
    rep_id serial PRIMARY KEY,
    voter_id integer REFERENCES user_t (user_id),
    holder_id integer REFERENCES holder (holder_id),
    value integer NOT NULL
)""",

"""CREATE TABLE IF NOT EXISTS comment (
    comment_id serial PRIMARY KEY, 
    writer_id integer REFERENCES user_t (user_id),
    holder_id integer REFERENCES holder (holder_id),
    content VARCHAR(255) NOT NULL,
    comment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""",

"ALTER TABLE event_t ADD COLUMN teams_filled integer DEFAULT 0;",
"ALTER TABLE event_t ADD COLUMN winner integer REFERENCES team (team_id)",
"ALTER TABLE team ADD COLUMN creator_id integer REFERENCES user_t (user_id)",
"ALTER TABLE team ADD COLUMN is_private integer",
"ALTER TABLE team ADD COLUMN team_filled integer",
"ALTER TABLE holder ADD COLUMN user_id integer REFERENCES user_t (user_id)",
"ALTER TABLE event_t ADD COLUMN creator integer REFERENCES user_t (user_id)"

]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()

if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    initialize(url)