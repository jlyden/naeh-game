import pickle
from app import db


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    round_count = db.Column(db.Integer)
    board_played = db.Column(db.Integer, default=0)
    moves = db.Column(db.PickleType)

    def __repr__(self):
        return "<Game %r Log>" % (self.game_id)

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
