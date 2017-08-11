import pickle
from datetime import datetime
from flask import redirect, url_for, flash
from app import db
from .boards import Emergency, Rapid, Outreach, Transitional
from .boards import Permanent, Unsheltered, Market
from .score import Score, Record, Log, Intake
from ..utils.lists import BOARD_LIST, AVAILABLE_BEADS, EMERG_START
from ..utils.lists import RAPID_START, OUTREACH_START, TRANS_START, PERM_START
from ..utils.lists import EMPTY_LIST, EXTRA_BOARD, generate_anywhere_list
from ..utils.statusloads import load_counts_and_changes
from ..utils.beadmoves import move_beads


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, default=datetime.now)
    round_count = db.Column(db.Integer, default=1)
    board_to_play = db.Column(db.Integer, default=0)
    intake_cols = db.Column(db.Integer, default=5)
    available_pickle = db.Column(db.PickleType, default=AVAILABLE_BEADS)
    board_list_pickle = db.Column(db.PickleType, default=BOARD_LIST)
    final_score = db.Column(db.Integer, default=0)
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

    def load_intake(self, no_red, moves):
        available_beads = pickle.loads(self.available_pickle)
        if len(available_beads) == 0:
            flash(u'Game over - no more plays.', 'warning')
            return redirect(url_for('status', game_id=self.id))
        else:
            intake = []
            available_beads, intake = move_beads(50, available_beads, intake,
                                                 no_red)
            self.available_pickle = pickle.dumps(available_beads)
            db.session.commit()
            moves.append("50 beads to intake")
            return intake, moves

    def send_anywhere(self, extra, from_board, no_red, moves):
        if self.board_to_play == 0:
            intake_record = Intake.query.filter(Intake.game_id == self.id,
                                                Intake.round_count == self.round_count
                                                ).order_by(desc(Intake.id)).first()

        # Get list of available programs to send beads
        anywhere_list = generate_anywhere_list(self.board_list_pickle)
        # Cycle through programs, moving as many beads as possible to each
        while len(from_board) > 0 and len(anywhere_list) > 0:
            prog_table = eval(anywhere_list.pop())
            prog = prog_table.query.filter_by(game_id=self.id).first()
            extra, from_board, moves = prog.receive_beads(extra,
                                                          from_board,
                                                          no_red,
                                                          moves)
        # Whatever remains is sent to unsheltered
        if len(from_board) > 0:
            unsheltered = Unsheltered.query.filter_by(game_id=self.id).first()
            from_board, moves = unsheltered.receive_unlimited(len(from_board),
                                                              from_board,
                                                              no_red,
                                                              moves)
        return from_board, moves

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

    def calculate_final_score(self):
        # Count lists
        counts, changes = load_counts_and_changes(self.id,
                                                  ['Emergency',
                                                   'Transitional'])
        # end_counts
        end_counts = {}
        for board in ['Rapid', 'Permanent', 'Unsheltered', 'Market']:
            this_record = Record.query.filter(Record.game_id == self.id,
                                              Record.board_name == board,
                                              Record.round_count == 5,
                                              ).first()
            end_counts[board] = this_record.end_count

        # Create, fill and return the scoreboard
        new_Score = Score(game_id=self.id)
        new_Score.emerg_total = sum(counts['Emergency'])
        new_Score.rapid = end_counts['Rapid']
        new_Score.trans_total = sum(counts['Transitional'])
        new_Score.perm = end_counts['Permanent']
        new_Score.unsheltered = end_counts['Unsheltered']
        new_Score.market = end_counts['Market']
        db.session.add(new_Score)
        db.session.commit()
        final_score = (new_Score.unsheltered * 3) + new_Score.emerg_total \
                      + new_Score.trans_total - new_Score.market \
                      + new_Score.rapid + new_Score.perm
        return final_score
