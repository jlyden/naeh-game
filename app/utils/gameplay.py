import random


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
