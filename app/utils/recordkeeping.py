from app import db
from .lists import ALL_BOARDS_LIST, pull_intake
from .dbsupport import get_board_contents
from ..models.record import Record, Count


def write_record(game_id, round_count, from_num, to_num, beads_moved):
    new_record = Record(game_id=game_id,
                        round_count=round_count,
                        from_board_num=from_num,
                        to_board_num=to_num,
                        beads_moved=beads_moved)
    db.session.add(new_record)
    db.session.commit()
    print('New Record: from ' + str(from_num) + ' to ' + str(to_num) + ', ' +
          str(beads_moved) + ' beads')
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
    trimmed_board_list = pull_intake()
    for prog in trimmed_board_list:
        # Get board number
        board_num = ALL_BOARDS_LIST.index(prog)
        # Get board length
        program, prog_board = get_board_contents(game_id, prog)
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
    print('Board ' + str(board_num) + ' has ' + str(beads) +
          ' beads at end of round ' + str(round_count))
    return
