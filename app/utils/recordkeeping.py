from app import db
from .lists import BOARD_CHARTS_LIST
from .dbsupport import get_board_contents
from ..models.record import Record, Count


def write_record(game_id, round_count, from_num, to_num, beads_moved):
    """ Creates a record for each movement of beads """
    new_record = Record(game_id=game_id,
                        round_count=round_count,
                        from_board_num=from_num,
                        to_board_num=to_num,
                        beads_moved=beads_moved)
    db.session.add(new_record)
    db.session.commit()
#    print('New Record: from ' + str(from_num) + ' to ' + str(to_num) + ', ' +
#          str(beads_moved) + ' beads')
    return


def end_round(game):
    # Update counts, then reset counters
    write_all_counts(game.id, game.round_count)
    game.round_count += 1
    game.board_to_play = reset_board_to_play(game.round_count)
    # If game is over, time to calculate Final Score
    if game.round_count == 6:
        final_score = game.generate_score()
        game.final_score = final_score
    db.session.commit()
    return


def write_all_counts(game_id, round_count):
    for board_num in BOARD_CHARTS_LIST:
        program, prog_board = get_board_contents(game_id, board_num)
        board_length = len(prog_board)
        write_count(game_id, round_count, board_num, board_length)
    return


def write_count(game_id, round_count, board_num, beads):
    this_count = Count(game_id=game_id,
                       round_count=round_count,
                       board_num=board_num,
                       beads=beads)
    db.session.add(this_count)
    db.session.commit()
#    print('Board ' + str(board_num) + ' has ' + str(beads) +
#          ' beads at end of round ' + str(round_count))
    return


def reset_board_to_play(round_count):
    # System event if moving into round 2-4
    if round_count < 5:
        board_to_play = 9
    else:
        # This is safe, b/c intake board is always 0, and always played first
        board_to_play = 0
    return board_to_play
