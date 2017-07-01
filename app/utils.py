import pickle


BOARD_LIST = ["Intake", "Emergency", "Rapid",
              "Outreach", "Transitional", "Permanent"]


def move_beads(number, from_board, to_board):
    if len(from_board) > 0:
        for i in range(number):
            selection = from_board.pop()
            to_board.append(selection)
        print(str(number) + ' beads moved')
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


