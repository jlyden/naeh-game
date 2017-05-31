import pickle
from datetime import datetime
from app import db
from .utils import get_random_bead, find_room, use_room, move_beads

# Beads 1-65 are red
# ALL_BEADS = list(range(1, 325))
EMERGENCY_START = pickle.dumps(list(range(1, 7)) + list(range(66, 80)))
OUTREACH_START = pickle.dumps(list(range(8, 10)) + list(range(89, 95)))
RAPID_START = pickle.dumps(list(range(7, 8)) + list(range(80, 89)))
TRANSITIONAL_START = pickle.dumps(list(range(10, 14)) + list(range(95, 107)))
PERMANENT_START = pickle.dumps(list(range(14, 26)) + list(range(107, 115)))
AVAILABLE_BEADS = pickle.dumps(list(range(26, 66)) + list(range(115, 325)))
EMPTY_LIST = pickle.dumps(list())


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, default=datetime.now)
    round_count = db.Column(db.Integer, default=0)
    round_over = db.Column(db.Boolean, default=True)
    diversion = db.Column(db.Boolean, default=False)

    available = db.Column(db.PickleType, default=AVAILABLE_BEADS)
    intake = db.Column(db.PickleType, default=EMPTY_LIST)
    unsheltered = db.Column(db.PickleType, default=EMPTY_LIST)
    outreach = db.Column(db.PickleType, default=OUTREACH_START)
    market = db.Column(db.PickleType, default=EMPTY_LIST)

    emergency = db.relationship('Emergency')
    rapid = db.relationship('Rapid')
    transitional = db.relationship('Transitional')
    permanent = db.relationship('Permanent')
    score = db.relationship('Score')

    def __repr__(self):
        return "<Game %r, round %r>" % (self.id, self.round_count)

    def load_intake(self):
        # This move begins round, so up-counter and toggle flag
        self.round_count += 1
        self.round_over = False
        print("Loading intake board for round " + str(self.round_count))
        available_list = pickle.loads(self.available)
        available_list, intake_list = get_random_bead(50, available_list)
        self.intake = pickle.dumps(intake_list)
        self.available = pickle.dumps(available_list)
        db.session.commit()
        return

    def send_to_unsheltered(self, beads, from_board):
        to_board = pickle.loads(self.unsheltered)
        from_board, to_board = move_beads(beads, from_board, to_board)
        self.unsheltered = pickle.dumps(to_board)
        db.session.commit()
        print("after Unsheltered, intake has " + str(len(from_board)) + " beads")
        return from_board

    def send_to_market(self, beads, from_board):
        to_board = pickle.loads(self.market)
        from_board, to_board = move_beads(10, from_board, to_board)
        self.market = pickle.dumps(to_board)
        db.session.commit()
        return from_board


class Emergency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    board = db.Column(db.PickleType, default=EMERGENCY_START)
    maximum = db.Column(db.Integer, default=25)

    def __repr__(self):
        board = pickle.loads(self.board)
        return "%r" % str(board)

    def receive_beads(self, beads, from_board):
        to_board = pickle.loads(self.board)
        room = find_room(to_board, self.maximum)
        if room is 0:
            extra = beads
        else:
            extra, from_board, to_board = use_room(room, beads, from_board,
                                                   to_board)
        count = len(to_board)
        self.board = pickle.dumps(to_board)
        db.session.commit()
        print("after Emergency, intake has " + str(len(from_board)) + " beads")
        return extra, from_board, count


class Rapid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    board = db.Column(db.PickleType, default=RAPID_START)
    maximum = db.Column(db.Integer, default=10)

    def __repr__(self):
        board = pickle.loads(self.board)
        return "%r" % str(board)

    def receive_beads(self, beads, from_board):
        to_board = pickle.loads(self.board)
        room = find_room(to_board, self.maximum)
        if room is 0:
            extra = beads
        else:
            extra, from_board, to_board = use_room(room, beads, from_board,
                                                   to_board)
        self.board = pickle.dumps(to_board)
        db.session.commit()
        print("after Rapid, from_board has " + str(len(from_board)) + " beads")
        return extra, from_board


class Transitional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    board = db.Column(db.PickleType, default=TRANSITIONAL_START)
    maximum = db.Column(db.Integer, default=20)

    def __repr__(self):
        board = pickle.loads(self.board)
        return "%r" % str(board)

    def receive_beads(self, beads, from_board):
        to_board = pickle.loads(self.board)
        room = find_room(to_board, self.maximum)
        if room is 0:
            extra = beads
        else:
            extra, from_board, to_board = use_room(room, beads, from_board,
                                                   to_board)
        count = len(to_board)
        self.board = pickle.dumps(to_board)
        db.session.commit()
        print("after Transitional, intake has " + str(len(from_board)) + " beads")
        return extra, from_board, count


class Permanent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    board = db.Column(db.PickleType, default=PERMANENT_START)
    maximum = db.Column(db.Integer, default=20)

    def __repr__(self):
        board = pickle.loads(self.board)
        return "%r" % str(board)

    def receive_beads(self, beads, from_board):
        to_board = pickle.loads(self.board)
        room = find_room(to_board, self.maximum)
        if room is 0:
            extra = beads
        else:
            extra, from_board, to_board = use_room(room, beads, from_board,
                                                   to_board)
        self.board = pickle.dumps(to_board)
        db.session.commit()
        print("after Permanent, intake has " + str(len(from_board)) + " beads")
        return extra, from_board


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

    # An integer is added to these arrays at end of each round
    emergency_count = db.Column(db.PickleType, default=EMPTY_LIST)
    transitional_count = db.Column(db.PickleType, default=EMPTY_LIST)

    # These values are entered after the game ends
    unsheltered = db.Column(db.Integer, default=0)
    market = db.Column(db.Integer, default=0)
    rapid = db.Column(db.Integer, default=0)
    permanent = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "<Game %r Scoreboard>" % (self.game_id)

    def add_score(self, emergency, transitional):
        this_emergency_count = pickle.loads(self.emergency_count)
        this_emergency_count.append(emergency)
        this_transitional_count = pickle.loads(self.transitional_count)
        this_transitional_count.append(transitional)
        self.emergency_count = pickle.dumps(this_emergency_count)
        self.transitional_count = pickle.dumps(this_transitional_count)
        db.session.commit()
        return
