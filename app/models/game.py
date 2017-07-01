import random
import pickle
from datetime import datetime
from flask import redirect, url_for, flash
from app import db
from .boards import Emergency, Rapid, Outreach, Transitional, Permanent
from .boards import Unsheltered, Market
from .score import Score, Log


# Beads 1-65 are red
# ALL_BEADS = list(range(1, 325))
EMERG_START = pickle.dumps(list(range(1, 7)) + list(range(66, 80)))
RAPID_START = pickle.dumps(list(range(7, 8)) + list(range(80, 89)))
OUTREACH_START = pickle.dumps(list(range(8, 10)) + list(range(89, 95)))
TRANS_START = pickle.dumps(list(range(10, 14)) + list(range(95, 107)))
PERM_START = pickle.dumps(list(range(14, 26)) + list(range(107, 115)))
AVAILABLE_BEADS = pickle.dumps(list(range(26, 66)) + list(range(115, 325)))
EMPTY_LIST = pickle.dumps(list())
EXTRA_BOARD = 25
BOARD_LIST = ["Intake", "Emergency", "Rapid",
              "Outreach", "Transitional", "Permanent"]


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, default=datetime.now)
    round_count = db.Column(db.Integer, default=1)
    board_to_play = db.Column(db.Integer, default=0)
    intake_cols = db.Column(db.Integer, default=5)

    available = db.Column(db.PickleType, default=AVAILABLE_BEADS)
    intake = db.Column(db.PickleType, default=EMPTY_LIST)

    # One to One relationships
    emergency = db.relationship('Emergency', uselist=False)
    rapid = db.relationship('Rapid', uselist=False)
    outreach = db.relationship('Outreach', uselist=False)
    transitional = db.relationship('Transitional', uselist=False)
    permanent = db.relationship('Permanent', uselist=False)
    unsheltered = db.relationship('Unsheltered', uselist=False)
    market = db.relationship('Market', uselist=False)
    score = db.relationship('Score', uselist=False)
    # One to Many relationship
    log = db.relationship('Log')

    def __repr__(self):
        return "<Game %r, round %r>" % (self.id, self.round_count)

    @classmethod
    def create(cls):
        # Instantiate game, to reference game.id
        new_game = cls()
        db.session.add(new_game)
        db.session.commit()
        # Instantiate other boards
        new_Emergency = Emergency(game_id=new_game.id,
                                  board=EMERG_START,
                                  record=pickle.dumps([20]),
                                  maximum=25)
        new_Rapid = Rapid(game_id=new_game.id,
                          board=RAPID_START,
                          record=pickle.dumps([10]),
                          maximum=10)
        new_Outreach = Outreach(game_id=new_game.id,
                                board=OUTREACH_START,
                                record=None,
                                maximum=10)
        new_Transitional = Transitional(game_id=new_game.id,
                                        board=TRANS_START,
                                        record=pickle.dumps([16]),
                                        maximum=20)
        new_Permanent = Permanent(game_id=new_game.id,
                                  board=PERM_START,
                                  record=pickle.dumps([20]),
                                  maximum=20)
        new_Unsheltered = Unsheltered(game_id=new_game.id,
                                      board=EMPTY_LIST,
                                      record=pickle.dumps([0]),
                                      maximum=None)
        new_Market = Market(game_id=new_game.id,
                            board=EMPTY_LIST,
                            record=pickle.dumps([0]),
                            maximum=None)
        # Instantiate first Log
        moves = []
        moves.append("Game " + str(new_game.id) + " initiated")
        move_log = Log(new_game.id, 1, 0, moves)
        db.session.add(new_Emergency)
        db.session.add(new_Rapid)
        db.session.add(new_Outreach)
        db.session.add(new_Transitional)
        db.session.add(new_Permanent)
        db.session.add(new_Unsheltered)
        db.session.add(new_Market)
        db.session.add(move_log)
        db.session.commit()
        return new_game

    def verify_board_to_play(self, board):
        if self.round_count > 5:
            flash(u'Game over - no more plays.', 'warning')
            return redirect(url_for('status', game_id=self.id))
        elif BOARD_LIST[self.board_to_play] != board:
            flash(u'Time to play ' + BOARD_LIST[self.board_to_play] +
                  ' board.', 'warning')
            return redirect(url_for('status', game_id=self.id))
        else:
            return

    def load_intake(self, moves):
        available_beads = pickle.loads(self.available)
        if len(available_beads) == 0:
            flash(u'Game over - no more plays.', 'warning')
            return redirect(url_for('status', game_id=self.id))
        else:
            available_beads, intake_board = get_random_bead(50,
                                                            available_beads)
            self.available = pickle.dumps(available_beads)
            self.intake = pickle.dumps(intake_board)
            db.session.commit()
            moves.append(message_for(50, "intake"))
            return moves

    def send_anywhere(self, extra, from_board, moves):
        order = random.sample(range(1, 5), 4)
        while len(from_board) > 0 and len(order) > 0:
            value = order.pop(0)
            if value == 1:
                emerg = Emergency.query.filter_by(game_id=self.id).first()
                extra, from_board, moves = emerg.receive_beads(extra,
                                                               from_board,
                                                               moves)
            elif value == 2:
                rapid = Rapid.query.filter_by(game_id=self.id).first()
                extra, from_board, moves = rapid.receive_beads(extra,
                                                               from_board,
                                                               moves)
            elif value == 3:
                trans = Transitional.query.filter_by(game_id=self.id).first()
                extra, from_board, moves = trans.receive_beads(extra,
                                                               from_board,
                                                               moves)
            elif value == 4:
                perm = Permanent.query.filter_by(game_id=self.id).first()
                extra, from_board, moves = perm.receive_beads(extra,
                                                              from_board,
                                                              moves)
        if len(from_board) > 0:
            from_board, moves = self.send_to_unsheltered(len(from_board),
                                                         from_board,
                                                         moves)
        return from_board, moves

    def update_records(self):
        # add_record() accepts and returns a pickle object
        emerg = Emergency.query.filter_by(game_id=self.id).first()
        emerg_board = pickle.loads(emerg.board)
        emerg.record = add_record(emerg.record, len(emerg_board))
        rapid = Rapid.query.filter_by(game_id=self.id).first()
        rapid_board = pickle.loads(rapid.board)
        rapid.record = add_record(rapid.record, len(rapid_board))
        trans = Transitional.query.filter_by(game_id=self.id).first()
        trans_board = pickle.loads(trans.board)
        trans.record = add_record(trans.record, len(trans_board))
        perm = Permanent.query.filter_by(game_id=self.id).first()
        perm_board = pickle.loads(perm.board)
        perm.record = add_record(perm.record, len(perm_board))
        unsheltered_board = pickle.loads(self.unsheltered)
        self.unsheltered_record = add_record(self.unsheltered_record,
                                             len(unsheltered_board))
        market_board = pickle.loads(self.market)
        self.market_record = add_record(self.market_record, len(market_board))
        db.session.commit()
        return

    def open_new(self, program, moves):
        print('program is ' + program)
        # Add 'extra' board (i.e. 25 slots to selected board/program)
        if program == 'emergency':
            emerg = Emergency.query.filter_by(game_id=self.id).first()
            emerg.maximum = EXTRA_BOARD + emerg.maximum
            print("emerg_max is now " + str(emerg.maximum))
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
            perm = Permanent.query.filter_by(game_id=self.id).first()
            perm.maximum = EXTRA_BOARD + perm.maximum
            print("perm_max is now " + str(perm.maximum))
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

    def calculate_final_score(self):
        # Gather all the values
        this_unsheltered = pickle.loads(self.unsheltered)
        this_market = pickle.loads(self.market)
        this_emerg = Emergency.query.filter_by(game_id=self.game_id).first()
        this_emerg_record = pickle.loads(this_emerg.record)
        this_rapid = Rapid.query.filter_by(game_id=self.game_id).first()
        this_rapid_board = pickle.loads(this_rapid.board)
        this_trans = Transitional.query.filter_by(game_id=self.game_id).first()
        this_trans_record = pickle.loads(this_trans.record)
        this_perm = Permanent.query.filter_by(game_id=self.game_id).first()
        this_perm_board = pickle.loads(this_perm.board)

        # Create, fill and return the scoreboard
        new_Score = Score(game_id=self.id)
        new_Score.unsheltered = len(this_unsheltered)
        new_Score.market = len(this_market)
        new_Score.emerg_total = sum(this_emerg_record)
        new_Score.rapid = len(this_rapid_board)
        new_Score.trans_total = sum(this_trans_record)
        new_Score.perm = len(this_perm_board)
        db.session.add(new_Score)
        db.session.commit()
        return


# Helper methods
def get_random_bead(number, available_beads):
    collection = []
    for i in range(number):
        selection = random.choice(available_beads)
        collection.append(selection)
        available_beads.remove(selection)
    return available_beads, collection


def add_record(record_pickle, value):
    record = pickle.loads(record_pickle)
    record.append(value)
    record_pickle = pickle.dumps(record)
    return record_pickle


def message_for(beads_moved, board):
    if beads_moved == "0":
        message = "No room in " + board
    else:
        message = str(beads_moved) + " beads to " + board
    return message
