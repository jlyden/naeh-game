import pickle
from app import db


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    round_count = db.Column(db.Integer, nullable=False)
    board_name = db.Column(db.String, nullable=False)
    beads_in = db.Column(db.Integer, default=0)
    beads_out = db.Column(db.Integer, default=0)
    end_count = db.Column(db.Integer, nullable=False, default=0)
    note = db.Column(db.String)

    def __repr__(self):
        return "<Record: Game %r, Round %r, Board %r >" % (self.game_id,
                                                           self.round_count,
                                                           self.board_name)

    def __init__(self, game_id, round_count, board_name):
        self.game_id = game_id
        self.round_count = round_count
        self.board_name = board_name


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    round_count = db.Column(db.Integer, nullable=False)
    board_played = db.Column(db.String)
    moves = db.Column(db.PickleType)

    def __repr__(self):
        return "<Log: Game %r, Round %r, Board %r >" % (self.game_id,
                                                        self.round_count,
                                                        self.board_played)

    def __init__(self, game_id, round_count, board_played, moves):
        self.game_id = game_id
        self.round_count = round_count
        self.board_played = board_played
        self.moves = pickle.dumps(moves)



class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    unsheltered = db.Column(db.Integer, default=0)
    market = db.Column(db.Integer, default=0)
    rapid = db.Column(db.Integer, default=0)
    perm = db.Column(db.Integer, default=0)
    emerg_total = db.Column(db.Integer, default=0)
    trans_total = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "<Game %r Scoreboard>" % (self.game_id)
