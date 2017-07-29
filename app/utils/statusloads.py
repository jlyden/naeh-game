import pickle
from sqlalchemy import desc
from ..models.score import Record, Log
from ..models.boards import Emergency, Rapid, Outreach, Transitional, Permanent
from ..models.boards import Unsheltered, Market


def load_boards_and_maxes(game_id, max_list, board_list):
    boards = {}
    maxes = {}
    for board in board_list:
        prog_table = eval(board)
        prog = prog_table.query.filter_by(game_id=game_id).first()
        prog_board = pickle.loads(prog.board)
        boards[board] = prog_board
        if board in max_list:
            board_max = prog.maximum
            maxes[board] = board_max
    return boards, maxes


def load_counts_and_changes(game_id, board_list):
    counts = {}
    changes = {}
    for board in board_list:
        board_counts = []
        changes_tuples = []
        # Get all records associated with the board, in order
        records = Record.query.filter(Record.game_id == game_id,
                                      Record.board_name == board
                                      ).order_by(Record.id)
        # Pull the end_counts from each record
        for record in records:
            board_counts.append(record.end_count)
            tup = (record.beads_in, record.beads_out)
            changes_tuples.append(tup)
        counts[board] = board_counts
        # Trim first tup, b/c it's before round 1
        changes_tuples.pop(0)
        changes[board] = changes_tuples
    return counts, changes


def load_decisions(game_id):
    decisions = []
    records = Record.query.filter(Record.game_id == game_id,
                                  Record.note.isnot(None)
                                  ).order_by(Record.id)
    for record in records:
        decisions.append(record.note)
    return decisions


def load_logs(game_id, round_count):
    moves_by_round = []
    for i in range(1, 6):
        round_logs = Log.query.filter(Log.game_id == game_id,
                                      Log.round_count == i).order_by(Log.id)
        logs = []
        for log in round_logs:
            last_moves = pickle.loads(log.moves)
            logs.append(last_moves)
        moves_by_round.append(logs)
    return moves_by_round


def load_records(game_id, board_list):
    records = []
    for board in board_list:
        if board != 'Intake':
            # This order_by gives us last record per board
            record = Record.query.filter(Record.game_id == game_id,
                                         Record.board_name == board
                                         ).order_by(desc(Record.id)).first()
            records.append(record)
    return records
