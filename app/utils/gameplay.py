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


