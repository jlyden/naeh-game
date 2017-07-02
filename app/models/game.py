import pickle
import random
from datetime import datetime
from flask import redirect, url_for, flash
from app import db
from .boards import Emergency, Rapid, Outreach, Transitional, Permanent
from .boards import Unsheltered, Market, move_beads
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
ANYWHERE_LIST = ["Emergency", "Rapid", "Transitional", "Permanent"]


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, default=datetime.now)
    round_count = db.Column(db.Integer, default=1)
    board_to_play = db.Column(db.Integer, default=0)

    available = db.Column(db.PickleType, default=AVAILABLE_BEADS)
    intake_cols = db.Column(db.Integer, default=5)

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
            db.session.commit()
            moves.append("50 beads to intake")
            return intake_board, moves

    def send_anywhere(self, extra, from_board, moves):
        order = random.sample(range(0, 4), 4)
        while len(from_board) > 0 and len(order) > 0:
            this_prog = ANYWHERE_LIST[order.pop(0)]
            this_table = eval(this_prog)
            this_board = this_table.query.filter_by(game_id=self.id).first()
            extra, from_board, moves = this_board.receive_beads(extra,
                                                                from_board,
                                                                moves)
        if len(from_board) > 0:
            unsheltered = Unsheltered.query.filter_by(game_id=self.id).first()
            from_board, moves = unsheltered.receive_unlimited(len(from_board),
                                                              from_board,
                                                              moves)
        return from_board, moves

    def update_records(self):
        this_emerg = Emergency.query.filter_by(game_id=self.id).first()
        this_emerg.update_record()
        this_rapid = Rapid.query.filter_by(game_id=self.id).first()
        this_rapid.update_record()
        this_trans = Transitional.query.filter_by(game_id=self.id).first()
        this_trans.update_record()
        this_perm = Permanent.query.filter_by(game_id=self.id).first()
        this_perm.update_record()
        this_unsheltered = Unsheltered.query.filter_by(game_id=self.id).first()
        this_unsheltered.update_record()
        this_market = Market.query.filter_by(game_id=self.id).first()
        this_market.update_record()
        return

    def open_new(self, program, moves):
        # Add 'diversion' column to intake board
        if program == 'Diversion':
            self.intake_cols = 6
            print("intake_cols is now " + str(self.intake_cols))
        # Add 'extra' board (i.e. 25 slots to selected board/program)
        else:
            table = eval(program)
            this_prog = table.query.filter_by(game_id=self.id).first()
            this_prog.maximum = EXTRA_BOARD + this_prog.maximum
            print(this_prog.__tablename__ + " max is now " +
                  str(this_prog.maximum))
        db.session.commit()
        message = "New " + program + " program added"
        moves.append(message)
        return moves

    def convert_program(self, from_program, to_program, moves):
        # Get both database objects and unpickle boards
        from_prog_table = eval(from_program)
        this_from_prog = from_prog_table.query.filter_by(game_id=self.id).first()
        from_prog_board = pickle.loads(this_from_prog.board)
        to_prog_table = eval(to_program)
        this_to_prog = to_prog_table.query.filter_by(game_id=self.id).first()
        to_prog_board = pickle.loads(this_to_prog.board)
        # Move beads from from_prog.board to to_prog.board
        print("from_board was " + str(from_prog_board))
        from_prog_board, to_prog_board = move_beads(len(from_prog_board),
                                                    from_prog_board,
                                                    to_prog_board)
        this_from_prog.board = pickle.dumps(from_prog_board)
        this_to_prog.board = pickle.dumps(to_prog_board)
        print("after move, from_board is " + str(from_prog_board))
        print("after move, to_board is " + str(to_prog_board))
        # Add from_program.max to to_program.max
        print("from_board_max started at " + str(this_from_prog.maximum))
        this_to_prog.maximum = this_from_prog.maximum + this_to_prog.maximum
        # Set from_program.max to 0
        this_from_prog.maximum = 0
        db.session.commit()
        message = this_from_prog.__tablename__ + " converted to " + this_to_prog.__tablename__
        moves.append(message)
        print(message)
        print("from_board_max is now " + str(this_from_prog.maximum))
        print("to_board_max is now " + str(this_to_prog.maximum))
        return moves

    def calculate_final_score(self):
        # Gather all the values
        this_emerg = Emergency.query.filter_by(game_id=self.id).first()
        this_emerg_record = pickle.loads(this_emerg.record)
        this_rapid = Rapid.query.filter_by(game_id=self.id).first()
        this_rapid_board = pickle.loads(this_rapid.board)
        this_trans = Transitional.query.filter_by(game_id=self.id).first()
        this_trans_record = pickle.loads(this_trans.record)
        this_perm = Permanent.query.filter_by(game_id=self.id).first()
        this_perm_board = pickle.loads(this_perm.board)
        this_unsheltered = Unsheltered.query.filter_by(game_id=self.id).first()
        this_unsheltered_board = pickle.loads(this_unsheltered.board)
        this_market = Market.query.filter_by(game_id=self.id).first()
        this_market_board = pickle.loads(this_market.board)

        # Create, fill and return the scoreboard
        new_Score = Score(game_id=self.id)
        new_Score.emerg_total = sum(this_emerg_record)
        new_Score.rapid = len(this_rapid_board)
        new_Score.trans_total = sum(this_trans_record)
        new_Score.perm = len(this_perm_board)
        new_Score.unsheltered = len(this_unsheltered_board)
        new_Score.market = len(this_market_board)
        db.session.add(new_Score)
        db.session.commit()
        return new_Score


# Helper methods
def get_random_bead(number, available_beads):
    collection = []
    for i in range(number):
        selection = random.choice(available_beads)
        collection.append(selection)
        available_beads.remove(selection)
    return available_beads, collection
