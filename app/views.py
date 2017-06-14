import math
import pickle
from flask import request, render_template, redirect, url_for, flash
from sqlalchemy import and_
from app import app, db
from .utils import find_room, move_beads
from .models import Game, Emergency, Rapid, Transitional, Permanent, Score, Log

BOARD_LIST = ["Intake", "Emergency", "Rapid",
              "Outreach", "Transitional", "Permanent"]


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_game = Game()
        db.session.add(new_game)
        db.session.commit()
        new_Emergency = Emergency(game_id=new_game.id)
        db.session.add(new_Emergency)
        new_Rapid = Rapid(game_id=new_game.id)
        db.session.add(new_Rapid)
        new_Transitional = Transitional(game_id=new_game.id)
        db.session.add(new_Transitional)
        new_Permanent = Permanent(game_id=new_game.id)
        db.session.add(new_Permanent)
        new_Score = Score(game_id=new_game.id)
        db.session.add(new_Score)
        moves = []
        message = "Game " + str(new_game.id) + " initiated"
        moves.append(message)
        move_log = Log(new_game.id, 0, 0, moves)
        db.session.add(move_log)
        db.session.commit()
        return redirect(url_for('status', game_id=new_game.id))
    elif request.method == 'GET':
        recent_games = Game.query.order_by(Game.start_datetime.desc())
        return render_template('index.html', recent_games=recent_games)


@app.route('/status/<game_id>')
def status(game_id):
    # Pull info from Game table
    this_game = Game.query.get_or_404(int(game_id))
    intake_board = pickle.loads(this_game.intake)
    outreach_board = pickle.loads(this_game.outreach)
    market_board = pickle.loads(this_game.market)
    unsheltered_board = pickle.loads(this_game.unsheltered)

    # Pull info from other board tables
    this_emergency = Emergency.query.filter_by(game_id=game_id).first()
    emergency_board = pickle.loads(this_emergency.board)
    this_rapid = db.session.query(Rapid).filter_by(game_id=game_id).first()
    rapid_board = pickle.loads(this_rapid.board)
    this_transitional = Transitional.query.filter_by(game_id=game_id).first()
    transitional_board = pickle.loads(this_transitional.board)
    this_permanent = Permanent.query.filter_by(game_id=game_id).first()
    permanent_board = pickle.loads(this_permanent.board)

    # Pull info from Score table
    this_score = Score.query.filter_by(game_id=game_id).first()
    emergency_count = pickle.loads(this_score.emergency_count)
    transitional_count = pickle.loads(this_score.transitional_count)

    # Pull last move info from Log table
    # If beginning of entire game (before first load/play of Intake)
    if this_game.round_count == 0:
        this_log = Log.query.filter(and_(Log.game_id == game_id,
                                         Log.round_count == 0,
                                         Log.board_played == 0)
                                    ).order_by(Log.id).first()
    # After first play of Intake board (round_count == 1)
    elif this_game.board_to_play == 1 and this_game.round_count == 1:
        this_log = Log.query.filter(and_(Log.game_id == game_id,
                                         Log.round_count == 1,
                                         Log.board_played ==
                                         this_game.board_to_play - 1)
                                    ).order_by(Log.id).first()
    # After future plays of Intake board (round_count > 1)
    elif this_game.board_to_play == 1 and this_game.round_count > 1:
        this_log = Log.query.filter(and_(Log.game_id == game_id,
                                         Log.round_count ==
                                         this_game.round_count - 1,
                                         Log.board_played ==
                                         this_game.board_to_play - 1)
                                    ).order_by(Log.id).first()
    # After play of Permanent board
    elif this_game.board_to_play == 0:
        this_log = Log.query.filter(and_(Log.game_id == game_id,
                                         Log.round_count ==
                                         this_game.round_count,
                                         Log.board_played == 5)
                                    ).order_by(Log.id).first()
    else:
        this_log = Log.query.filter(and_(Log.game_id == game_id,
                                         Log.round_count ==
                                         this_game.round_count,
                                         Log.board_played ==
                                         this_game.board_to_play - 1)
                                    ).order_by(Log.id).first()
    last_moves = pickle.loads(this_log.moves)
    # Boards have to be passed individually because of unpickling
    return render_template('status.html',
                           game=this_game,
                           BOARD_LIST=BOARD_LIST,
                           intake=intake_board,
                           outreach=outreach_board,
                           market=market_board,
                           unsheltered=unsheltered_board,
                           emergency=emergency_board,
                           rapid=rapid_board,
                           transitional=transitional_board,
                           permanent=permanent_board,
                           emergency_count=emergency_count,
                           transitional_count=transitional_count,
                           last_moves=last_moves)


