def message_for(beads_moved, board_name):
    if beads_moved == "0":
        message = "No room in " + board_name
    else:
        message = str(beads_moved) + " beads to " + board_name
    return message


def gen_progs_for_sys_event(board_list_pickle):
    """Generate programs dict for round 2/3 system_event"""
    import pickle
    board_list = pickle.loads(board_list_pickle)
    progs_list = board_list[:]
    progs_list.remove('Intake')
    progs_dict = {}
    for prog in progs_list:
        short_list = progs_list[:]
        short_list.remove(prog)
        progs_dict[prog] = short_list
    return progs_dict
