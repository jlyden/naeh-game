import pickle
from sqlalchemy import desc
from app import db
from .lists import RECORDS_LIST
from ..models.boards import Emergency, Rapid, Outreach, Transitional, Permanent
from ..models.boards import Unsheltered, Market
from ..models.score import Record


def end_round(game, board_list):
    # Update record and reset counters - for ALL boards, even not being played
    update_all_records(game.id, game.round_count, RECORDS_LIST)
    game.round_count += 1
    game.board_to_play = 0
    db.session.commit()
    return


def intiate_records(game):
    # Initiate records which don't already exist
    for board in RECORDS_LIST:
        record = Record.query.filter(Record.game_id == game.id,
                                     Record.board_name == board,
                                     Record.round_count == game.round_count
                                     ).order_by(desc(Record.id)).first()
        if record is None:
            # initiate record for current round
            record = Record(game_id=game.id,
                            round_count=game.round_count,
                            board_name=board)
            db.session.add(record)
    db.session.commit()
    return


def update_all_records(game_id, round_count, board_list):
    for board in board_list:
        prog_table = eval(board)
        prog = prog_table.query.filter_by(game_id=game_id).first()
        prog_board = pickle.loads(prog.board)
        board_length = len(prog_board)
        record = Record.query.filter(Record.game_id == game_id,
                                     Record.board_name == board,
                                     Record.round_count == round_count
                                     ).order_by(desc(Record.id)).first()
        if record is None:
            # initiate record for current round
            record = Record(game_id=game_id,
                            round_count=round_count,
                            board_name=board)
            record.beads_in = board_length
            record.end_count = board_length
            db.session.add(record)
            print("Added NEW end_count record for " + board + ": " +
                  str(record.end_count))
        else:
            print("update_all_records found " + str(record))
            calc_end = record.calc_end_count()
            if board_length != calc_end:
                print(board + " length= " + str(board_length) + "; calc_end=" +
                      str(calc_end))
            record.end_count = board_length
            print("Updated end_count record for " + board + ": " +
                  str(record.end_count))
        db.session.commit()
    return
