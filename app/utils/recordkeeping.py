import pickle
from sqlalchemy import desc
from app import db
from .lists import ALL_BOARDS_LIST
from ..models.boards import Emergency, Rapid, Outreach, Transitional
from ..models.boards import Permanent, Unsheltered, Market
from ..models.record import Record, Count


def write_record(game_id, round_count, from_num, to_num, beads_moved):
    new_record = Record(game_id=game_id,
                        round_count=round_count,
                        from_board_num=from_num,
                        to_board_num=to_num,
                        beads_moved=beads_moved)
    db.session.add(new_record)
    db.commit
    print('New Record: from ' + from_num + ' to ' + to_num + ', ' +
          beads_moved + ' beads')
    return


def end_round(game):
    # Update counts, then reset counters
    write_all_counts(game.id, game.round_count)
    game.round_count += 1
    # System event if moving into round 2-4
    if game.round_count < 5:
        game.board_to_play = 9
    else:
        # This is safe, b/c intake board is always 0, and always played first
        game.board_to_play = 0
    db.session.commit()
    return game.round_count


def write_all_counts(game_id, round_count):
    for board in ALL_BOARDS_LIST:
        # Get board number
        board_num = get_board_number(board)
        # Get board length
        prog_table = eval(board)
        prog = prog_table.query.filter_by(game_id=game_id).first()
        prog_board = pickle.loads(prog.board)
        board_length = len(prog_board)
        write_count(game_id, round_count, board_num, board_length)
    return


def write_count(game_id, round_count, board, beads):
    this_count = Count(game_id=game_id,
                       round_count=round_count,
                       board_name=board,
                       beads=beads)
    db.session.add(this_count)
    db.session.commit()
    print('Board ' + board + ' has ' + beads + ' beads at end of round ' +
          round_count)
    return


def get_board_number(board):
    """ ALL_BOARDS_LIST doesn't have Intake, so shift for that """
    return ALL_BOARDS_LIST.index(board) + 1
