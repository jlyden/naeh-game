import pickle
import random
from datetime import datetime
from flask import redirect, url_for, flash
from app import db
from .boards import Emergency, Rapid, Outreach, Transitional, Permanent
from .boards import Unsheltered, Market, move_beads
from .score import Score, Record, Log


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
BOARD_LIST = pickle.dumps(["Intake", "Emergency", "Rapid",
                           "Outreach", "Transitional", "Permanent"])


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, default=datetime.now)
    round_count = db.Column(db.Integer, default=1)
    board_to_play = db.Column(db.Integer, default=0)
    intake_cols = db.Column(db.Integer, default=5)
    available_pickle = db.Column(db.PickleType, default=AVAILABLE_BEADS)
    board_list_pickle = db.Column(db.PickleType, default=BOARD_LIST)
    # One to One relationships
    emergency = db.relationship('Emergency', uselist=False)
    rapid = db.relationship('Rapid', uselist=False)
    outreach = db.relationship('Outreach', uselist=False)
    transitional = db.relationship('Transitional', uselist=False)
    permanent = db.relationship('Permanent', uselist=False)
    unsheltered = db.relationship('Unsheltered', uselist=False)
    market = db.relationship('Market', uselist=False)
    score = db.relationship('Score', uselist=False)
    # One to Many relationships
    record = db.relationship('Record')
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
                                  maximum=25)
        new_Rapid = Rapid(game_id=new_game.id,
                          board=RAPID_START,
                          maximum=10)
        new_Outreach = Outreach(game_id=new_game.id,
                                board=OUTREACH_START,
                                maximum=10)
        new_Transitional = Transitional(game_id=new_game.id,
                                        board=TRANS_START,
                                        maximum=20)
        new_Permanent = Permanent(game_id=new_game.id,
                                  board=PERM_START,
                                  maximum=20)
        new_Unsheltered = Unsheltered(game_id=new_game.id,
                                      board=EMPTY_LIST,
                                      maximum=None)
        new_Market = Market(game_id=new_game.id,
                            board=EMPTY_LIST,
                            maximum=None)
        # Instantiate Records - end_count = beads counts before first play
        E_record = Record(game_id=new_game.id,
                          round_count=0,
                          board_name="Emergency")
        E_record.end_count = 20
        R_record = Record(game_id=new_game.id,
                          round_count=0,
                          board_name="Rapid")
        R_record.end_count = 10
        O_record = Record(game_id=new_game.id,
                          round_count=0,
                          board_name="Outreach")
        O_record.end_count = 8
        T_record = Record(game_id=new_game.id,
                          round_count=0,
                          board_name="Transitional")
        T_record.end_count = 16
        P_record = Record(game_id=new_game.id,
                          round_count=0,
                          board_name="Permanent")
        P_record.end_count = 20
        U_record = Record(game_id=new_game.id,
                          round_count=0,
                          board_name="Unsheltered")
        M_record = Record(game_id=new_game.id,
                          round_count=0,
                          board_name="Market")
        # Instantiate first Log
        moves = []
        moves.append("Game " + str(new_game.id) + " started")
        move_log = Log(new_game.id, 1, 0, moves)

        db.session.add_all([new_Emergency, new_Rapid, new_Outreach,
                            new_Transitional, new_Permanent, new_Unsheltered,
                            new_Market, E_record, R_record, O_record, T_record,
                            P_record, U_record, M_record, move_log])
        db.session.commit()
        return new_game

    def verify_board_to_play(self, board_name):
        board_list = pickle.loads(self.board_list_pickle)
        if self.round_count > 5:
            flash(u'Game over - no more plays.', 'warning')
            return redirect(url_for('status', game_id=self.id))
        elif board_list[self.board_to_play] != board_name:
            flash(u'Time for ' + board_list[self.board_to_play] + ' board.',
                  'warning')
            return redirect(url_for('status', game_id=self.id))
        else:
            return

    def load_intake(self, moves):
        available_beads = pickle.loads(self.available_pickle)
        if len(available_beads) == 0:
            flash(u'Game over - no more plays.', 'warning')
            return redirect(url_for('status', game_id=self.id))
        else:
            available_beads, intake = get_random_bead(50, available_beads)
            self.available_pickle = pickle.dumps(available_beads)
            db.session.commit()
            moves.append("50 beads to intake")
            return intake, moves

    def send_anywhere(self, extra, from_board, moves):
        # Get list of available programs to send beads
        anywhere_list = generate_anywhere_list(self.board_list_pickle)
        print("Anywhere_list is " + str(anywhere_list))
        # Cycle through programs, moving as many beads as possible to each
        while len(from_board) > 0 and len(anywhere_list) > 0:
            prog_table = eval(anywhere_list.pop())
            prog = prog_table.query.filter_by(game_id=self.id).first()
            extra, from_board, moves = prog.receive_beads(extra,
                                                          from_board,
                                                          moves)
        # Whatever remains is sent to unsheltered
        if len(from_board) > 0:
            unsheltered = Unsheltered.query.filter_by(game_id=self.id).first()
            from_board, moves = unsheltered.receive_unlimited(len(from_board),
                                                              from_board,
                                                              moves)
        return from_board, moves

    def open_new(self, program, moves):
        # Add 'diversion' column to intake board
        if program == 'Diversion':
            self.intake_cols = 6
            print("Intake_cols is now " + str(self.intake_cols))
        # Add 'extra' board (i.e. 25 slots to selected board/program)
        else:
            prog_table = eval(program)
            prog = prog_table.query.filter_by(game_id=self.id).first()
            prog.maximum = EXTRA_BOARD + prog.maximum
            print(prog.__tablename__.title() + " max is now " +
                  str(prog.maximum))
        db.session.commit()
        message = "New " + program + " program added"
        moves.append(message)
        return moves

    def convert_program(self, from_program, to_program, moves):
        # Get both database objects and unpickle boards
        from_prog_table = eval(from_program)
        from_prog = from_prog_table.query.filter_by(game_id=self.id).first()
        from_prog_board = pickle.loads(from_prog.board)
        to_prog_table = eval(to_program)
        to_prog = to_prog_table.query.filter_by(game_id=self.id).first()
        to_prog_board = pickle.loads(to_prog.board)
        # Move beads from from_prog.board to to_prog.board
        from_prog_board, to_prog_board = move_beads(len(from_prog_board),
                                                    from_prog_board,
                                                    to_prog_board)
        from_prog.board = pickle.dumps(from_prog_board)
        to_prog.board = pickle.dumps(to_prog_board)
        # Add from_program.max to to_program.max
        to_prog.maximum = from_prog.maximum + to_prog.maximum
        from_prog.maximum = 0
        # Remove from_prog from play
        board_list = pickle.loads(self.board_list_pickle)
        board_list.remove(from_prog.__tablename__.title())
        self.board_list_pickle = pickle.dumps(board_list)
        db.session.commit()
        message = from_prog.__tablename__.title() + " converted to " \
            + to_prog.__tablename__.title()
        moves.append(message)
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
    try:
        for i in range(number):
            selection = random.choice(available_beads)
            collection.append(selection)
            available_beads.remove(selection)
    except IndexError:
        print("Ran out of available_beads")
    return available_beads, collection


def generate_anywhere_list(board_list_pickle):
    # Board list always contains "Intake"
    board_list = pickle.loads(board_list_pickle)
    board_list.remove("Intake")
    if "Outreach" in board_list:
        board_list.remove("Outreach")
    return random.sample(board_list, len(board_list))
