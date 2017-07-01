import random
import pickle


BOARD_LIST = ["Intake", "Emergency", "Rapid",
              "Outreach", "Transitional", "Permanent"]


def get_random_bead(number, available_pickle):
    available_beads = pickle.loads(available_pickle)
    collection = []
    for i in range(number):
        selection = random.choice(available_beads)
        collection.append(selection)
        available_beads.remove(selection)
    available_pickle = pickle.dumps(available_beads)
    collection_pickle = pickle.dumps(collection)
    return available_pickle, collection_pickle


def move_beads(number, from_board, to_board_pickle):
    to_board = pickle.loads(to_board_pickle)
    for i in range(number):
        selection = from_board.pop()
        to_board.append(selection)
    to_board_pickle = pickle.dumps(to_board)
    print(str(number) + 'beads moved')
    return from_board, to_board_pickle


def find_room(board_max, board_pickle):
    board = pickle.loads(board_pickle)
    room = board_max - len(board)
    return room


def use_room(room, beads, from_board, to_board_pickle):
    if room > beads:
        from_board, to_board_pickle = move_beads(beads, from_board,
                                                 to_board_pickle)
        extra = 0
    elif beads >= room:
        from_board, to_board_pickle = move_beads(room, from_board,
                                                 to_board_pickle)
        extra = beads - room
    return extra, from_board, to_board_pickle


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
