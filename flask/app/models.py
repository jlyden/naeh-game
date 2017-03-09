from app import db


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(40))
    start_datetime = db.Column(db.DateTime)
    round_count = db.Column(db.Integer, default=0)
    round_over = db.Column(db.Boolean, default=True)
    diversion = db.Column(db.Boolean, default=False)

    score = db.relationship('Score')
    available = db.relationship('Available')
    market = db.relationship('Market')
    unsheltered = db.relationship('Unsheltered')
    intake = db.relationship('Intake')
    emergency = db.relationship('Emergency')
    rapid = db.relationship('Rapid')
    outreach = db.relationship('Outreach')
    transitional = db.relationship('Transitional')
    permanent = db.relationship('Permanent')

    def __repr__(self):
        return "<%r's Game>" % (self.team_name)


class Available(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    beads = db.Column(db.Array(db.Integer))


class Market(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    beads = db.Column(db.Array(db.Integer))


class Unsheltered(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    beads = db.Column(db.Array(db.Integer))


class Intake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    beads = db.Column(db.Array(db.Integer))


class Emergency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    beads = db.Column(db.Array(db.Integer))


class Rapid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    beads = db.Column(db.Array(db.Integer))


class Outreach(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    beads = db.Column(db.Array(db.Integer))


class Transitional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    beads = db.Column(db.Array(db.Integer))


class Permanent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    beads = db.Column(db.Array(db.Integer))


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    # Integer is added to these arrays at end of each round
    emergency_count = db.Column(db.Array(db.Integer))
    transitional_count = db.Column(db.Array(db.Integer))
