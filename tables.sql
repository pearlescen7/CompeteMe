CREATE TABLE IF NOT EXISTS holder (
    holder_id serial PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS event_t (
    event_id serial PRIMARY KEY,
    title VARCHAR(32) NOT NULL,
    event_desc VARCHAR(255),
    team_size integer NOT NULL,
    no_of_teams integer NOT NULL,
    starting_date TIMESTAMP NOT NULL,
    duration integer NOT NULL,
    event_type integer NOT NULL,
    event_status integer NOT NULL,
    event_code VARCHAR(6) UNIQUE NOT NULL,
    prize integer CHECK(prize > 0) NOT NULL,
    xp_prize integer CHECK(xp_prize > 0) NOT NULL,
    winner integer
);

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id serial PRIMARY KEY,
    size integer NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS item (
    item_id serial PRIMARY KEY,
    inventory_id integer REFERENCES inventory (inventory_id),
    item_name VARCHAR(32) NOT NULL,
    item_desc VARCHAR(255),
    item_price integer NOT NULL,
    item_pic bytea
);

CREATE TABLE IF NOT EXISTS team (
    team_id serial PRIMARY KEY, 
    event_id integer REFERENCES event_t (event_id),
    team_name VARCHAR(32) NOT NULL,
    team_size integer,
    score integer CHECK(score > 0)
);

ALTER TABLE team ADD COLUMN creator_id integer REFERENCES user_t (user_id);

CREATE TABLE IF NOT EXISTS user_t (
    user_id serial PRIMARY KEY,
    team_id integer REFERENCES team (team_id),
    inventory_id integer REFERENCES inventory (inventory_id),
    holder_id integer REFERENCES holder (holder_id),
    username VARCHAR(32) UNIQUE NOT NULL,
    u_password text NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    profile_pic bytea,
    biography VARCHAR(255),
    no_events_created integer DEFAULT 0,
    no_events_joined integer DEFAULT 0,
    no_events_won integer DEFAULT 0,
    rep_points integer DEFAULT 0,
    experience integer DEFAULT 0,
    currency integer CHECK(currency >= 0) DEFAULT 0
);

ALTER TABLE holder ADD COLUMN user_id integer REFERENCES user_t (user_id);

CREATE TABLE IF NOT EXISTS adminship (
    user_id integer REFERENCES user_t (user_id), 
    event_id integer REFERENCES event_t (event_id),
    PRIMARY KEY (user_id, event_id)
);

CREATE TABLE IF NOT EXISTS reputation (
    rep_id serial PRIMARY KEY,
    voter_id integer REFERENCES user_t (user_id),
    holder_id integer REFERENCES holder (holder_id),
    value integer NOT NULL
);

CREATE TABLE IF NOT EXISTS comment (
    comment_id serial PRIMARY KEY, 
    writer_id integer REFERENCES user_t (user_id),
    holder_id integer REFERENCES holder (holder_id),
    content VARCHAR(255) NOT NULL,
    comment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);