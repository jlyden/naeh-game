import math
import pickle
from flask import request, render_template, redirect, url_for
from sqlalchemy import desc
from app import app, db
from .models import Game, Emergency, Rapid, Transitional, Permanent, Score, Log
from .utils import find_room, move_beads, BOARD_LIST


@app.route('/', methods=['GET', 'POST'])
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
        move_log = Log(new_game.id, 1, 0, moves)
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
    m_counts = pickle.loads(this_game.market_record)
    unsheltered_board = pickle.loads(this_game.unsheltered)
    u_counts = pickle.loads(this_game.unsheltered_record)

    # Pull info from other board tables
    this_emergency = Emergency.query.filter_by(game_id=game_id).first()
    emergency_board = pickle.loads(this_emergency.board)
    e_counts = pickle.loads(this_emergency.record)
    this_rapid = db.session.query(Rapid).filter_by(game_id=game_id).first()
    rapid_board = pickle.loads(this_rapid.board)
    r_counts = pickle.loads(this_rapid.record)
    this_transitional = Transitional.query.filter_by(game_id=game_id).first()
    transitional_board = pickle.loads(this_transitional.board)
    t_counts = pickle.loads(this_transitional.record)
    this_permanent = Permanent.query.filter_by(game_id=game_id).first()
    permanent_board = pickle.loads(this_permanent.board)
    p_counts = pickle.loads(this_permanent.record)

    # Pull last move info from Log table
    this_log = Log.query.filter(Log.game_id == game_id).order_by(desc(Log.id)).first();
    last_moves = pickle.loads(this_log.moves)
    # Boards have to be passed individually because of unpickling
    return render_template('status.html',
                           BOARD_LIST=BOARD_LIST,
                           game=this_game,
                           intake=intake_board,
                           outreach=outreach_board,
                           market=market_board,
                           unsheltered=unsheltered_board,
                           emergency=emergency_board,
                           rapid=rapid_board,
                           transitional=transitional_board,
                           permanent=permanent_board,
                           m_counts=m_counts,
                           u_counts=u_counts,
                           e_counts=e_counts,
                           r_counts=r_counts,
                           t_counts=t_counts,
                           p_counts=p_counts,
                           last_moves=last_moves)


@app.route('/view_log/<game_id>')
def view_log(game_id):
    # Pull info from Game and Log table
    this_game = Game.query.get_or_404(int(game_id))
    this_game_logs = Log.query.filter(Log.game_id == game_id).order_by(Log.id);
    all_moves = []
    for log in this_game_logs:
        last_moves = pickle.loads(log.moves)
        all_moves.extend(last_moves)
    return render_template('log.html', game=this_game, moves=all_moves)


