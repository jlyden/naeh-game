from .lists import BOARD_LIST
from ..models.game import Game


def gen_board_string_list(board_num_list):
    progs_list = []
    for board_num in board_num_list:
        progs_list.append(BOARD_LIST[board_num])
    return progs_list


def gen_progs_for_sys_event(board_list):
    """Generate programs dict for round 2/3 system_event"""
    board_list.remove('Intake')
    progs_dict = {}
    for board in board_list:
        short_list = board_list[:]
        short_list.remove(board)
        progs_dict[board] = short_list
    return progs_dict


def set_board_to_play(board_num, board_num_list):
    """ Get next board_num from list """
    current_index = board_num_list.index(board_num)
    next_index = current_index + 1
    # if next_index exceeds board_num_list, set to end round
    if next_index > (len(board_num_list) - 1):
        board_to_play = 6
    else:
        board_to_play = board_num_list(current_index + 1)
    return board_to_play


def check_no_red(game_id, table_name):
    # This is called from boards.py, so we need to query the game
    this_game = Game.query.get_or_404(int(game_id))
    # No_red beads rules for Transitional board
    if table_name == "transitional":
        no_red = True
    # No_red beads rules for Emergency board
    elif this_game.board_to_play == 1 and \
        table_name == "market" and (this_game.round_count == 1 or
                                    this_game.round_count == 3):
        no_red = True
    # No_red beads rules for Rapid board
    elif this_game.board_to_play == 2 and (this_game.round_count == 2 or
                                           this_game.round_count == 4):
        no_red = True
    else:
        no_red = False
    return no_red
