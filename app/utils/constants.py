import pickle


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
BOARD_LIST = pickle.dumps(["Intake", "Emergency", "Rapid",
                           "Outreach", "Transitional", "Permanent"])
RECORDS_LIST = ["Emergency", "Rapid", "Outreach", "Transitional",
                "Permanent", "Unsheltered", "Market"]
