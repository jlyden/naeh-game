import pickle
from flask import request, render_template, redirect, url_for, flash
from sqlalchemy import desc
from app import app, db
from .models.game import Game
from .models.score import Record, Log, Score
from .utils.boardplay import DISPATCHER_DEFAULT
from .utils.lists import BOARD_LIST, RECORDS_LIST
from .utils.misc import gen_progs_for_sys_event
from .utils.recordkeeping import end_round
from .utils.statusloads import load_boards_and_maxes, load_counts_and_changes
from .utils.statusloads import load_decisions, load_logs, load_records


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
    this_game = Game.query.get_or_404(int(game_id))
    board_list = pickle.loads(this_game.board_list_pickle)
    boards, maxes = load_boards_and_maxes(game_id, board_list, RECORDS_LIST)
    records = load_records(game_id, board_list)
    counts, changes = load_counts_and_changes(game_id, RECORDS_LIST)
    decisions = load_decisions(game_id)
    score = Score.query.filter_by(game_id=game_id).first()
    return render_template('status.html', game=this_game,
                           board_list=board_list, boards=boards,
                           maxes=maxes, records=records,
                           counts=counts, changes=changes,
                           decisions=decisions, score=score)


@app.route('/view_log/<game_id>')
def view_log(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    moves_by_round = load_logs(game_id, this_game.round_count)
    return render_template('log.html',
                           BOARD_LIST=BOARD_LIST,
                           game=this_game,
                           moves_by_round=moves_by_round)


@app.route('/animated/<game_id>')
def animated(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    return render_template('animated.html', game=this_game)


@app.route('/play_round/<game_id>')
def play_round(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    if this_game.round_count < 6:
        board_list = pickle.loads(this_game.board_list_pickle)
        for board_name in board_list:
            play_board(board_name, game_id)
        return redirect(url_for('system_event', game_id=game_id))
    else:
        flash(u'Game over - no more plays.', 'warning')
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_board/<board_name>/<game_id>')
def play_board(board_name, game_id):
    # Set up
    game = Game.query.get_or_404(int(game_id))
    print("Playing " + str(game.board_to_play) + ", " + board_name)
    moves = []

    # Play the board specified
    moves, beads_moved, no_red = DISPATCHER_DEFAULT[board_name](game, moves)

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
            return render_template('event.html', game=this_game, programs={})
        else:
            programs = gen_progs_for_sys_event(this_game.board_list_pickle)
            return render_template('event.html', game=this_game,
                                   programs=programs)


# TODO: integrate system_event as (disappearing) part of status page
# TODO: One-button run simulation version with side-by-side comparison
# TODO: add animation
# TODO: add informative details (definitions of boards, etc)
