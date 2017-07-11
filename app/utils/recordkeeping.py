from app import db
from .models import Record


def load_counts(game_id, board_list):
    counts = {}
    for board in board_list:
        board_counts = []
        # Get all records associated wtih the board, in order
        records = Record.query.filter(Record.game_id == game_id,
                                      Record.board_name == board
                                      ).order_by(Record.id)
        # Pull the end_counts from each record
        for record in records:
            board_counts.append(record.end_count)
        counts[board] = board_counts
    return counts


def intiate_records(game):
    from app.utils import RECORDS_LIST
    from sqlalchemy import desc
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


def message_for(beads_moved, board_name):
    if beads_moved == "0":
        message = "No room in " + board_name
    else:
        message = str(beads_moved) + " beads to " + board_name
    return message
