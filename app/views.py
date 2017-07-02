import math
import pickle
from flask import request, render_template, redirect, url_for, flash
from sqlalchemy import desc
from app import app, db
from .models import Game, Emergency, Rapid, Outreach, Transitional, Permanent
from .models import Unsheltered, Market, Score, Log, BOARD_LIST


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
    this_emerg = Emergency.query.filter_by(game_id=game_id).first()
    emerg_board = pickle.loads(this_emerg.board)
    e_counts = pickle.loads(this_emerg.record)
    this_rapid = db.session.query(Rapid).filter_by(game_id=game_id).first()
    rapid_board = pickle.loads(this_rapid.board)
    r_counts = pickle.loads(this_rapid.record)
    this_outreach = Outreach.query.filter_by(game_id=game_id).first()
    outreach_board = pickle.loads(this_outreach.board)
    this_trans = Transitional.query.filter_by(game_id=game_id).first()
    trans_board = pickle.loads(this_trans.board)
    t_counts = pickle.loads(this_trans.record)
    this_perm = Permanent.query.filter_by(game_id=game_id).first()
    perm_board = pickle.loads(this_perm.board)
    p_counts = pickle.loads(this_perm.record)
    this_unsheltered = Unsheltered.query.filter_by(game_id=game_id).first()
    unsheltered_board = pickle.loads(this_unsheltered.board)
    u_counts = pickle.loads(this_unsheltered.record)
    this_market = Market.query.filter_by(game_id=game_id).first()
    market_board = pickle.loads(this_market.board)
    m_counts = pickle.loads(this_market.record)
    # Pull last move info from Log table
    this_log = Log.query.filter(Log.game_id == game_id).order_by(desc(Log.id)
                                                                 ).first()
    last_moves = pickle.loads(this_log.moves)
    # Boards have to be passed individually because of unpickling
    return render_template('status.html',
                           BOARD_LIST=BOARD_LIST,
                           game=this_game, last_moves=last_moves,
                           emerg=emerg_board, e_counts=e_counts,
                           rapid=rapid_board, r_counts=r_counts,
                           outreach=outreach_board,
                           trans=trans_board, t_counts=t_counts,
                           perm=perm_board, p_counts=p_counts,
                           unsheltered=unsheltered_board, u_counts=u_counts,
                           market=market_board, m_counts=m_counts)


@app.route('/view_log/<game_id>')
def view_log(game_id):
    # Pull info from Game and Log table
    this_game = Game.query.get_or_404(int(game_id))
    this_game_logs = Log.query.filter(Log.game_id == game_id).order_by(Log.id)
    rnd1_moves = []
    rnd2_moves = []
    rnd3_moves = []
    rnd4_moves = []
    rnd5_moves = []
    for log in this_game_logs:
        last_moves = pickle.loads(log.moves)
        if log.round_count == 1:
            rnd1_moves.extend(last_moves)
        if log.round_count == 2:
            rnd2_moves.extend(last_moves)
        if log.round_count == 3:
            rnd3_moves.extend(last_moves)
        if log.round_count == 4:
            rnd4_moves.extend(last_moves)
        if log.round_count == 5:
            rnd5_moves.extend(last_moves)
    return render_template('log.html',
                           BOARD_LIST=BOARD_LIST,
                           game=this_game,
                           rnd1_moves=rnd1_moves,
                           rnd2_moves=rnd2_moves,
                           rnd3_moves=rnd3_moves,
                           rnd4_moves=rnd4_moves,
                           rnd5_moves=rnd5_moves)


