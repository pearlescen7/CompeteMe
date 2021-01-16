class Event():
    def __init__(self, title, team_size, team_no, start, duration, e_type, status, code, creator, id=None, desc=None, prize=1000, xp_prize=200, winner=None):
        self.id = id
        self.title = title
        self.desc = desc
        self.team_size = team_size
        self.team_no = team_no
        self.start = start
        self.duration = duration
        self.e_type = e_type
        self.status = status
        self.code = code
        self.prize = prize
        self.xp_prize = xp_prize
        self.winner = winner
        self.creator = creator