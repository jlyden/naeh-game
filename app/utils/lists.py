import pickle
import random

# Beads 1-65 are red
# ALL_BEADS = list(range(1, 325))
EMERG_START = pickle.dumps(list(range(1, 7)) + list(range(66, 80)))
RAPID_START = pickle.dumps(list(range(7, 8)) + list(range(80, 89)))
OUTREACH_START = pickle.dumps(list(range(8, 10)) + list(range(89, 95)))
TRANS_START = pickle.dumps(list(range(10, 14)) + list(range(95, 107)))
PERM_START = pickle.dumps(list(range(14, 26)) + list(range(107, 115)))
AVAILABLE_BEADS = pickle.dumps(list(range(26, 66)) + list(range(115, 325)))
EMPTY_LIST = pickle.dumps(list())

EXTRA_BOARD = 25
BOARD_NUM_LIST = pickle.dumps(list(range(0, 6)))

# The boards below are always called for status page
BOARD_CHARTS_LIST = [1, 2, 3, 4, 5, 6, 7]

ALL_BOARDS = ["Intake", "Emergency", "Rapid", "Outreach",
              "Transitional", "Permanent", "Unsheltered", "Market"]


def gen_anywhere_list(board_num_list_pickle):
    """ Generate random array of up-to-four boards numbers
        (for Emergency, Rapid, Transitional, Permanent)
        depending on what has not been closed """
    board_num_list = pickle.loads(board_num_list_pickle)
    board_num_list.remove(0)  # Intake
    if 3 in board_num_list:
        board_num_list.remove(3)  # Outreach
    return random.sample(board_num_list, len(board_num_list))


def gen_board_string_list(board_num_list):
    progs_list = []
    for board_num in board_num_list:
        progs_list.append(ALL_BOARDS[board_num])
    return progs_list


def gen_progs_for_sys_event(board_num_list):
    """ Generate programs dictionary for round 3-4 system_event """
    board_string_list = gen_board_string_list(board_num_list)
    board_string_list.remove('Intake')
    progs_dict = {}
    for board in board_string_list:
        short_list = board_string_list[:]
        short_list.remove(board)
        progs_dict[board] = short_list
    return progs_dict


def set_board_to_play(board_num, board_num_list):
    """ Get next board_num from list """
    current_index = board_num_list.index(board_num)
    next_index = current_index + 1
    # if next_index exceeds board_num_list, set to end round
    # TODO: Double check why (-1) - add logs
    if next_index > (len(board_num_list) - 1):
        board_to_play = 6
    else:
        board_to_play = board_num_list[next_index]
    return board_to_play


def pull_intake():
    board_list_copy = list(ALL_BOARDS)
    board_list_copy.remove("Intake")
    return board_list_copy
