from datetime import datetime
from app import db


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(40))
    start_datetime = db.Column(db.DateTime, default=datetime.now)
    round_count = db.Column(db.Integer, default=0)
    round_over = db.Column(db.Boolean, default=True)
    diversion = db.Column(db.Boolean, default=False)

    available = db.Column(db.ARRAY(db.Integer))
    market = db.Column(db.ARRAY(db.Integer))
    unsheltered = db.Column(db.ARRAY(db.Integer))
    intake = db.Column(db.ARRAY(db.Integer))
    emergency = db.Column(db.ARRAY(db.Integer))
    rapid = db.Column(db.ARRAY(db.Integer))
    outreach = db.Column(db.ARRAY(db.Integer))
    transitional = db.Column(db.ARRAY(db.Integer))
    permanent = db.Column(db.ARRAY(db.Integer))

    score = db.relationship('Score')

    def __repr__(self):
        return "<%r's Game>" % (self.team_name)


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    # Integer is added to these arrays at end of each round
    emergency_count = db.Column(db.ARRAY(db.Integer))
    transitional_count = db.Column(db.ARRAY(db.Integer))
