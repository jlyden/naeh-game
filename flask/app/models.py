from datetime import datetime
from app import db

# Beads 1-65 are red
# ALL_BEADS = list(range(1, 325))
EMERGENCY_START = list(range(1, 7)) + list(range(66, 80))
RAPID_START = list(range(7, 8)) + list(range(80, 89))
OUTREACH_START = list(range(8, 10)) + list(range(89, 95))
TRANSITIONAL_START = list(range(10, 14)) + list(range(95, 107))
PERMANENT_START = list(range(14, 26)) + list(range(107, 115))
AVAILABLE_BEADS = list(range(26, 66)) + list(range(115, 325))


class Game(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    start_datetime  = db.Column(db.DateTime, default=datetime.now)
    round_count     = db.Column(db.Integer, default=0)
    round_over      = db.Column(db.Boolean, default=True)
    diversion       = db.Column(db.Boolean, default=False)

    available       = db.Column(db.ARRAY(db.Integer), default=AVAILABLE_BEADS)
    market          = db.Column(db.ARRAY(db.Integer), default=[])
    unsheltered     = db.Column(db.ARRAY(db.Integer), default=[])
    intake          = db.Column(db.ARRAY(db.Integer), default=[])
    emergency       = db.Column(db.ARRAY(db.Integer), default=EMERGENCY_START)
    rapid           = db.Column(db.ARRAY(db.Integer), default=RAPID_START)
    outreach        = db.Column(db.ARRAY(db.Integer), default=OUTREACH_START)
    transitional    = db.Column(db.ARRAY(db.Integer), default=TRANSITIONAL_START)
    permanent       = db.Column(db.ARRAY(db.Integer), default=PERMANENT_START)

    score           = db.relationship('Score')

    def __repr__(self):
        return "<%r's Game>" % (self.team_name)


class Score(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    game_id         = db.Column(db.Integer, db.ForeignKey('game.id'))

    # An integer is added to these arrays at end of each round
    emergency_count    = db.Column(db.ARRAY(db.Integer), default=[])
    transitional_count = db.Column(db.ARRAY(db.Integer), default=[])

    # These values are entered after the game ends
    unsheltered     = db.Column(db.Integer, default=0)
    market          = db.Column(db.Integer, default=0)
    rapid           = db.Column(db.Integer, default=0)
    permanent       = db.Column(db.Integer, default=0)
