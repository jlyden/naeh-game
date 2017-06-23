import random
import pickle
from datetime import datetime
from flask import redirect, url_for, flash
from app import db
from .utils import get_random_bead, find_room, use_room, move_beads
from .utils import add_record, message_for, BOARD_LIST

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
    outreach = db.Column(db.PickleType, default=OUTREACH_START)
    unsheltered = db.Column(db.PickleType, default=EMPTY_LIST)
    unsheltered_record = db.Column(db.PickleType, default=pickle.dumps([0]))
    market = db.Column(db.PickleType, default=EMPTY_LIST)
    market_record = db.Column(db.PickleType, default=pickle.dumps([0]))

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

    def verify_board_to_play(self, board):
        if self.round_count == 6:
            flash(u'Game over - no more plays.', 'warning')
            return redirect(url_for('status', game_id=self.id))
        elif BOARD_LIST[self.board_to_play] != board:
            flash(u'Time to play ' + BOARD_LIST[self.board_to_play] +
                  ' board.', 'warning')
            return redirect(url_for('status', game_id=self.id))
        else:
            return
    
    def load_intake(self, moves):
        self.available, self.intake = get_random_bead(50, self.available)
        db.session.commit()
        moves.append(message_for(50, "intake"))
        return moves

    def send_to_unsheltered(self, beads, from_board, moves):
        from_board, self.unsheltered = move_beads(beads, from_board, self.unsheltered)
        db.session.commit()
        moves.append(message_for(beads, "unsheltered"))
        return from_board, moves

    def send_to_market(self, beads, from_board, moves):
        from_board, self.market = move_beads(beads, from_board, self.market)
        db.session.commit()
        moves.append(message_for(beads, "market"))
        return from_board, moves
    
    def send_anywhere(self, extra, from_board, moves):
        order = random.sample(range(1,5), 4)
        print("order = " + str(order))
        while len(from_board) > 0 and len(order) > 0:
            value = order.pop(0)
            if value == 1:
                emergency = Emergency.query.filter_by(game_id=self.id).first()
                extra, from_board, moves = emergency.receive_beads(extra, from_board, moves)
                print("Anywhere: moved beads to Emergency")
            elif value == 2:
                rapid = Rapid.query.filter_by(game_id=self.id).first()
                extra, from_board, moves = rapid.receive_beads(extra, from_board, moves)
                print("Anywhere: moved beads to Rapid")
            elif value == 3:
                transitional = Transitional.query.filter_by(game_id=self.id).first()
                extra, from_board, moves = transitional.receive_beads(extra, from_board, moves)
                print("Anywhere: moved beads to Transitional")
            elif value == 4:
                permanent = Permanent.query.filter_by(game_id=self.id).first()
                extra, from_board, moves = permanent.receive_beads(extra, from_board, moves)
                print("Anywhere: moved beads to Permanent")
        if len(from_board) > 0:
            from_board, moves = self.send_to_unsheltered(len(from_board), from_board, moves)
            print("Anywhere: moved beads to Unsheltered")
        return from_board, moves 


    def update_records(self):
        # add_record() accepts and returns a pickle object
        emergency = Emergency.query.filter_by(game_id=self.id).first()
        emerg_board = pickle.loads(emergency.board)
        emergency.record = add_record(emergency.record, len(emerg_board))
        rapid = Rapid.query.filter_by(game_id=self.id).first()
        rapid_board = pickle.loads(rapid.board)
        rapid.record = add_record(rapid.record, len(rapid_board))
        trans = Transitional.query.filter_by(game_id=self.id).first()
        trans_board = pickle.loads(trans.board)
        trans.record = add_record(trans.record, len(trans_board))
        permanent = Permanent.query.filter_by(game_id=self.id).first()
        permanent_board = pickle.loads(permanent.board)
        permanent.record = add_record(permanent.record, len(permanent_board))
        unsheltered_board = pickle.loads(self.unsheltered)
        self.unsheltered_record = add_record(self.unsheltered_record, len(unsheltered_board))
        market_board = pickle.loads(self.market)
        self.market_record = add_record(self.market_record, len(market_board))
        db.session.commit()
        return

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
    record = db.Column(db.PickleType, default=pickle.dumps([20]))
    maximum = db.Column(db.Integer, default=25)

    def __repr__(self):
        board = pickle.loads(self.board)
        return "%r" % str(board)

    def receive_beads(self, beads, from_board, moves):
        room = find_room(self.maximum, self.board)
        if room is 0:
            extra = beads
        else:
            extra, from_board, to_board = use_room(room, beads, from_board, self.board)
        db.session.commit()
        moved = str(beads - extra)
        moves.append(message_for(moved, "emergency"))
        return extra, from_board, moves


