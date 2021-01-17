from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password, email, team_id=None, inventory_id=None, pfp=None, bio=None, no_events_created=0, no_events_joined=0, no_events_won=0, rep_points=0, experience=0, currency=0):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.pfp = pfp
        self.bio = bio
        self.team_id = team_id
        self.no_events_created = no_events_created
        self.no_events_joined = no_events_joined
        self.no_events_won = no_events_won
        self.rep_points = rep_points
        self.experience = experience
        self.currency = currency
    
    def get_id(self):
        return self.id