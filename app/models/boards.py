import random
import pickle
from app import db
from sqlalchemy import desc
from .score import Record


# Mixin class for related boards
class Other_Boards(object):
    board = db.Column(db.PickleType)
    maximum = db.Column(db.Integer)

    def __repr__(self):
        board = pickle.loads(self.board)
        return "Game %r" % str(board)

    def __init__(self, game_id, board, maximum):
        self.game_id = game_id
        self.board = board
        self.maximum = maximum

    def receive_beads(self, bead_count, from_board, no_red, moves):
        if self.__tablename__ == 'transitional':
            no_red = self.no_red
        beads_moved = 0
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
            print("receive_beads found " + str(record))
            record.record_change_beads('in', beads_moved, no_red)
        else:
            extra = bead_count
        db.session.commit()
        moves.append(message_for(str(beads_moved), self.__tablename__.title()))
        return extra, from_board, moves

    def receive_unlimited(self, beads, from_board, no_red, moves):
        # No need for records here - end_count captured at end of round
        this_board = pickle.loads(self.board)
        from_board, this_board = move_beads(beads, from_board,
                                            this_board, no_red)
        self.board = pickle.dumps(this_board)
        record = Record.query.filter(Record.game_id == self.game_id,
                                     Record.board_name ==
                                     self.__tablename__.title()
                                     ).order_by(desc(Record.id)).first()
        print("receive_unlimited found " + str(record))
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
        record.record_change_beads('in', room)
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


# Helper methods
def move_beads(number, from_board, to_board, no_red):
    for i in range(number):
        selection = random.choice(from_board)
        # If no_red = True, and this bead is red, don't move it
        if no_red and selection < 65:
            pass
        else:
            to_board.append(selection)
            from_board.remove(selection)
    return from_board, to_board


def find_room(board_max, board):
    room = board_max - len(board)
    return room


def use_room(room, number_beads, from_board, to_board, no_red):
    if room > number_beads:
        from_board, to_board = move_beads(number_beads, from_board,
                                          to_board, no_red)
        extra = 0
    elif number_beads >= room:
        from_board, to_board = move_beads(room, from_board, to_board, no_red)
        extra = number_beads - room
    return extra, from_board, to_board


def message_for(beads_moved, board):
    if beads_moved == "0":
        message = "No room in " + board
    else:
        message = str(beads_moved) + " beads to " + board
    return message