class Rapid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    board = db.Column(db.PickleType, default=RAPID_START)
    record = db.Column(db.PickleType, default=pickle.dumps([10]))
    maximum = db.Column(db.Integer, default=10)

    def __repr__(self):
        board = pickle.loads(self.board)
        return "%r" % str(board)

    def receive_beads(self, beads, from_board, moves):
        room = find_room(self.maximum, self.board)
        if room is 0:
            extra = beads
        else:
            extra, from_board, to_board = use_room(room, beads, from_board, self.board)
        db.session.commit()
        moved = str(beads - extra)
        moves.append(message_for(moved, "rapid"))
        return extra, from_board, moves


class Transitional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    board = db.Column(db.PickleType, default=TRANSITIONAL_START)
    record = db.Column(db.PickleType, default=pickle.dumps([16]))
    maximum = db.Column(db.Integer, default=20)

    def __repr__(self):
        board = pickle.loads(self.board)
        return "%r" % str(board)

    def receive_beads(self, beads, from_board, moves):
        room = find_room(self.maximum, self.board)
        if room is 0:
            extra = beads
        else:
            extra, from_board, to_board = use_room(room, beads, from_board, self.board)
        db.session.commit()
        moved = str(beads - extra)
        moves.append(message_for(moved, "transitional"))
        return extra, from_board, moves


class Permanent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    board = db.Column(db.PickleType, default=PERMANENT_START)
    record = db.Column(db.PickleType, default=pickle.dumps([20]))
    maximum = db.Column(db.Integer, default=20)

    def __repr__(self):
        board = pickle.loads(self.board)
        return "%r" % str(board)

    def receive_beads(self, beads, from_board, moves):
        room = find_room(self.maximum, self.board)
        if room is 0:
            extra = beads
        else:
            extra, from_board, to_board = use_room(room, beads, from_board, self.board)
        db.session.commit()
        moved = str(beads - extra)
        moves.append(message_for(moved, "permanent"))
        return extra, from_board, moves


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    unsheltered = db.Column(db.Integer, default=0)
    market = db.Column(db.Integer, default=0)
    rapid = db.Column(db.Integer, default=0)
    permanent = db.Column(db.Integer, default=0)
    emergency_total = db.Column(db.Integer, default=0)
    transitional_total = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "<Game %r Scoreboard>" % (self.game_id)

    def calculate_final_score(self):
        this_game = Game.query.filter_by(id=self.game_id).first()
        this_unsheltered = pickle.loads(this_game.unsheltered)
        this_market = pickle.loads(this_game.market)
        this_emerg = Emergency.query.filter_by(game_id=self.game_id).first()
        this_emerg_record = pickle.loads(this_emerg.record)
        this_rapid = Rapid.query.filter_by(game_id=self.game_id).first()
        this_rapid_board = pickle.loads(this_rapid.board)
        this_trans = Rapid.query.filter_by(game_id=self.game_id).first()
        this_trans_record = pickle.loads(this_trans.record)
        this_permanent = Permanent.query.filter_by(game_id=self.game_id).first()
        this_permanent_board = pickle.loads(this_permanent.board)
        self.unsheltered = len(this_unsheltered)
        self.market = len(this_market)
        self.emergency_total = sum(this_emerg_record)
        self.rapid = len(this_rapid_board)
        self.transitional_total = sum(this_trans_record)
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
