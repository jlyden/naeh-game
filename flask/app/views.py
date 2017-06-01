import math
import pickle
from flask import request, render_template, redirect, url_for, flash
from app import app, db
from .utils import find_room, move_beads
from .models import Game, Emergency, Rapid, Transitional, Permanent, Score


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

    return render_template('status.html', game=this_game, intake=intake_board,
                           outreach=outreach_board, market=market_board,
                           unsheltered=unsheltered_board,
                           emergency=emergency_board, rapid=rapid_board,
                           transitional=transitional_board,
                           permanent=permanent_board,
                           emergency_count=emergency_count,
                           transitional_count=transitional_count)


@app.route('/load_intake/<game_id>')
def load_intake(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    intake = pickle.loads(this_game.intake)

    # Validation: Only load intake board after end of previous round
    if intake or not this_game.round_over:
        flash('Only load intake board once per round.', 'error')
    else:
        this_game.load_intake()
    return redirect(url_for('status', game_id=this_game.id))


@app.route('/play_intake/<game_id>')
def play_intake(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    intake = pickle.loads(this_game.intake)

    # Validation
    if this_game.round_over or not intake:
        flash('Load intake board to start round.', 'error')
    else:
        # col = one "column" in game instructions
        col = math.ceil(50 / this_game.intake_cols)
        print("col is " + str(col))
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        surplus, intake = emergency.receive_beads(col, intake)
        intake = this_game.send_to_unsheltered(col, intake)

        # Find room anywhere
        print("before find room anywhere, intake is  " + str(len(intake)))
        extra, intake = emergency.receive_beads(len(intake), intake)
        rapid = Rapid.query.filter_by(game_id=game_id).first()
        extra, intake = rapid.receive_beads(extra, intake)
        transitional = Transitional.query.filter_by(game_id=game_id).first()
        extra, intake = transitional.receive_beads(extra, intake)
        permanent = Permanent.query.filter_by(game_id=game_id).first()
        extra, intake = permanent.receive_beads(extra, intake)

        print("before last unsheltered, intake has " + str(len(intake)) + " beads")
        intake = this_game.send_to_unsheltered(len(intake), intake)
        this_game.intake = pickle.dumps(intake)
        db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_emergency/<game_id>')
def play_emergency(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    intake = pickle.loads(this_game.intake)

    # Validation
    if this_game.round_over or len(intake) is not 0:
        flash('Play intake board first.', 'error')
    else:
        # Emergency board = 5x5, so 1 col = 5; 1.5 col = 8
        col = math.ceil(1.5 * 5)
        print("Emergency col = " + str(col))
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        emerg_board = pickle.loads(emergency.board)
        emerg_board = this_game.send_to_market(col, emerg_board)
        emerg_board = this_game.send_to_unsheltered(col, emerg_board)

        extra = len(emerg_board)
        rapid = Rapid.query.filter_by(game_id=game_id).first()
        extra, emerg_board = rapid.receive_beads(extra, emerg_board)
        transitional = Transitional.query.filter_by(game_id=game_id).first()
        extra, emerg_board = transitional.receive_beads(extra, emerg_board)
        permanent = Permanent.query.filter_by(game_id=game_id).first()
        extra, emerg_board = permanent.receive_beads(extra, emerg_board)
        emerg_board = this_game.send_to_unsheltered(extra, emerg_board)
        emergency.board = pickle.dumps(emerg_board)
        db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_rapid/<game_id>')
def play_rapid(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    intake = pickle.loads(this_game.intake)

    # Validation
    if this_game.round_over or len(intake) is not 0:
        flash('Play intake board first.', 'error')
    else:
        # Rapid board = 5x2, so 1 col = 2
        col = 2
        rapid = Rapid.query.filter_by(game_id=game_id).first()
        rapid_board = pickle.loads(rapid.board)
        rapid_board = this_game.send_to_market(3 * col, rapid_board)
        print("after market, rapid_board is " + str(len(rapid_board)))
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        extra, rapid_board = emergency.receive_beads(col, rapid_board)
        rapid.board = pickle.dumps(rapid_board)
        db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_outreach/<game_id>')
def play_outreach(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    intake = pickle.loads(this_game.intake)

    # Validation
    if this_game.round_over or len(intake) is not 0:
        flash('Play intake board first.', 'error')
    else:
        outreach_max = 10
        outreach_board = pickle.loads(this_game.outreach)
        room = find_room(outreach_max, outreach_board)
        print("Outreach room is " + str(room))
        unsheltered_board = pickle.loads(this_game.unsheltered)
        unsheltered_board, outreach_board = move_beads(room, unsheltered_board, outreach_board)
        print("at max, outreach_board is " + str(len(outreach_board)))

        # TODO: add check for while extra > 0
        extra = len(outreach_board)
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        extra, outreach_board = emergency.receive_beads(extra, outreach_board)
        rapid = Rapid.query.filter_by(game_id=game_id).first()
        extra, outreach_board = rapid.receive_beads(extra, outreach_board)
        trans = Transitional.query.filter_by(game_id=game_id).first()
        extra, outreach_board = trans.receive_beads(extra, outreach_board)
        permanent = Permanent.query.filter_by(game_id=game_id).first()
        extra, outreach_board = permanent.receive_beads(extra, outreach_board)
        outreach_board = this_game.send_to_unsheltered(extra, outreach_board)
        this_game.outreach = pickle.dumps(outreach_board)
        db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_transitional/<game_id>')
def play_transitional(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    intake = pickle.loads(this_game.intake)

    # Validation
    if this_game.round_over or len(intake) is not 0:
        flash('Play intake board first.', 'error')
    else:
        # Transitional board = 5x4, so 1 col = 4
        col = 4
        trans = Transitional.query.filter_by(game_id=game_id).first()
        trans_board = pickle.loads(trans.board)
        trans_board = this_game.send_to_market(col, trans_board)
        print("after market, trans_board is " + str(len(trans_board)))
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        extra, trans_board = emergency.receive_beads(col, trans_board)
        if extra:
            trans_board = this_game.send_to_unsheltered(extra, trans_board)
        print("after unsheltered, trans_board is " + str(len(trans_board)))
        trans.board = pickle.dumps(trans_board)
        db.session.commit()
    return redirect(url_for('status', game_id=game_id))


# round implemented
@app.route('/play_permanent/<game_id>')
def play_permanent(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    intake = pickle.loads(this_game.intake)
    print("intake is " + str(intake))

    # Validation
    if this_game.round_over or len(intake) is not 0:
        flash('Play intake board first.', 'error')
    else:
        permanent = Permanent.query.filter_by(game_id=game_id).first()
        permanent_board = pickle.loads(permanent.board)
        # if even round
        if this_game.round_count % 2 == 0:
            permanent_board = this_game.send_to_unsheltered(1, permanent_board)
            print("after unsheltered, permanent_board is " + str(len(permanent_board)))
        else:
            permanent_board = this_game.send_to_market(1, permanent_board)
            print("after market, permanent_board is " + str(len(permanent_board)))
        permanent.board = pickle.dumps(permanent_board)

        # This ends round - time to score
        this_game.round_over = True
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        emerg_count = len(pickle.loads(emergency.board))
        trans = Transitional.query.filter_by(game_id=game_id).first()
        trans_count = len(pickle.loads(trans.board))
        this_score = Score.query.filter_by(game_id=game_id).first()
        this_score.add_score(emerg_count, trans_count)
        db.session.commit()
    return redirect(url_for('status', game_id=game_id))

# TODO: diversion
# TODO: diff rules in rounds!
# TODO: randomize order in lists
# TODO: randomize "place anywhere" board order
