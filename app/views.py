import math
import pickle
from flask import request, render_template, redirect, url_for, flash
from sqlalchemy import desc
from app import app, db
from .models import Game, Emergency, Rapid, Outreach, Transitional, Permanent
from .models import Unsheltered, Market, Record, Log, Score
from .models import BOARD_LIST, load_counts


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        new_game = Game.create()
        return redirect(url_for('status', game_id=new_game.id))
    elif request.method == 'GET':
        recent_games = Game.query.order_by(Game.start_datetime.desc())
        return render_template('home.html', recent_games=recent_games)


@app.route('/status/<game_id>')
def status(game_id):
    # Grab info from db
    this_game = Game.query.get_or_404(int(game_id))
    board_list = pickle.loads(this_game.board_list_pickle)
    expanded_list = expand_board_list(board_list)
    boards = load_boards(game_id, expanded_list)
    records = load_records(game_id, expanded_list)
    counts = load_counts(game_id, expanded_list)
    return render_template('status.html', game=this_game,
                           board_list=board_list, boards=boards,
                           records=records, counts=counts)


@app.route('/view_log/<game_id>')
def view_log(game_id):
    # Pull info from Game and Log table
    this_game = Game.query.get_or_404(int(game_id))
    moves_by_round = []
    for i in range(1, 6):
        round_logs = Log.query.filter(Log.game_id == game_id,
                                      Log.round_count == i).order_by(Log.id)
        logs = []
        for log in round_logs:
            last_moves = pickle.loads(log.moves)
            logs.append(last_moves)
        moves_by_round.append(logs)
    return render_template('log.html',
                           BOARD_LIST=BOARD_LIST,
                           game=this_game,
                           moves_by_round=moves_by_round)


