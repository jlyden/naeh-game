import pickle
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
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        # surplus will be added to extra later; extra is dynamic
        surplus, intake, emergency_count = emergency.receive_beads(10, intake)
        intake = this_game.send_to_unsheltered(10, intake)
        extra, intake, emergency_count = emergency.receive_beads(30, intake)

        rapid = db.session.query(Rapid).filter_by(game_id=game_id).first()
        extra, intake = rapid.receive_beads(extra, intake)

        transitional = Transitional.query.filter_by(game_id=game_id).first()
        extra, intake, trans_count = transitional.receive_beads(extra, intake)

        permanent = Permanent.query.filter_by(game_id=game_id).first()
        extra, intake = permanent.receive_beads(extra, intake)

        surplus += extra
        print("before last load, surplus is " + str(surplus))
        print("before last load, intake has " + str(len(intake)) + " beads")
        intake = this_game.send_to_unsheltered(surplus, intake)
        print("after last load, intake has " + str(len(intake)) + " beads")

        this_game.intake = pickle.dumps(intake)
        this_game.round_over = True
        db.session.commit()

        this_score = Score.query.filter_by(game_id=game_id).first()
        this_score.add_score(emergency_count, trans_count)

    return redirect(url_for('status', game_id=game_id))
