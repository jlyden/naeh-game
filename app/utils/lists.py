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

BOARD_LIST = ["Intake", "Emergency", "Rapid",
              "Outreach", "Transitional", "Permanent"]

BOARD_NUM_LIST = pickle.dumps(list(range(0, 6)))

BOARD_CHARTS_LIST = [1, 2, 4, 5, 6, 7]

ALL_BOARDS_LIST = ["Intake", "Emergency", "Rapid", "Outreach",
                   "Transitional", "Permanent", "Unsheltered", "Market"]


def generate_anywhere_list(board_num_list_pickle):
    # Board list always contains 0 (Intake)
    board_num_list = pickle.loads(board_num_list_pickle)
    board_num_list.remove(0)
    # Board list might contain 3 (Outreach)
    if 3 in board_num_list:
        board_num_list.remove(3)
    return random.sample(board_num_list, len(board_num_list))


def pull_intake():
    board_list_copy = list(ALL_BOARDS_LIST)
    board_list_copy.remove("Intake")
    return board_list_copy
