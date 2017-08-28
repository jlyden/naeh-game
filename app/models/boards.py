import pickle
from app import db
from ..utils.beadmoves import move_beads, find_room, use_room


# Mixin class for related boards
class Other_Boards(object):
    board = db.Column(db.PickleType)
    maximum = db.Column(db.Integer)

    def __repr__(self):
        board = pickle.loads(self.board)
        return "%r -> %r" % self.__tablename__, str(board)

    def receive_beads(self, bead_count, from_board):
        from .boards.game import check_no_red
        no_red = check_no_red(self.game_id, self.__tablename__)
        this_board = pickle.loads(self.board)
        room = find_room(self.maximum, this_board)
        if room > 0:
            extra, from_board, this_board = use_room(room, bead_count,
                                                     from_board, this_board,
                                                     no_red)
            self.board = pickle.dumps(this_board)
            db.session.commit()
            beads_moved = bead_count - extra
        else:
            extra = bead_count
            beads_moved = 0
        return extra, from_board, beads_moved

    def receive_unlimited(self, bead_count, from_board):
        from .boards.game import check_no_red
        no_red = check_no_red(self.game_id, self.__tablename__)
        this_board = pickle.loads(self.board)
        from_board, this_board = move_beads(bead_count, from_board,
                                            this_board, no_red)
        self.board = pickle.dumps(this_board)
        db.session.commit()
        return from_board


class Emergency(db.Model, Other_Boards):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))


class Rapid(db.Model, Other_Boards):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))


class Outreach(db.Model, Other_Boards):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

    def fill_from(self, unsheltered_board):
        # Fill Outreach Board from Unsheltered
        no_red = False  # No restrictions on red beads to Outreach
        outreach_board = pickle.loads(self.board)
        room = find_room(self.maximum, outreach_board)
        unsheltered_board, outreach_board = move_beads(room, unsheltered_board,
                                                       outreach_board, no_red)
        return unsheltered_board, outreach_board, room


class Transitional(db.Model, Other_Boards):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    no_red = db.Column(db.Boolean, default=False)


class Permanent(db.Model, Other_Boards):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))


class Unsheltered(db.Model, Other_Boards):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))


class Market(db.Model, Other_Boards):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
