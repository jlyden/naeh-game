from ..models.record import Record, Count, Decision
from .lists import pull_intake, prep_for_counts
from .dbsupport import get_board_contents


def load_board_lens_and_maxes(game_id, current_board_list):
    """ Get lengths of all boards and max values of active boards  """
    board_lens = {}
    maxes = {}
    trimmed_board_list = pull_intake()
    for prog in trimmed_board_list:
        program, prog_board = get_board_contents(game_id, prog)
        board_lens[prog] = len(prog_board)
        if prog in current_board_list:
            board_max = program.maximum
            maxes[prog] = board_max
    return board_lens, maxes


def load_counts(game_id, board_num_list):
    """ Get round-by-round counts of active boards """
    updated_board_list = prep_for_counts(board_num_list)
    all_counts = {}
    for board_num in updated_board_list:
        board_counts = []
        # Get all counts associated with the board, in order
        counts = Count.query.filter(Count.game_id == game_id,
                                    Count.board_num == board_num
                                    ).order_by(Count.id)
        # Put the counts into a list and add to dict
        for count in counts:
            board_counts.append(count.beads)
        all_counts[board_num] = board_counts
    return all_counts


def load_final_counts(game_id, board_num_list):
    """ Get final counts (end of round 5) """
    final_counts = {}
    for board_num in board_num_list:
        board_counts = []
        # Get all counts associated with the board, in order
        counts = Count.query.filter(Count.game_id == game_id,
                                    Count.board_num == board_num
                                    ).order_by(Count.id)
        # Put the counts into a list and add to dict
        for count in counts:
            board_counts.append(count.beads)
        final_counts[board_num] = board_counts
    return final_counts


def load_changes(game_id, round_count, board_num_list):
    """ Get round-by-round changes (beads in, beads out) of active boards """
    changes = {}
    rounds = range(1, round_count + 1)
    # Run through all the rounds, calculating tuples
    print('board num list is ' + str(board_num_list))
    for board_num in board_num_list:
        changes_tuples = []
        for each_round in rounds:
            from_sum = 0
            to_sum = 0
            # Get all to_board stats for that board
            to_board_recs = Record.query.filter(Record.game_id == game_id,
                                                Record.to_board_num ==
                                                board_num)
            # Sum beads_moved IN
            for rec in to_board_recs:
                to_sum += rec.beads_moved
            # Get all from_board stats for that board
            from_board_recs = Record.query.filter(Record.game_id == game_id,
                                                  Record.from_board_num ==
                                                  board_num)
            # Sum beads_moved OUT
            for rec in from_board_recs:
                from_sum += rec.beads_moved
            # Add tuple of changes (to, from)
            tup = (to_sum, from_sum)
            changes_tuples.append(tup)
            print('board num ' + str(board_num) + ' change tuples is ' + str(changes_tuples))
        changes[board_num] = changes_tuples
    print(str(changes))
    return changes


def load_decisions(game_id):
    """ Get major game decisions """
    decisions = []
    dec_objs = Decision.query.filter(Decision.game_id == game_id
                                     ).order_by(Decision.id)
    for dec in dec_objs:
        decisions.append(dec.note)
    return decisions