@app.route('/play_round/<game_id>')
def play_round(game_id):
    play_intake(game_id)
    play_emergency(game_id)
    play_rapid(game_id)
    play_outreach(game_id)
    play_transitional(game_id)
    play_permanent(game_id)
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_intake/<game_id>')
def play_intake(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    this_game.verify_board_to_play('Intake')
    print("Playing Intake Board")
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
    # surplus doesn't matter, b/c len(intake) will be passed later
    surplus, intake, moves = emergency.receive_beads(col, intake, moves)
    intake, moves = this_game.send_to_unsheltered(col, intake, moves)
    intake, moves = this_game.send_anywhere(len(intake), intake, moves)
    this_game.intake = pickle.dumps(intake)
    move_log = Log(game_id, this_game.round_count, this_game.board_to_play, moves)
    db.session.add(move_log)
    this_game.board_to_play += 1
    print("next board to play is " + str(this_game.board_to_play))
    db.session.commit()
    return redirect(url_for('status', game_id=game_id))


# TODO: Something is wrong in this log
@app.route('/play_emergency/<game_id>')
def play_emergency(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    this_game.verify_board_to_play('Emergency')
    print("Playing Emergency Board")
    moves = []
    # Emergency board = 5x5, so 1 col = 5; 1.5 col = 8
    col = math.ceil(1.5 * 5)
    emergency = Emergency.query.filter_by(game_id=game_id).first()
    emerg_board = pickle.loads(emergency.board)
    emerg_board, moves = this_game.send_to_market(col, emerg_board, moves)
    emerg_board, moves = this_game.send_to_unsheltered(col, emerg_board, moves)
    # Send rest of Emergency Board wherever there is room
    emerg_board, moves = this_game.send_anywhere(len(emerg_board), emerg_board, moves)
    emergency.board = pickle.dumps(emerg_board)
    move_log = Log(game_id, this_game.round_count,
                   this_game.board_to_play, moves)
    db.session.add(move_log)
    this_game.board_to_play += 1
    print("next board to play is " + str(this_game.board_to_play))
    db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_rapid/<game_id>')
def play_rapid(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    this_game.verify_board_to_play('Rapid')
    print("Playing Rapid Board")
    moves = []
    # Rapid board = 5x2, so 1 col = 2
    col = 2
    rapid = Rapid.query.filter_by(game_id=game_id).first()
    rapid_board = pickle.loads(rapid.board)
    rapid_board, moves = this_game.send_to_market(3 * col, rapid_board, moves)
    emergency = Emergency.query.filter_by(game_id=game_id).first()
    extra, rapid_board, moves = emergency.receive_beads(col, rapid_board, moves)
    rapid.board = pickle.dumps(rapid_board)

    move_log = Log(game_id, this_game.round_count, this_game.board_to_play, moves)
    db.session.add(move_log)
    this_game.board_to_play += 1
    print("next board to play is " + str(this_game.board_to_play))
    db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_outreach/<game_id>')
def play_outreach(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    this_game.verify_board_to_play('Outreach')
    print("Playing Outreach Board")
    moves = []
    this_unsheltered = pickle.loads(this_game.unsheltered)
    room = find_room(this_game.outreach_max, this_game.outreach)
    this_unsheltered, this_game.outreach = move_beads(room, this_unsheltered, this_game.outreach)
    this_game.unsheltered = pickle.dumps(this_unsheltered)
    message = str(room) + " beads to outreach"
    moves.append(message)
    outreach_board = pickle.loads(this_game.outreach)
    outreach_board, moves = this_game.send_anywhere(len(outreach_board), outreach_board, moves)
    this_game.outreach = pickle.dumps(outreach_board)
    move_log = Log(game_id, this_game.round_count,
                   this_game.board_to_play, moves)
    db.session.add(move_log)
    this_game.board_to_play += 1
    print("next board to play is " + str(this_game.board_to_play))
    db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_transitional/<game_id>')
def play_transitional(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    this_game.verify_board_to_play('Transitional')
    print("Playing Transitional Board")
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
    print("next board to play is " + str(this_game.board_to_play))
    db.session.commit()
    return redirect(url_for('status', game_id=game_id))


# TEMP comment: round rules implemented
@app.route('/play_permanent/<game_id>')
def play_permanent(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    this_game.verify_board_to_play('Permanent')
    print("Playing Permanent Board")
    moves = []
    permanent = Permanent.query.filter_by(game_id=game_id).first()
    permanent_board = pickle.loads(permanent.board)
    # if even round
    if this_game.round_count % 2 == 0:
        permanent_board, moves = this_game.send_to_unsheltered(1, permanent_board, moves)
    else:
        permanent_board, moves = this_game.send_to_market(1, permanent_board, moves)
    permanent.board = pickle.dumps(permanent_board)
    move_log = Log(game_id, this_game.round_count,
                   this_game.board_to_play, moves)
    db.session.add(move_log)
    # Update record and reset counters
    this_game.update_records()
    this_game.round_count += 1
    this_game.board_to_play = 0
    print("next board to play is " + str(this_game.board_to_play))
    db.session.commit()
    return redirect(url_for('system_event', game_id=game_id))


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
    elif request.method == 'GET':
        # Time to calculate Final Score
        if this_game.round_count == 6:
            this_score = Score.query.filter_by(game_id=game_id).first()
            this_score.calculate_final_score()
            return render_template('event.html', game=this_game, score=this_score)
        else:
            return render_template('event.html', game=this_game)

# TODO: Something is funky with validation of which board to play next
# TODO: fold creation of other boards into game init?
# TODO: gameplay where you make pre-round choices, then play entire round with 1 click
# TODO: add check for round six - no more playing - maybe disappear play buttons
# TODO: add game logic for board conversion
# TODO: diff rules in rounds!
# TODO: change "round 6" to "game over" somehow
# TODO: add check for while extra > 0 - maybe accomplished by send_anywhere?
# TODO: randomize order in lists (for red beads)
# TODO: Add charts and major game choices to score board
