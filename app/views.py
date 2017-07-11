import pickle
from flask import request, render_template, redirect, url_for, flash
from sqlalchemy import desc
from app import app, db
from .models import Game, Record, Log, Score
from .utils import BOARD_LIST, RECORDS_LIST, DISPATCHER_DEFAULT, load_counts


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
    counts = load_counts(game_id, RECORDS_LIST)
    decisions = load_decisions(game_id)
    score = Score.query.filter_by(game_id=game_id).first()
    return render_template('status.html', game=this_game,
                           board_list=board_list, boards=boards,
                           maxes=maxes, records=records,
                           counts=counts, decisions=decisions,
                           score=score)


@app.route('/view_log/<game_id>')
def view_log(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    moves_by_round = load_logs(game_id, this_game.round_count)
    return render_template('log.html',
                           BOARD_LIST=BOARD_LIST,
                           game=this_game,
                           moves_by_round=moves_by_round)


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
    game.verify_board_to_play(board_name)
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


def gen_progs_for_sys_event(board_list_pickle):
    board_list = pickle.loads(board_list_pickle)
    progs_list = board_list[:]
    progs_list.remove('Intake')
    progs_dict = {}
    for prog in progs_list:
        short_list = progs_list[:]
        short_list.remove(prog)
        progs_dict[prog] = short_list
    return progs_dict


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


def load_decisions(game_id):
    decisions = []
    records = Record.query.filter(Record.game_id == game_id,
                                  Record.note.isnot(None)
                                  ).order_by(desc(Record.id))
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


def end_round(game, board_list):
    # Update record and reset counters - for ALL boards, even not being played
    update_all_records(game.id, game.round_count, RECORDS_LIST)
    game.round_count += 1
    game.board_to_play = 0
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


# TODO: Major refactor!
# TODO: Add bar charts to show bead movement
# TODO: One-button run simulation version with side-by-side comparison
# TODO: integrate system_event as (disappearing) part of status page
# TODO: Something is STILL funky with validation of which board to play next
# TODO: Remove calc_end_count once it's clear all the math works
