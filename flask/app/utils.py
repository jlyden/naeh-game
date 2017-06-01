import random


def get_random_bead(number, available_beads):
    collection = []
    for i in range(number):
        selection = random.choice(available_beads)
        collection.append(selection)
        available_beads.remove(selection)
    return available_beads, collection


def move_beads(number, from_board, to_board):
    for i in range(number):
        selection = from_board.pop()
        to_board.append(selection)
    return from_board, to_board


def find_room(board_max, board):
    room = board_max - len(board)
    return room


def use_room(room, beads, from_board, to_board):
    if room > beads:
        from_board, to_board = move_beads(beads, from_board, to_board)
        extra = 0
    elif beads > room:
        from_board, to_board = move_beads(room, from_board, to_board)
        extra = beads - room
    return extra, from_board, to_board