@app.route('/play_round/<game_id>')
def play_round(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    if this_game.round_count < 6:
        for program in DISPATCHER_DEFAULT:
            DISPATCHER_DEFAULT[program](game_id)
        system_event(game_id)
    else:
        flash(u'Game over - no more plays.', 'warning')
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_intake/<game_id>')
def play_intake(game_id):
    # Set up
    this_game = Game.query.get_or_404(int(game_id))
    this_game.verify_board_to_play('Intake')
    print("Playing Intake Board")
    # col = one 'column' in game instructions
    col = math.ceil(50 / this_game.intake_cols)
    moves = []

    # Load boards
    intake_board, moves = this_game.load_intake(moves)
    this_unsheltered = Unsheltered.query.filter_by(game_id=game_id).first()
    this_market = Market.query.filter_by(game_id=game_id).first()
    this_emerg = Emergency.query.filter_by(game_id=game_id).first()

    # Move beads
    # If Diversion column is open
    if this_game.intake_cols == 6:
        message = "Diversion column being played"
        moves.append(message)
        intake_board, moves = this_market.receive_unlimited(col, intake_board,
                                                            moves)
    # surplus doesn't matter, b/c len(intake) will be passed later
    surplus, intake_board, moves = this_emerg.receive_beads(col, intake_board,
                                                            moves)
    intake_board, moves = this_unsheltered.receive_unlimited(col, intake_board,
                                                             moves)
    intake_board, moves = this_game.send_anywhere(len(intake_board),
                                                  intake_board, moves)

    # Wrap up
    move_log = Log(game_id, this_game.round_count,
                   this_game.board_to_play, moves)
    db.session.add(move_log)
    this_game.board_to_play += 1
    print("next board to play is " + str(this_game.board_to_play))
    db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_emerg/<game_id>')
def play_emergency(game_id):
    # Set up
    this_game = Game.query.get_or_404(int(game_id))
    this_game.verify_board_to_play('Emergency')
    print("Playing Emergency Board")
    moves = []

    # Load boards
    emerg = Emergency.query.filter_by(game_id=game_id).first()
    emerg_board = pickle.loads(emerg.board)
    this_unsheltered = Unsheltered.query.filter_by(game_id=game_id).first()
    this_market = Market.query.filter_by(game_id=game_id).first()
    # Each board has 5 columns - instructions say to move 1.5 cols in emergency
    col = math.ceil(1.5 * (emerg.maximum / 5))

    # Move beads
    emerg_board, moves = this_market.receive_unlimited(col, emerg_board, moves)
    emerg_board, moves = this_unsheltered.receive_unlimited(col, emerg_board,
                                                            moves)
    if len(emerg_board) > 0:
        emerg_board, moves = this_game.send_anywhere(len(emerg_board),
                                                     emerg_board, moves)

    # Wrap up
    emerg.board = pickle.dumps(emerg_board)
    move_log = Log(game_id, this_game.round_count,
                   this_game.board_to_play, moves)
    db.session.add(move_log)
    this_game.board_to_play += 1
    print("next board to play is " + str(this_game.board_to_play))
    db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_rapid/<game_id>')
def play_rapid(game_id):
    # Set up
    this_game = Game.query.get_or_404(int(game_id))
    this_game.verify_board_to_play('Rapid')
    print("Playing Rapid Board")
    moves = []

    # Load boards
    rapid = Rapid.query.filter_by(game_id=game_id).first()
    rapid_board = pickle.loads(rapid.board)
    this_market = Market.query.filter_by(game_id=game_id).first()
    this_emerg = Emergency.query.filter_by(game_id=game_id).first()
    # Each board has 5 columns
    col = math.ceil(rapid.maximum / 5)

    rapid_board, moves = this_market.receive_unlimited(3 * col, rapid_board,
                                                       moves)
    extra, rapid_board, moves = this_emerg.receive_beads(col, rapid_board,
                                                         moves)
    # Wrap up
    rapid.board = pickle.dumps(rapid_board)
    move_log = Log(game_id, this_game.round_count,
                   this_game.board_to_play, moves)
    db.session.add(move_log)
    this_game.board_to_play += 1
    print("next board to play is " + str(this_game.board_to_play))
    db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_outreach/<game_id>')
def play_outreach(game_id):
    # Set up
    this_game = Game.query.get_or_404(int(game_id))
    this_game.verify_board_to_play('Outreach')
    print("Playing Outreach Board")
    moves = []

    # Load boards, moves beads INTO outreach
    this_unsheltered = Unsheltered.query.filter_by(game_id=game_id).first()
    unsheltered_board = pickle.loads(this_unsheltered.board)
    this_outreach = Outreach.query.filter_by(game_id=game_id).first()
    unsheltered_board, outreach_board, moves = this_outreach.fill_from(unsheltered_board, moves)
    this_unsheltered.board = pickle.dumps(unsheltered_board)

    # Move beads FROM Outreach
    outreach_board, moves = this_game.send_anywhere(len(outreach_board),
                                                    outreach_board, moves)

    # Wrap up
    this_outreach.board = pickle.dumps(outreach_board)
    move_log = Log(game_id, this_game.round_count,
                   this_game.board_to_play, moves)
    db.session.add(move_log)
    this_game.board_to_play += 1
    print("next board to play is " + str(this_game.board_to_play))
    db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_trans/<game_id>')
def play_transitional(game_id):
    # Set up
    this_game = Game.query.get_or_404(int(game_id))
    this_game.verify_board_to_play('Transitional')
    print("Playing Transitional Board")
    # Transitional board = 5x4, so 1 col = 4
    col = 4
    moves = []

    # Load boards
    trans = Transitional.query.filter_by(game_id=game_id).first()
    trans_board = pickle.loads(trans.board)
    this_market = Market.query.filter_by(game_id=game_id).first()
    this_emerg = Emergency.query.filter_by(game_id=game_id).first()
    this_unsheltered = Unsheltered.query.filter_by(game_id=game_id).first()
    # Each board has 5 columns
    col = math.ceil(trans.maximum / 5)

    # Move beads
    trans_board, moves = this_market.receive_unlimited(col, trans_board, moves)
    extra, trans_board, moves = this_emerg.receive_beads(col, trans_board,
                                                         moves)
    if extra:
        trans_board, moves = this_unsheltered.receive_unlimited(extra,
                                                                trans_board,
                                                                moves)
    # Wrap up
    trans.board = pickle.dumps(trans_board)
    move_log = Log(game_id, this_game.round_count,
                   this_game.board_to_play, moves)
    db.session.add(move_log)
    this_game.board_to_play += 1
    print("next board to play is " + str(this_game.board_to_play))
    db.session.commit()
    return redirect(url_for('status', game_id=game_id))


# TEMP comment: round rules implemented
@app.route('/play_perm/<game_id>')
def play_permanent(game_id):
    # Set up
    this_game = Game.query.get_or_404(int(game_id))
    this_game.verify_board_to_play('Permanent')
    print("Playing Permanent Board")
    moves = []

    # Load board
    perm = Permanent.query.filter_by(game_id=game_id).first()
    perm_board = pickle.loads(perm.board)

    # Moves beads; different rules depending on even or odd round
    if this_game.round_count % 2 == 0:
        this_unsheltered = Unsheltered.query.filter_by(game_id=game_id).first()
        perm_board, moves = this_unsheltered.receive_unlimited(1, perm_board,
                                                               moves)
    else:
        this_market = Market.query.filter_by(game_id=game_id).first()
        perm_board, moves = this_market.receive_unlimited(1, perm_board, moves)

    # Wrap up
    perm.board = pickle.dumps(perm_board)
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
            this_game.calculate_final_score()
            this_score = Score.query.filter_by(game_id=game_id).first()
            return render_template('event.html', game=this_game,
                                   score=this_score)
        else:
            return render_template('event.html', game=this_game)


DISPATCHER_DEFAULT = {'Intake': play_intake, 'Emergency': play_emergency,
                      'Rapid': play_rapid, 'Outreach': play_outreach,
                      'Transitional': play_transitional,
                      'Permanent': play_permanent}


# TODO: change status to reflect program changes
# TODO: diff rules in rounds!

# TODO: Something is funky with validation of which board to play next
# TODO: gameplay where you make pre-round choices, then play entire round with 1 click
# TODO: change "round 6" to "game over" somehow

# TODO: randomize order in lists (for red beads)
# TODO: Add charts and major game choices to score board

# TODO: Improve view_log method