@app.route('/play_round/<game_id>')
def play_round(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    if this_game.round_count < 6:
        board_list = pickle.loads(this_game.board_list_pickle)
        for board in board_list:
            play_board(board, game_id)
        return redirect(url_for('system_event', game_id=game_id))
    else:
        flash(u'Game over - no more plays.', 'warning')
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_board/<board_name>/<game_id>')
def play_board(board_name, game_id):
    # Set up
    game = Game.query.get_or_404(int(game_id))
    game.verify_board_to_play(board_name)
    print("Playing " + str(game.board_to_play) + ", " + board_name)
    moves = []

    # Play the board specified
    moves, beads_moved = DISPATCHER_DEFAULT[board_name](game, moves)

    # Wrap up
    if board_name != 'Intake':
        record = Record.query.filter(Record.game_id == game_id,
                                     Record.board_name == board_name,
                                     ).order_by(desc(Record.id)).first()
        print("play_board found " + str(record))
        record.record_change_beads('out', beads_moved)
    move_log = Log(game_id, game.round_count, board_name, moves)
    db.session.add(move_log)
    game.board_to_play += 1

    # If board list is exhausted ...
    board_list = pickle.loads(game.board_list_pickle)
    if game.board_to_play > len(board_list) - 1:
        end_round(game, board_list)
        return redirect(url_for('system_event', game_id=game_id))

    db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/system_event/<game_id>', methods=['GET', 'POST'])
def system_event(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    if request.method == 'POST':
        print("Executing System Event")
        moves = []
        if this_game.round_count == 2:
            program = request.form.get('program')
            moves = this_game.open_new(program, moves)
        elif this_game.round_count == 3 or this_game.round_count == 4:
            from_program = request.form.get('from_program')
            to_program = request.form.get('to_program')
            print('from_program is ' + str(from_program))
            print('to_program is ' + str(to_program))
            moves = this_game.convert_program(from_program, to_program, moves)

        # Set "board_played == 6" for sake of log
        move_log = Log(game_id, this_game.round_count, 6, moves)
        db.session.add(move_log)
        db.session.commit()
        return redirect(url_for('status', game_id=game_id))
    else:
        # Time to calculate Final Score
        if this_game.round_count == 6:
            this_game.calculate_final_score()
            this_score = Score.query.filter_by(game_id=game_id).first()
            return render_template('event.html', game=this_game,
                                   score=this_score)
        else:
            return render_template('event.html', game=this_game)


def play_intake(game, moves):
    intiate_records(game)
    # Load boards
    intake, moves = game.load_intake(moves)
    unsheltered = Unsheltered.query.filter_by(game_id=game.id).first()
    market = Market.query.filter_by(game_id=game.id).first()
    emerg = Emergency.query.filter_by(game_id=game.id).first()
    # col = one 'column' in game instructions
    col = math.ceil(50 / game.intake_cols)

    # Move beads
    # If Diversion column is open
    if game.intake_cols == 6:
        message = "Diversion column being played"
        moves.append(message)
        intake, moves = market.receive_unlimited(col, intake, moves)
    surplus, intake, moves = emerg.receive_beads(col, intake, moves)
    intake, moves = unsheltered.receive_unlimited(col, intake, moves)
    intake, moves = game.send_anywhere(len(intake), intake, moves)
    # Intake always ends at 0, and can't receive, so not saved
    beads_moved = 50
    return moves, beads_moved


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

    # Move beads
    emerg_board, moves = market.receive_unlimited(col, emerg_board, moves)
    emerg_board, moves = unsheltered.receive_unlimited(col, emerg_board, moves)
    if len(emerg_board) > 0:
        emerg_board, moves = game.send_anywhere(len(emerg_board), emerg_board,
                                                moves)

    # Save played board
    emerg.board = pickle.dumps(emerg_board)
    db.session.commit()
    return moves, beads_moved


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

    # Move beads
    rapid_board, moves = market.receive_unlimited(3 * col, rapid_board, moves)
    extra, rapid_board, moves = emerg.receive_beads(col, rapid_board, moves)
    len_end = len(rapid_board)
    beads_moved = len_start - len_end

    # Save played board
    rapid.board = pickle.dumps(rapid_board)
    db.session.commit()
    return moves, beads_moved


def play_outreach(game, moves):
    # Load boards
    unsheltered = Unsheltered.query.filter_by(game_id=game.id).first()
    unsheltered_board = pickle.loads(unsheltered.board)
    outreach = Outreach.query.filter_by(game_id=game.id).first()

    # Move beads TO outreach
    unsheltered_board, outreach_board, moves = \
        outreach.fill_from(unsheltered_board, moves)
    unsheltered.board = pickle.dumps(unsheltered_board)
    # Move beads FROM Outreach
    outreach_board, moves = game.send_anywhere(len(outreach_board),
                                               outreach_board, moves)

    # Save played board
    outreach.board = pickle.dumps(outreach_board)
    db.session.commit()
    # Outreach is filled to 10 and emptied each round
    return moves, 10


def play_transitional(game, moves):
    # Load boards
    trans = Transitional.query.filter_by(game_id=game.id).first()
    trans_board = pickle.loads(trans.board)
    market = Market.query.filter_by(game_id=game.id).first()
    emerg = Emergency.query.filter_by(game_id=game.id).first()
    unsheltered = Unsheltered.query.filter_by(game_id=game.id).first()
    # Each board has 5 columns
    col = math.ceil(trans.maximum / 5)
    len_start = len(trans_board)

    # Move beads
    trans_board, moves = market.receive_unlimited(col, trans_board, moves)
    extra, trans_board, moves = emerg.receive_beads(col, trans_board, moves)
    if extra:
        trans_board, moves = unsheltered.receive_unlimited(extra, trans_board,
                                                           moves)
    len_end = len(trans_board)
    beads_moved = len_start - len_end

    # Save played board
    trans.board = pickle.dumps(trans_board)
    db.session.commit()
    return moves, beads_moved


# TEMP comment: round rules implemented
def play_permanent(game, moves):
    # Load board
    perm = Permanent.query.filter_by(game_id=game.id).first()
    perm_board = pickle.loads(perm.board)

    # Moves beads; different rules depending on even or odd round
    if game.round_count % 2 == 0:
        unsheltered = Unsheltered.query.filter_by(game_id=game.id).first()
        perm_board, moves = unsheltered.receive_unlimited(1, perm_board, moves)
    else:
        market = Market.query.filter_by(game_id=game.id).first()
        perm_board, moves = market.receive_unlimited(1, perm_board, moves)

    # Wrap up
    perm.board = pickle.dumps(perm_board)
    db.session.commit()
    # Transitional board only moves 1 bead per round
    return moves, 1


def load_boards(game_id, expanded_list):
    boards = {}
    for board in expanded_list:
        prog_table = eval(board)
        prog = prog_table.query.filter_by(game_id=game_id).first()
        prog_board = pickle.loads(prog.board)
        boards[board] = prog_board
    return boards


def load_records(game_id, expanded_list):
    records = []
    for board in expanded_list:
        # This order_by gives us last record per board
        record = Record.query.filter(Record.game_id == game_id,
                                     Record.board_name == board
                                     ).order_by(desc(Record.id)).first()
        records.append(record)
    return records


def intiate_records(game):
    board_list = pickle.loads(game.board_list_pickle)
    for board in board_list:
        if board != "Intake":
            record = Record(game_id=game.id,
                            round_count=game.round_count,
                            board_name=board)
            db.session.add(record)
            db.session.commit()
    return


def end_round(game, board_list):
    # Update record and reset counters
    update_all_records(game.id, game.round_count, board_list)
    game.round_count += 1
    game.board_to_play = 0
    db.session.commit()
    return


def expand_board_list(board_list):
    expanded_board_list = board_list[:]
    expanded_board_list.remove('Intake')
    expanded_board_list.append('Unsheltered')
    expanded_board_list.append('Market')
    return expanded_board_list


def update_all_records(game_id, round_count, board_list):
    expanded_list = expand_board_list(board_list)
    for board in expanded_list:
        record = Record.query.filter(Record.game_id == game_id,
                                     Record.board_name == board,
                                     Record.round_count == round_count
                                     ).order_by(desc(Record.id)).first()
        if record is None:
            # initiate record for current round
            record = Record(game_id=game_id,
                            round_count=round_count,
                            board_name=board)
            prog_table = eval(board)
            prog = prog_table.query.filter_by(game_id=game_id).first()
            prog_board = pickle.loads(prog.board)
            record.beads_in = len(prog_board)
            record.end_count = len(prog_board)
            db.session.add(record)
            print("Added NEW end_count record for " + board + ": " +
                  str(record.end_count))
        else:
            print("update_all_records found " + str(record))
            record.end_count = record.calc_end_count()
            print("Updated end_count record for " + board + ": " +
                  str(record.end_count))
        db.session.commit()
    return


DISPATCHER_DEFAULT = {'Intake': play_intake, 'Emergency': play_emergency,
                      'Rapid': play_rapid, 'Outreach': play_outreach,
                      'Transitional': play_transitional,
                      'Permanent': play_permanent}


# TODO: add records in system events with notes! (and calculations)
# TODO: ALWAYS add records for boards involved in scoring (even with 0000)
# TODO: diff rules in rounds!
# TODO: Add charts and major game choices to score board
# TODO: Something is STILL funky with validation of which board to play next

# TODO: Once we're back to functionality - try removing __init__ methods
# TODO: integrate system_event as (disappearing) part of status page
#  - https://stackoverflow.com/questions/1976651/multiple-level-template-inheritance-in-jinja2

# TODO: randomize order in lists (for red beads)
