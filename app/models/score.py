import pickle
from sqlalchemy import desc
from app import db


class Stats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    round_count = db.Column(db.Integer, nullable=False)
    from_board = db.Column(db.Integer, nullable=False)
    to_board = db.Column(db.Integer, nullable=False)
    beads_moved = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<Stats: Game %r, Round %r, \
                 From_Board %r, To_Board %r, Beads %r >" % (self.game_id,
                                                            self.round_count,
                                                            self.from_board,
                                                            self.to_board,
                                                            self.beads_moved)


class Counts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    round_count = db.Column(db.Integer, nullable=False)
    board_num = db.Column(db.Integer, nullable=False)
    beads = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return "<End Counts: Game %r, Round %r,\
                 Board %r, Beads %r >" % (self.game_id,
                                          self.round_count,
                                          self.board,
                                          self.beads)


class Decisions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    round_count = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(500))

    def __repr__(self):
        return "<Decisions: Game %r, Round %r - %r >" % (self.game_id,
                                                         self.round_count,
                                                         self.note)


# TODO: Delete after record refactor
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    round_count = db.Column(db.Integer, nullable=False)
    board_played = db.Column(db.String(25))
    moves = db.Column(db.PickleType)

    def __repr__(self):
        return "<Log: Game %r, Round %r, Board %r >" % (self.game_id,
                                                        self.round_count,
                                                        self.board_played)

    def __init__(self, game_id, round_count, board_played, moves):
        self.game_id = game_id
        self.round_count = round_count
        self.board_played = board_played
        self.moves = pickle.dumps(moves)


# TODO: Delete after record refactor
class Intake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    round_count = db.Column(db.Integer, nullable=False)
    to_emerg = db.Column(db.Integer, default=0)
    to_rapid = db.Column(db.Integer, default=0)
    to_trans = db.Column(db.Integer, default=0)
    to_perm = db.Column(db.Integer, default=0)
    to_market = db.Column(db.Integer, default=0)
    to_unshel = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "<Intake Out: Game %r, Round %r>" % (self.game_id,
                                                    self.round_count)


# TODO: Delete after record refactor
class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    round_count = db.Column(db.Integer, nullable=False)
    board_name = db.Column(db.String(25), nullable=False)
    beads_in = db.Column(db.Integer, default=0)
    beads_out = db.Column(db.Integer, default=0)
    end_count = db.Column(db.Integer, nullable=False, default=0)
    note = db.Column(db.String(500))

    def __repr__(self):
        return "<Record: Game %r, Round %r, Board %r >" % (self.game_id,
                                                           self.round_count,
                                                           self.board_name)

    def record_change_beads(self, direction, bead_count):
        if direction == 'in':
            self.beads_in = self.beads_in + bead_count
        elif direction == 'out':
            self.beads_out = self.beads_out + bead_count
        db.session.commit()
        return

    def calc_end_count(self):
        # get end_count from last round
        last_record = Record.query.filter(Record.game_id == self.game_id,
                                          Record.board_name == self.board_name,
                                          Record.round_count ==
                                          self.round_count - 1
                                          ).order_by(desc(Record.id)).first()
        last_end_count = last_record.end_count
        # add beads_in, subtract beads out
        return last_end_count + self.beads_in - self.beads_out


# TODO: Delete after record refactor
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    unsheltered = db.Column(db.Integer, default=0)
    market = db.Column(db.Integer, default=0)
    rapid = db.Column(db.Integer, default=0)
    perm = db.Column(db.Integer, default=0)
    emerg_total = db.Column(db.Integer, default=0)
    trans_total = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "<Game %r Scoreboard>" % (self.game_id)
