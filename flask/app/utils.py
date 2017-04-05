import random
from flask import flash


maximum = {'emergency': 25,
           'rapid': 10,
           'transitional': 20,
           'permanent': 20}


def get_random_bead(number, available_beads):
    collection = []
    for i in range(number):
        selection = random.choice(available_beads)
        collection.append(selection)
        available_beads.remove(selection)
    return collection, available_beads


def move_beads(number, from_board, to_board):
    for i in range(number):
        selection = from_board.pop()
        to_board.append(selection)
    return from_board, to_board


def find_room(board, board_max):
    print('max=' + str(board_max) + ', len=' + str(len(board)))
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


def single_board_transfer(beads, from_board, to_board, to_board_max):
    room = find_room(to_board, to_board_max)
    if room is 0:
        extra = beads
    else:
        extra, from_board, to_board = use_room(room, beads, from_board,
                                               to_board)
    return extra, from_board, to_board
