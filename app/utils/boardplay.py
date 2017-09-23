import math
import pickle
from app import db
from ..models.boards import Emergency, Rapid, Outreach, Transitional, Permanent
from ..models.boards import Unsheltered, Market
from .recordkeeping import write_record


def play_intake(game):
    # Load boards
    intake = game.load_intake()
    unsheltered = Unsheltered.query.filter_by(game_id=game.id).first()
    market = Market.query.filter_by(game_id=game.id).first()
    emerg = Emergency.query.filter_by(game_id=game.id).first()
    # col = one 'column' in game instructions
    col = math.ceil(50 / game.intake_cols)

    # Move beads and record moves
    # If Diversion is open
    if game.intake_cols == 6:
        intake = market.receive_unlimited(col, intake)
        write_record(game.id, game.round_count, 0, 7, col)
    surplus, intake, beads_moved = emerg.receive_beads(col, intake)
    write_record(game.id, game.round_count, 0, 1, col)
    if game.round_count == 1:
        intake = unsheltered.receive_unlimited(col, intake)
        write_record(game.id, game.round_count, 0, 6, col)
    elif game.round_count == 4:
        surplus, intake = emerg.receive_beads(col, intake,)
        write_record(game.id, game.round_count, 0, 1, col)
    db.session.commit()
    intake = game.send_anywhere(len(intake), intake, 0)
    # Intake always ends at 0, and can't receive, so not saved to db
    return


def play_emergency(game):
    # Load boards
    emerg = Emergency.query.filter_by(game_id=game.id).first()
    emerg_board = pickle.loads(emerg.board)
    unsheltered = Unsheltered.query.filter_by(game_id=game.id).first()
    market = Market.query.filter_by(game_id=game.id).first()
    # Each board has 5 columns - emergency rules say to move 1.5 cols
    col = math.ceil(1.5 * (emerg.maximum / 5))

    # Move beads and record moves
    emerg_board = market.receive_unlimited(col, emerg_board)
    write_record(game.id, game.round_count, 1, 7, col)
    emerg_board = unsheltered.receive_unlimited(col, emerg_board)
    write_record(game.id, game.round_count, 1, 6, col)
    if len(emerg_board) > 0:
        emerg_board = game.send_anywhere(len(emerg_board), emerg_board, 1)

    # Save played board
    emerg.board = pickle.dumps(emerg_board)
    db.session.commit()
    return


def play_rapid(game):
    # Load boards
    rapid = Rapid.query.filter_by(game_id=game.id).first()
    rapid_board = pickle.loads(rapid.board)
    market = Market.query.filter_by(game_id=game.id).first()
    emerg = Emergency.query.filter_by(game_id=game.id).first()
    # Each board has 5 columns
    col = math.ceil(rapid.maximum / 5)

    # Move beads and record moves
    rapid_board = market.receive_unlimited(3 * col, rapid_board)
    write_record(game.id, game.round_count, 2, 7, 3 * col)
    extra, rapid_board, beads_moved = emerg.receive_beads(col, rapid_board)
    write_record(game.id, game.round_count, 2, 1, col)

    # Save played board
    rapid.board = pickle.dumps(rapid_board)
    db.session.commit()
    return


def play_outreach(game):
    # Load boards
    unsheltered = Unsheltered.query.filter_by(game_id=game.id).first()
    unsheltered_board = pickle.loads(unsheltered.board)
    outreach = Outreach.query.filter_by(game_id=game.id).first()

    # Move beads TO outreach
    unsheltered_board, outreach_board,\
        beads_moved = outreach.fill_from(unsheltered_board)
    write_record(game.id, game.round_count, 6, 3, beads_moved)
    unsheltered.board = pickle.dumps(unsheltered_board)
    # Move beads FROM Outreach
    outreach_board = game.send_anywhere(len(outreach_board),
                                        outreach_board, 3)

    # Save played board
    outreach.board = pickle.dumps(outreach_board)
    db.session.commit()
    return


def play_transitional(game):
    # Load boards
    trans = Transitional.query.filter_by(game_id=game.id).first()
    trans_board = pickle.loads(trans.board)
    market = Market.query.filter_by(game_id=game.id).first()
    emerg = Emergency.query.filter_by(game_id=game.id).first()
    unsheltered = Unsheltered.query.filter_by(game_id=game.id).first()
    # Each board has 5 columns
    col = math.ceil(trans.maximum / 5)

    # Move beads
    trans_board = market.receive_unlimited(col, trans_board)
    write_record(game.id, game.round_count, 4, 7, col)
    extra, trans_board, beads_moved = emerg.receive_beads(col, trans_board)
    write_record(game.id, game.round_count, 4, 1, col)
    if extra:
        trans_board = unsheltered.receive_unlimited(extra, trans_board, 4)

    # Save played board
    trans.board = pickle.dumps(trans_board)
    db.session.commit()
    return


def play_permanent(game):
    # Load board
    perm = Permanent.query.filter_by(game_id=game.id).first()
    perm_board = pickle.loads(perm.board)

    # Moves beads; different rules depending on even or odd round
    if game.round_count % 2 == 0:
        unsheltered = Unsheltered.query.filter_by(game_id=game.id).first()
        perm_board = unsheltered.receive_unlimited(1, perm_board)
        write_record(game.id, game.round_count, 5, 6, 1)
    else:
        market = Market.query.filter_by(game_id=game.id).first()
        perm_board = market.receive_unlimited(1, perm_board)
        write_record(game.id, game.round_count, 5, 7, 1)

    # Save played board
    perm.board = pickle.dumps(perm_board)
    db.session.commit()
    return


DISPATCHER_DEFAULT = [play_intake,
                      play_emergency,
                      play_rapid,
                      play_outreach,
                      play_transitional,
                      play_permanent]
