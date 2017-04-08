from datetime import datetime
from app import db
from .utils import get_random_bead, single_board_transfer, move_beads

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
    outreach        = db.Column(db.ARRAY(db.Integer), default=OUTREACH_START)

    emergency       = db.relationship('Emergency')
    rapid           = db.relationship('Rapid')
    transitional    = db.relationship('Transitional')
    permanent       = db.relationship('Permanent')
    score           = db.relationship('Score')

    def __repr__(self):
        return "<Game %r, round %r>" % (self.id, self.round_count)

    def load_intake(self):
        self.available, self.intake = get_random_bead(50, self.available)

        # This move begins round, so up-counter and toggle flag
        self.round_count += 1
        self.round_over = False
        db.session.commit()
        return


class Emergency(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    game_id         = db.Column(db.Integer, db.ForeignKey('game.id'))
    board           = db.Column(db.ARRAY(db.Integer), default=EMERGENCY_START)
    maximum         = db.Column(db.Integer, default=25)
    room            = db.Column(db.Integer, default=5)

    def __repr__(self):
        return "room = %r || %r" % (str(self.room), str(self.board))


class Rapid(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    game_id         = db.Column(db.Integer, db.ForeignKey('game.id'))
    board           = db.Column(db.ARRAY(db.Integer), default=RAPID_START)
    maximum         = db.Column(db.Integer, default=10)
    room            = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "room = %r || %r" % (str(self.room), str(self.board))


class Transitional(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    game_id         = db.Column(db.Integer, db.ForeignKey('game.id'))
    board           = db.Column(db.ARRAY(db.Integer), default=TRANSITIONAL_START)
    maximum         = db.Column(db.Integer, default=20)
    room            = db.Column(db.Integer, default=4)

    def __repr__(self):
        return "room = %r || %r" % (str(self.room), str(self.board))


class Permanent(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    game_id         = db.Column(db.Integer, db.ForeignKey('game.id'))
    board           = db.Column(db.ARRAY(db.Integer), default=PERMANENT_START)
    maximum         = db.Column(db.Integer, default=20)
    room            = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "room = %r || %r" % (str(self.room), str(self.board))


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

    def __repr__(self):
        return "<Game %r Scoreboard>" % (self.game_id)
