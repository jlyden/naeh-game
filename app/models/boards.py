import pickle
from app import db
from sqlalchemy import desc


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

    def receive_beads(self, beads, from_board, moves):
        this_board = pickle.loads(self.board)
        room = find_room(self.maximum, this_board)
        beads_moved = 0
        extra = 0
        if room != 0:
            extra, from_board, this_board = use_room(room, beads,
                                                     from_board, this_board)
            self.board = pickle.dumps(this_board)
            beads_moved = beads - extra
        #     # Order_by desc, then taking first gives most recent (i.e. current) record
        #     record = Record.query.filter(Record.game_id == self.game_id,
        #                                  Record.board_name ==
        #                                  self.__tablename__.title()
        #                                  ).order_by(desc(Record.id)).first()
        #     print(str(record) + " for " + self.__tablename__.title() + " board")
        #     record.record_change_beads('in', beads_moved)
        #     print(self.__tablename__.title() + " moved " + str(beads_moved) + " beads IN")
        # db.session.commit()
        moves.append(message_for(str(beads_moved), self.__tablename__.title()))
        return extra, from_board, moves

    def receive_unlimited(self, beads, from_board, moves):
        this_board = pickle.loads(self.board)
        from_board, this_board = move_beads(beads, from_board, this_board)
        self.board = pickle.dumps(this_board)
        db.session.commit()
        moves.append(message_for(beads, self.__tablename__.title()))
        return from_board, moves

    def update_record(self):
        # add_record() accepts and returns a pickle object
        this_board = pickle.loads(self.board)
        self.record = add_record(self.record, len(this_board))
        db.session.commit()
        return


class Emergency(db.Model, Other_Boards):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))


class Rapid(db.Model, Other_Boards):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))


class Outreach(db.Model, Other_Boards):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

    def fill_from(self, unsheltered_board, moves):
        # Fill Outreach Board from Unsheltered
        outreach_board = pickle.loads(self.board)
        room = find_room(self.maximum, outreach_board)
        unsheltered_board, outreach_board = move_beads(room, unsheltered_board,
                                                       outreach_board)
        message = str(room) + " beads from unsheltered to outreach"
        # # Order_by desc, then taking first gives most recent (i.e. current) record
        # record = Record.query.filter(Record.game_id == self.game_id,
        #                              Record.board_name ==
        #                              self.__tablename__.title()
        #                              ).order_by(desc(Record.id)).first()
        # record.record_change_beads('in', room)
        moves.append(message)
        return unsheltered_board, outreach_board, moves


class Transitional(db.Model, Other_Boards):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))


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
def move_beads(number, from_board, to_board):
    try:
        for i in range(number):
            selection = from_board.pop(i)
            to_board.append(selection)
    except IndexError:
        print("Ran out of available_beads")
    return from_board, to_board


def find_room(board_max, board):
    room = board_max - len(board)
    return room


def use_room(room, beads, from_board, to_board):
    if room > beads:
        from_board, to_board_pickle = move_beads(beads, from_board, to_board)
        extra = 0
    elif beads >= room:
        from_board, to_board_pickle = move_beads(room, from_board, to_board)
        extra = beads - room
    return extra, from_board, to_board


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
