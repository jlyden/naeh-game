import pickle
from ..models.boards import Emergency, Rapid, Outreach, Transitional
from ..models.boards import Permanent, Unsheltered, Market
from .lists import ALL_BOARDS


def get_board_contents(game_id, board_num):
    program_name = ALL_BOARDS[board_num]
    prog_table = eval(program_name)
    program = prog_table.query.filter_by(game_id=game_id).first()
    prog_board = pickle.loads(program.board)
    return program, prog_board


def check_no_red(game_id, table_name):
    from ..models.game import Game
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
