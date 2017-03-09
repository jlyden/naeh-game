from app import db


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(40))
    start_datetime = db.Column(db.DateTime)
    round_count = db.Column(db.Integer, default=0)
    round_over = db.Column(db.Boolean, default=True)
    diversion = db.Column(db.Boolean, default=False)

    available = db.Column(db.Array(db.Integer))
    market = db.Column(db.Array(db.Integer))
    unsheltered = db.Column(db.Array(db.Integer))
    intake = db.Column(db.Array(db.Integer))
    emergency = db.Column(db.Array(db.Integer))
    rapid = db.Column(db.Array(db.Integer))
    outreach = db.Column(db.Array(db.Integer))
    transitional = db.Column(db.Array(db.Integer))
    permanent = db.Column(db.Array(db.Integer))

    score = db.relationship('Score')

    def __repr__(self):
        return "<%r's Game>" % (self.team_name)


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    # Integer is added to these arrays at end of each round
    emergency_count = db.Column(db.Array(db.Integer))
    transitional_count = db.Column(db.Array(db.Integer))
