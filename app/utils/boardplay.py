import math
import pickle
from app import db
from app.models import Emergency, Rapid, Outreach, Transitional, Permanent
from app.models import Unsheltered, Market
from .recordkeeping import intiate_records


def play_intake(game, moves):
    intiate_records(game)
    # Load boards
    intake, moves = game.load_intake(False, moves)
    unsheltered = Unsheltered.query.filter_by(game_id=game.id).first()
    market = Market.query.filter_by(game_id=game.id).first()
    emerg = Emergency.query.filter_by(game_id=game.id).first()
    # col = one 'column' in game instructions
    col = math.ceil(50 / game.intake_cols)
    no_red = False

    # Move beads
    # If Diversion column is open
    if game.intake_cols == 6:
        message = "Diversion column being played"
        moves.append(message)
        intake, moves = market.receive_unlimited(col, intake, no_red, moves)
    surplus, intake, moves = emerg.receive_beads(col, intake, no_red, moves)
    if game.round_count == 1:
        intake, moves = unsheltered.receive_unlimited(col, intake, no_red,
                                                      moves)
    elif game.round_count == 4:
        surplus, intake, moves = emerg.receive_beads(col, intake, no_red,
                                                     moves)
    intake, moves = game.send_anywhere(len(intake), intake, no_red, moves)
    # Intake always ends at 0, and can't receive, so not saved
    beads_moved = 50
    return moves, beads_moved, no_red


def play_emergency(game, moves):
    # Load boards
    emerg = Emergency.query.filter_by(game_id=game.id).first()
    emerg_board = pickle.loads(emerg.board)
    unsheltered = Unsheltered.query.filter_by(game_id=game.id).first()
    market = Market.query.filter_by(game_id=game.id).first()
    # Each board has 5 columns - emergency rules say to move 1.5 cols
    col = math.ceil(1.5 * (emerg.maximum / 5))
    # Emergency board is cleared each round
    beads_moved = len(emerg_board)

    # Move beads - If round 1 or 3, no red beads to Market Housing
    if game.round_count == 1 or game.round_count == 3:
        no_red = True
    else:
        no_red = False
    emerg_board, moves = market.receive_unlimited(col, emerg_board, no_red,
                                                  moves)
    emerg_board, moves = unsheltered.receive_unlimited(col, emerg_board, False,
                                                       moves)
    if len(emerg_board) > 0:
        emerg_board, moves = game.send_anywhere(len(emerg_board), emerg_board,
                                                False, moves)

    # Save played board
    emerg.board = pickle.dumps(emerg_board)
    db.session.commit()
    return moves, beads_moved, no_red


def play_rapid(game, moves):
    # Load boards
    rapid = Rapid.query.filter_by(game_id=game.id).first()
    rapid_board = pickle.loads(rapid.board)
    market = Market.query.filter_by(game_id=game.id).first()
    emerg = Emergency.query.filter_by(game_id=game.id).first()
    # Each board has 5 columns
    col = math.ceil(rapid.maximum / 5)
    # Save length so beads_moved can be calculated
    len_start = len(rapid_board)

    # Move beads - If round 2 or 4, no red beads move
    if game.round_count == 2 or game.round_count == 4:
        no_red = True
    else:
        no_red = False
    rapid_board, moves = market.receive_unlimited(3 * col, rapid_board,
                                                  no_red, moves)
    extra, rapid_board, moves = emerg.receive_beads(col, rapid_board,
                                                    no_red, moves)
    len_end = len(rapid_board)
    beads_moved = len_start - len_end

    # Save played board
    rapid.board = pickle.dumps(rapid_board)
    db.session.commit()
    return moves, beads_moved, no_red


def play_outreach(game, moves):
    # Load boards
    unsheltered = Unsheltered.query.filter_by(game_id=game.id).first()
    unsheltered_board = pickle.loads(unsheltered.board)
    outreach = Outreach.query.filter_by(game_id=game.id).first()
    no_red = False

    # Move beads TO outreach
    unsheltered_board, outreach_board, moves = \
        outreach.fill_from(unsheltered_board, no_red, moves)
    unsheltered.board = pickle.dumps(unsheltered_board)
    # Move beads FROM Outreach
    outreach_board, moves = game.send_anywhere(len(outreach_board),
                                               outreach_board, no_red, moves)

    # Save played board
    outreach.board = pickle.dumps(outreach_board)
    db.session.commit()
    # Outreach is filled to 10 and emptied each round
    return moves, 10, no_red


def play_transitional(game, moves):
    # Load boards
    trans = Transitional.query.filter_by(game_id=game.id).first()
    trans_board = pickle.loads(trans.board)
    market = Market.query.filter_by(game_id=game.id).first()
    emerg = Emergency.query.filter_by(game_id=game.id).first()
    unsheltered = Unsheltered.query.filter_by(game_id=game.id).first()
    # Each board has 5 columns
    col = math.ceil(trans.maximum / 5)
    no_red = False
    len_start = len(trans_board)

    # Move beads
    trans_board, moves = market.receive_unlimited(col, trans_board, no_red,
                                                  moves)
    extra, trans_board, moves = emerg.receive_beads(col, trans_board, no_red,
                                                    moves)
    if extra:
        trans_board, moves = unsheltered.receive_unlimited(extra, trans_board,
                                                           no_red, moves)
    len_end = len(trans_board)
    beads_moved = len_start - len_end

    # Save played board
    trans.board = pickle.dumps(trans_board)
    db.session.commit()
    return moves, beads_moved, no_red


def play_permanent(game, moves):
    # Load board
    perm = Permanent.query.filter_by(game_id=game.id).first()
    perm_board = pickle.loads(perm.board)
    no_red = False

    # Moves beads; different rules depending on even or odd round
    if game.round_count % 2 == 0:
        unsheltered = Unsheltered.query.filter_by(game_id=game.id).first()
        perm_board, moves = unsheltered.receive_unlimited(1, perm_board,
                                                          no_red, moves)
    else:
        market = Market.query.filter_by(game_id=game.id).first()
        perm_board, moves = market.receive_unlimited(1, perm_board, no_red,
                                                     moves)

    # Wrap up
    perm.board = pickle.dumps(perm_board)
    db.session.commit()
    # Transitional board only moves 1 bead per round
    return moves, 1, no_red


DISPATCHER_DEFAULT = {'Intake': play_intake, 'Emergency': play_emergency,
                      'Rapid': play_rapid, 'Outreach': play_outreach,
                      'Transitional': play_transitional,
                      'Permanent': play_permanent}
