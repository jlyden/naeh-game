import pickle
from app import db
from sqlalchemy import desc
from .score import Record
from app.utils import move_beads, find_room, use_room, message_for


# Mixin class for related boards
class Other_Boards(object):
    board = db.Column(db.PickleType)
    maximum = db.Column(db.Integer)

    def __repr__(self):
        board = pickle.loads(self.board)
        return "%r -> %r" % self.__tablename__, str(board)

    def receive_beads(self, bead_count, from_board, no_red, moves):
        # transitional board may reject red beads
        if self.__tablename__ == 'transitional':
            no_red = self.no_red

        this_board = pickle.loads(self.board)
        room = find_room(self.maximum, this_board)
        if room != 0:
            extra, from_board, this_board = use_room(room, bead_count,
                                                     from_board, this_board,
                                                     no_red)
            self.board = pickle.dumps(this_board)
            beads_moved = bead_count - extra
            record = Record.query.filter(Record.game_id == self.game_id,
                                         Record.board_name ==
                                         self.__tablename__.title()
                                         ).order_by(desc(Record.id)).first()
            record.record_change_beads('in', beads_moved, no_red)
        else:
            extra = bead_count
            beads_moved = 0
        db.session.commit()
        moves.append(message_for(str(beads_moved), self.__tablename__.title()))
        return extra, from_board, moves

    def receive_unlimited(self, beads, from_board, no_red, moves):
        this_board = pickle.loads(self.board)
        from_board, this_board = move_beads(beads, from_board,
                                            this_board, no_red)
        self.board = pickle.dumps(this_board)
        record = Record.query.filter(Record.game_id == self.game_id,
                                     Record.board_name ==
                                     self.__tablename__.title()
                                     ).order_by(desc(Record.id)).first()
        record.record_change_beads('in', beads, no_red)
        db.session.commit()
        moves.append(message_for(beads, self.__tablename__.title()))
        return from_board, moves


class Emergency(db.Model, Other_Boards):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))


class Rapid(db.Model, Other_Boards):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))


class Outreach(db.Model, Other_Boards):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

    def fill_from(self, unsheltered_board, no_red, moves):
        # Fill Outreach Board from Unsheltered
        outreach_board = pickle.loads(self.board)
        room = find_room(self.maximum, outreach_board)
        unsheltered_board, outreach_board = move_beads(room, unsheltered_board,
                                                       outreach_board, no_red)
        record = Record.query.filter(Record.game_id == self.game_id,
                                     Record.board_name ==
                                     self.__tablename__.title()
                                     ).order_by(desc(Record.id)).first()
        print("fill_from found " + str(record))
        record.record_change_beads('in', room, no_red)
        message = str(room) + " beads from Unsheltered to Outreach"
        moves.append(message)
        return unsheltered_board, outreach_board, moves


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

