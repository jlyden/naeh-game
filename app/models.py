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
EXTRA_BOARD = 25


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, default=datetime.now)
    round_count = db.Column(db.Integer, default=1)
    board_to_play = db.Column(db.Integer, default=0)
    intake_cols = db.Column(db.Integer, default=5)
    outreach_max = db.Column(db.Integer, default=10)

    available = db.Column(db.PickleType, default=AVAILABLE_BEADS)
    intake = db.Column(db.PickleType, default=EMPTY_LIST)
    unsheltered = db.Column(db.PickleType, default=EMPTY_LIST)
    outreach = db.Column(db.PickleType, default=OUTREACH_START)
    market = db.Column(db.PickleType, default=EMPTY_LIST)

    # One to One relationships
    emergency = db.relationship('Emergency', uselist=False)
    rapid = db.relationship('Rapid', uselist=False)
    transitional = db.relationship('Transitional', uselist=False)
    permanent = db.relationship('Permanent', uselist=False)
    score = db.relationship('Score', uselist=False)
    # One to Many relationship
    log = db.relationship('Log')

    def __repr__(self):
        return "<Game %r, round %r>" % (self.id, self.round_count)

    def load_intake(self, moves):
        available_list = pickle.loads(self.available)
        available_list, intake_list = get_random_bead(50, available_list)
        self.intake = pickle.dumps(intake_list)
        self.available = pickle.dumps(available_list)
        db.session.commit()
        message = "50 beads to intake"
        moves.append(message)
        return moves

    def send_to_unsheltered(self, beads, from_board, moves):
        to_board = pickle.loads(self.unsheltered)
        from_board, to_board = move_beads(beads, from_board, to_board)
        self.unsheltered = pickle.dumps(to_board)
        db.session.commit()
        message = str(beads) + " beads to unsheltered"
        moves.append(message)
        return from_board, moves

    def send_to_market(self, beads, from_board, moves):
        to_board = pickle.loads(self.market)
        from_board, to_board = move_beads(beads, from_board, to_board)
        self.market = pickle.dumps(to_board)
        db.session.commit()
        message = str(beads) + " beads to market"
        moves.append(message)
        return from_board, moves

    def open_new(self, program, moves):
        print('program is ' + program)
        # Add 'extra' board (i.e. 25 slots to selected board/program)
        if program == 'emergency':
            emergency = Emergency.query.filter_by(game_id=self.id).first()
            emergency.maximum = EXTRA_BOARD + emergency.maximum
            print("emergency_max is now " + str(emergency.maximum))
        elif program == 'rapid':
            rapid = Rapid.query.filter_by(game_id=self.id).first()
            rapid.maximum = EXTRA_BOARD + rapid.maximum
            print("rapid_max is now " + str(rapid.maximum))
        elif program == 'outreach':
            self.outreach_max = EXTRA_BOARD + self.outreach_max
            print("outreach_max is now " + str(self.outreach_max))
        elif program == 'transitional':
            trans = Transitional.query.filter_by(game_id=self.id).first()
            trans.maximum = EXTRA_BOARD + trans.maximum
            print("trans_max is now " + str(trans.maximum))
        elif program == 'permanent':
            permanent = Permanent.query.filter_by(game_id=self.id).first()
            permanent.maximum = EXTRA_BOARD + permanent.maximum
            print("permanent_max is now " + str(permanent.maximum))
        # Add 'diversion' column to intake board
        elif program == 'diversion':
            self.intake_cols = 6
            print("intake_cols is now " + str(self.intake_cols))
        db.session.commit()
        message = "New " + program + " program added"
        moves.append(message)
        return moves

    def convert_program(self, from_program, to_program, moves):
        # Get beads from from_program.board
        # Store value of from_program.max
        # Set from_program.max to 0
        # Add from_program.max to to_program.max
        # Put beads in to_program.board
        return moves


class Emergency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    board = db.Column(db.PickleType, default=EMERGENCY_START)
    maximum = db.Column(db.Integer, default=25)

    def __repr__(self):
        board = pickle.loads(self.board)
        return "%r" % str(board)

    def receive_beads(self, beads, from_board, moves):
        to_board = pickle.loads(self.board)
        room = find_room(self.maximum, to_board)
        if room is 0:
            extra = beads
        else:
            extra, from_board, to_board = use_room(room, beads, from_board,
                                                   to_board)
        self.board = pickle.dumps(to_board)
        db.session.commit()
        message = str(beads - extra) + " beads to emergency"
        moves.append(message)
        return extra, from_board, moves


class Rapid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    board = db.Column(db.PickleType, default=RAPID_START)
    maximum = db.Column(db.Integer, default=10)

    def __repr__(self):
        board = pickle.loads(self.board)
        return "%r" % str(board)

    def receive_beads(self, beads, from_board, moves):
        to_board = pickle.loads(self.board)
        room = find_room(self.maximum, to_board)
        if room is 0:
            extra = beads
        else:
            extra, from_board, to_board = use_room(room, beads, from_board,
                                                   to_board)
        self.board = pickle.dumps(to_board)
        db.session.commit()
        message = str(beads - extra) + " beads to rapid"
        moves.append(message)
        return extra, from_board, moves


class Transitional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    board = db.Column(db.PickleType, default=TRANSITIONAL_START)
    maximum = db.Column(db.Integer, default=20)

    def __repr__(self):
        board = pickle.loads(self.board)
        return "%r" % str(board)

    def receive_beads(self, beads, from_board, moves):
        to_board = pickle.loads(self.board)
        room = find_room(self.maximum, to_board)
        if room is 0:
            extra = beads
        else:
            extra, from_board, to_board = use_room(room, beads, from_board,
                                                   to_board)
        self.board = pickle.dumps(to_board)
        db.session.commit()
        message = str(beads - extra) + " beads to transitional"
        moves.append(message)
        return extra, from_board, moves


class Permanent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    board = db.Column(db.PickleType, default=PERMANENT_START)
    maximum = db.Column(db.Integer, default=20)

    def __repr__(self):
        board = pickle.loads(self.board)
        return "%r" % str(board)

    def receive_beads(self, beads, from_board, moves):
        to_board = pickle.loads(self.board)
        room = find_room(self.maximum, to_board)
        if room is 0:
            extra = beads
        else:
            extra, from_board, to_board = use_room(room, beads, from_board,
                                                   to_board)
        self.board = pickle.dumps(to_board)
        db.session.commit()
        message = str(beads - extra) + " beads to permanent"
        moves.append(message)
        return extra, from_board, moves


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
    emergency_total = db.Column(db.Integer, default=0)
    transitional_total = db.Column(db.Integer, default=0)

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

    def calculate_final_score(self):
        this_game = Game.query.filter_by(id=self.game_id).first()
        this_emergency_count = pickle.loads(self.emergency_count)
        this_transitional_count = pickle.loads(self.transitional_count)
        this_unsheltered = pickle.loads(this_game.unsheltered)
        this_market = pickle.loads(this_game.market)
        this_rapid = Rapid.query.filter_by(game_id=self.game_id).first()
        this_rapid_board = pickle.loads(this_rapid.board)
        this_permanent = Permanent.query.filter_by(game_id=self.game_id).first()
        this_permanent_board = pickle.loads(this_permanent.board)
        self.emergency_total = sum(this_emergency_count)
        self.transitional_total = sum(this_transitional_count)
        self.unsheltered = len(this_unsheltered)
        self.market = len(this_market)
        self.rapid = len(this_rapid_board)
        self.permanent = len(this_permanent_board)
        db.session.commit()


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
