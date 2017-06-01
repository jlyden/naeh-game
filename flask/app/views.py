import pickle, math
from flask import request, render_template, redirect, url_for, flash
from app import app, db
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
    print("this_game.unsheltered in round " + str(this_game.round_count) + " has " + str(len(unsheltered_board)) + " beads")

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
        # factor = one "column" in game instructions
        factor = math.ceil(50 / this_game.intake_cols)
        print("factor is " + str(factor))
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        surplus, intake = emergency.receive_beads(factor, intake)
        intake = this_game.send_to_unsheltered(factor, intake)

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
        print("after last load, intake has " + str(len(intake)) + " beads")

        this_game.intake = pickle.dumps(intake)
        db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/play_emergency/<game_id>')
def play_emergency(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    intake = pickle.loads(this_game.intake)

    # Validation
    if this_game.round_over or intake:
        flash('Play intake board first.', 'error')
    else:
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        emerg_board = pickle.loads(emergency.board)
        emerg_board = this_game.send_to_market(8, emerg_board)
        emerg_board = this_game.send_to_unsheltered(8, emerg_board)

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


#        this_game.round_over = True
# Need to query for these counts
#        this_score = Score.query.filter_by(game_id=game_id).first()
#        this_score.add_score(emerg_count, trans_count)