@app.route('/play_intake/<game_id>')
def play_intake(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    if BOARD_LIST[this_game.board_to_play] != 'Intake':
        flash('Time to play ' + BOARD_LIST[this_game.board_to_play] +
              ' board.', 'error')
    else:
        moves = []
        moves = this_game.load_intake(moves)

        # col = one 'column' in game instructions
        col = math.ceil(50 / this_game.intake_cols)
        intake = pickle.loads(this_game.intake)
        # If Diversion column is open
        if this_game.intake_cols == 6:
            message = "Diversion column being played"
            moves.append(message)
            intake, moves = this_game.send_to_market(col, intake, moves)
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        surplus, intake, moves = emergency.receive_beads(col, intake, moves)
        intake, moves = this_game.send_to_unsheltered(col, intake, moves)

        # Find room anywhere
        extra, intake, moves = emergency.receive_beads(len(intake), intake, moves)
        rapid = Rapid.query.filter_by(game_id=game_id).first()
        extra, intake, moves = rapid.receive_beads(extra, intake, moves)
        transitional = Transitional.query.filter_by(game_id=game_id).first()
        extra, intake, moves = transitional.receive_beads(extra, intake, moves)
        permanent = Permanent.query.filter_by(game_id=game_id).first()
        extra, intake, moves = permanent.receive_beads(extra, intake, moves)

        intake, moves = this_game.send_to_unsheltered(len(intake), intake, moves)
        this_game.intake = pickle.dumps(intake)

        move_log = Log(game_id, this_game.round_count,
                       this_game.board_to_play, moves)
        db.session.add(move_log)
        this_game.board_to_play += 1
        db.session.commit()
    return redirect(url_for('status', game_id=game_id))


# Something is wrong in this log
@app.route('/play_emergency/<game_id>')
def play_emergency(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    if BOARD_LIST[this_game.board_to_play] != 'Emergency':
        flash('Time to play ' + BOARD_LIST[this_game.board_to_play] +
              ' board.', 'error')
    else:
        moves = []
        # Emergency board = 5x5, so 1 col = 5; 1.5 col = 8
        col = math.ceil(1.5 * 5)
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        emerg_board = pickle.loads(emergency.board)
        emerg_board, moves = this_game.send_to_market(col, emerg_board, moves)
        emerg_board, moves = this_game.send_to_unsheltered(col, emerg_board, moves)
        # Send rest of Emergency Board wherever there is room
        extra = len(emerg_board)
        rapid = Rapid.query.filter_by(game_id=game_id).first()
        extra, emerg_board, moves = rapid.receive_beads(extra, emerg_board, moves)
        transitional = Transitional.query.filter_by(game_id=game_id).first()
        extra, emerg_board, moves = transitional.receive_beads(extra, emerg_board, moves)
        permanent = Permanent.query.filter_by(game_id=game_id).first()
        extra, emerg_board, moves = permanent.receive_beads(extra, emerg_board, moves)
        emerg_board, moves = this_game.send_to_unsheltered(extra, emerg_board, moves)
        emergency.board = pickle.dumps(emerg_board)

        move_log = Log(game_id, this_game.round_count,
                       this_game.board_to_play, moves)
        db.session.add(move_log)
        this_game.board_to_play += 1
        db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_rapid/<game_id>')
def play_rapid(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    if BOARD_LIST[this_game.board_to_play] != 'Rapid':
        flash('Time to play ' + BOARD_LIST[this_game.board_to_play] +
              ' board.', 'error')
    else:
        moves = []
        # Rapid board = 5x2, so 1 col = 2
        col = 2
        rapid = Rapid.query.filter_by(game_id=game_id).first()
        rapid_board = pickle.loads(rapid.board)
        rapid_board, moves = this_game.send_to_market(3 * col, rapid_board, moves)
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        extra, rapid_board, moves = emergency.receive_beads(col, rapid_board, moves)
        rapid.board = pickle.dumps(rapid_board)

        move_log = Log(game_id, this_game.round_count,
                       this_game.board_to_play, moves)
        db.session.add(move_log)
        this_game.board_to_play += 1
        db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_outreach/<game_id>')
def play_outreach(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    if BOARD_LIST[this_game.board_to_play] != 'Outreach':
        flash('Time to play ' + BOARD_LIST[this_game.board_to_play] +
              ' board.', 'error')
    else:
        moves = []
        outreach_board = pickle.loads(this_game.outreach)
        room = find_room(this_game.outreach_max, outreach_board)
        unsheltered_board = pickle.loads(this_game.unsheltered)
        unsheltered_board, outreach_board = move_beads(room, unsheltered_board, outreach_board)
        message = str(room) + " beads to outreach"
        moves.append(message)

        # Send rest of Outreach Board wherever there is room
        extra = len(outreach_board)
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        extra, outreach_board, moves = emergency.receive_beads(extra, outreach_board, moves)
        rapid = Rapid.query.filter_by(game_id=game_id).first()
        extra, outreach_board, moves = rapid.receive_beads(extra, outreach_board, moves)
        trans = Transitional.query.filter_by(game_id=game_id).first()
        extra, outreach_board, moves = trans.receive_beads(extra, outreach_board, moves)
        permanent = Permanent.query.filter_by(game_id=game_id).first()
        extra, outreach_board, moves = permanent.receive_beads(extra, outreach_board, moves)
        outreach_board, moves = this_game.send_to_unsheltered(extra, outreach_board, moves)
        this_game.outreach = pickle.dumps(outreach_board)

        move_log = Log(game_id, this_game.round_count,
                       this_game.board_to_play, moves)
        db.session.add(move_log)
        this_game.board_to_play += 1
        db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_transitional/<game_id>')
def play_transitional(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    if BOARD_LIST[this_game.board_to_play] != 'Transitional':
        flash('Time to play ' + BOARD_LIST[this_game.board_to_play] +
              ' board.', 'error')
    else:
        moves = []
        # Transitional board = 5x4, so 1 col = 4
        col = 4
        trans = Transitional.query.filter_by(game_id=game_id).first()
        trans_board = pickle.loads(trans.board)
        trans_board, moves = this_game.send_to_market(col, trans_board, moves)
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        extra, trans_board, moves = emergency.receive_beads(col, trans_board, moves)
        if extra:
            trans_board, moves = this_game.send_to_unsheltered(extra, trans_board, moves)
        trans.board = pickle.dumps(trans_board)

        move_log = Log(game_id, this_game.round_count,
                       this_game.board_to_play, moves)
        db.session.add(move_log)
        this_game.board_to_play += 1
        db.session.commit()
    return redirect(url_for('status', game_id=game_id))


# TEMP comment: round rules implemented
@app.route('/play_permanent/<game_id>')
def play_permanent(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    if BOARD_LIST[this_game.board_to_play] != 'Permanent':
        flash('Time to play ' + BOARD_LIST[this_game.board_to_play] +
              ' board.', 'error')
    else:
        moves = []
        permanent = Permanent.query.filter_by(game_id=game_id).first()
        permanent_board = pickle.loads(permanent.board)
        # if even round
        if this_game.round_count % 2 == 0:
            permanent_board, moves = this_game.send_to_unsheltered(1, permanent_board, moves)
        else:
            permanent_board, moves = this_game.send_to_market(1, permanent_board, moves)
        permanent.board = pickle.dumps(permanent_board)

        # This ends round - time to score
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        emerg_count = len(pickle.loads(emergency.board))
        trans = Transitional.query.filter_by(game_id=game_id).first()
        trans_count = len(pickle.loads(trans.board))
        this_score = Score.query.filter_by(game_id=game_id).first()
        this_score.add_score(emerg_count, trans_count)

        move_log = Log(game_id, this_game.round_count,
                       this_game.board_to_play, moves)
        db.session.add(move_log)
        this_game.board_to_play = 0
        db.session.commit()
    return redirect(url_for('system_event', game_id=game_id))


@app.route('/system_event/<game_id>', methods=['GET', 'POST'])
def system_event(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    if request.method == 'POST':
        moves = []
        if this_game.round_count == 1:
            program = request.form.get('program')
            moves = this_game.open_new(program, moves)
        elif this_game.round_count == 2 or this_game.round_count == 3:
            from_program = request.form.get('from_program')
            to_program = request.form.get('to_program')
            print('from_program is ' + str(from_program))
            print('to_program is ' + str(to_program))
            moves = this_game.convert_program(from_program, to_program, moves)

        # Set "board_to_play == 5" for sake of log
        move_log = Log(game_id, this_game.round_count, 5, moves)
        db.session.add(move_log)
        db.session.commit()
        return redirect(url_for('status', game_id=game_id))
    elif request.method == 'GET':
        # Time to calculate Final Score
        if this_game.round_count == 5:
            this_score = Score.query.filter_by(game_id=game_id).first()
            this_score.calculate_final_score()
        return render_template('event.html', game=this_game, score=this_score)

# TODO: move board_count +1 to end of previous round
# TODO: add game logic for board conversion
# TODO: diff rules in rounds!
# TODO: add check for while extra > 0
# TODO: randomize order in lists
# TODO: randomize 'place anywhere' board order
