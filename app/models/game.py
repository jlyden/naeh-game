import pickle
from datetime import datetime
from flask import redirect, url_for, flash
from app import db
from .boards import Emergency, Rapid, Outreach, Transitional
from .boards import Permanent, Unsheltered, Market
from .record import Record, Count
from ..utils.lists import BOARD_NUM_LIST, AVAILABLE_BEADS, EMERG_START
from ..utils.lists import BOARD_LIST
from ..utils.lists import RAPID_START, OUTREACH_START, TRANS_START, PERM_START
from ..utils.lists import EMPTY_LIST, EXTRA_BOARD, generate_anywhere_list
from ..utils.statusloads import load_counts, load_final_count
from ..utils.beadmoves import move_beads
from .recordkeeping import write_record


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, default=datetime.now)
    round_count = db.Column(db.Integer, default=1)
    board_to_play = db.Column(db.Integer, default=0)
    intake_cols = db.Column(db.Integer, default=5)
    available_pickle = db.Column(db.PickleType, default=AVAILABLE_BEADS)
    board_num_list_pickle = db.Column(db.PickleType, default=BOARD_NUM_LIST)
    final_score = db.Column(db.Integer, default=0)
    # One to One relationships
    emergency = db.relationship('Emergency', backref='game', uselist=False)
    rapid = db.relationship('Rapid', backref='game', uselist=False)
    outreach = db.relationship('Outreach', backref='game', uselist=False)
    transitional = db.relationship('Transitional', uselist=False,
                                   backref='game')
    permanent = db.relationship('Permanent', backref='game', uselist=False)
    unsheltered = db.relationship('Unsheltered', backref='game', uselist=False)
    market = db.relationship('Market', backref='game', uselist=False)
    # One to Many relationships
    records = db.relationship('Record', backref='game')
    counts = db.relationship('Count', backref='game')
    decisions = db.relationship('Decision', backref='game')

    def __repr__(self):
        return "<Game %r, round %r, board %r>" % (self.id,
                                                  self.round_count,
                                                  self.board_to_play)

    @classmethod
    def setup(cls):
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
        # Set up initial Counts for Charts
        E_count = Count(game_id=new_game.id,
                        round_count=0,
                        board_num=1,
                        beads=20)
        R_count = Count(game_id=new_game.id,
                        round_count=0,
                        board_num=2,
                        beads=10)
        T_count = Count(game_id=new_game.id,
                        round_count=0,
                        board_num=4,
                        beads=16)
        P_count = Count(game_id=new_game.id,
                        round_count=0,
                        board_num=5,
                        beads=20)
        U_count = Count(game_id=new_game.id,
                        round_count=0,
                        board_num=6,
                        beads=0)
        M_count = Count(game_id=new_game.id,
                        round_count=0,
                        board_num=7,
                        beads=0)

        db.session.add_all([new_Emergency, new_Rapid, new_Outreach,
                            new_Transitional, new_Permanent, new_Unsheltered,
                            new_Market, E_count, R_count, T_count,
                            P_count, U_count, M_count])
        db.session.commit()
        return new_game

    def load_intake(self):
        available_beads = pickle.loads(self.available_pickle)
        if len(available_beads) == 0:
            flash(u'Game over - no more plays.', 'warning')
            return redirect(url_for('status', game_id=self.id))
        else:
            intake = []
            no_red = False  # Red beads always allowed in Intake
            available_beads, intake = move_beads(50, available_beads, intake,
                                                 no_red)
            self.available_pickle = pickle.dumps(available_beads)
            db.session.commit()
            return intake

    def send_anywhere(self, extra, from_board, from_board_num):
        # Get list of available programs to send beads
        anywhere_list = generate_anywhere_list(self.board_num_list_pickle)
        # Cycle through programs, moving as many beads as possible to each
        while len(from_board) > 0 and len(anywhere_list) > 0:
            to_board_num = anywhere_list.pop()
            prog_table = eval(BOARD_LIST[to_board_num])
            prog = prog_table.query.filter_by(game_id=self.id).first()
            extra, from_board, beads_moved = prog.receive_beads(extra,
                                                                from_board)
            write_record(self.id, self.round_count, from_board_num,
                         to_board_num, beads_moved)

        # Whatever remains is sent to unsheltered
        if len(from_board) > 0:
            bead_count = len(from_board)
            unsheltered = Unsheltered.query.filter_by(game_id=self.id).first()
            from_board = unsheltered.receive_unlimited(bead_count,
                                                       from_board)
            write_record(self.id, self.round_count, from_board_num, 6,
                         bead_count)
        return from_board

    def open_new(self, program, moves):
        # Add 'diversion' column to intake board
        if program == 'Diversion':
            self.intake_cols = 6
            prog_record = Record(game_id=self.id, round_count=self.round_count,
                                 board_name="Market")
            prog_record.note = "Diversion opened round " + \
                str(self.round_count)
        # Add 'extra' board (i.e. 25 slots to selected board/program)
        else:
            prog_table = eval(program)
            prog = prog_table.query.filter_by(game_id=self.id).first()
            prog.maximum = EXTRA_BOARD + prog.maximum
            prog_record = Record(game_id=self.id, round_count=self.round_count,
                                 board_name=program)
            prog_record.note = program + " expanded round " + \
                str(self.round_count)
        db.session.add(prog_record)
        db.session.commit()
        message = "New " + program + " program added"
        moves.append(message)
        return moves

    def convert_program(self, from_program, to_program, moves):
        # Get both database objects and unpickle boards
        from_prog_table = eval(from_program)
        from_prog = from_prog_table.query.filter_by(game_id=self.id).first()
        from_prog_board = pickle.loads(from_prog.board)
        beads_moved = len(from_prog_board)
        to_prog_table = eval(to_program)
        to_prog = to_prog_table.query.filter_by(game_id=self.id).first()
        to_prog_board = pickle.loads(to_prog.board)
        # Initiate relevant records (in between rounds)
        from_record = Record(game_id=self.id, round_count=self.round_count,
                             board_name=from_program)
        from_record.beads_out = beads_moved
        from_record.note = from_program + " closed round " + \
            str(self.round_count)
        to_record = Record(game_id=self.id, round_count=self.round_count,
                           board_name=to_program)
        to_record.beads_in = beads_moved
        to_record.beads_out = 0
        to_record.end_count = to_record.calc_end_count()
        to_record.note = to_program + " expanded round " + \
            str(self.round_count)
        db.session.add_all([from_record, to_record])
        # Move beads from from_prog.board to to_prog.board
        from_prog_board, to_prog_board = move_beads(beads_moved,
                                                    from_prog_board,
                                                    to_prog_board,
                                                    False)
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

    def generate_score(self):
        # Count lists
        counts = load_counts(self.id, [1, 4])
        # End_counts
        final_counts = load_final_count(self.id, [2, 5, 6, 7])

        # Calculate the final score
        final_score = ((final_counts[6] * 3) +  # Unsheltered
                       sum(counts[1]) +         # Emergency
                       sum(counts[4]) -         # Transitional
                       final_counts[7] +        # Market
                       final_counts[2] +        # Rapid
                       final_counts[5])         # Permanent
        return final_score
