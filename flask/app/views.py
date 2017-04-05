from flask import request, render_template, redirect, url_for, flash
from app import app, db
from .models import Game, Emergency, Rapid, Transitional, Permanent
from .utils import get_random_bead, single_board_transfer, move_beads


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_game = Game()
        db.session.add(new_game)
        new_game = Game.query.order_by(Game.start_datetime.desc()).first()
        emergency = Emergency(game_id=new_game.id)
        rapid = Rapid(game_id=new_game.id)
        transitional = Transitional(game_id=new_game.id)
        permanent = Permanent(game_id=new_game.id)
        db.session.add(emergency)
        db.session.add(rapid)
        db.session.add(transitional)
        db.session.add(permanent)
        db.session.commit()
        return redirect(url_for('status', game_id=new_game.id))
    elif request.method == 'GET':
        recent_games = Game.query.order_by(Game.start_datetime.desc()).limit(5)
        return render_template('index.html', recent_games=recent_games)


@app.route('/status/<game_id>')
def status(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    return render_template('status.html', this_game=this_game)


@app.route('/load_intake/<game_id>')
def load_intake(game_id):
    this_game = Game.query.get_or_404(int(game_id))

    # Validation: Only load intake board after end of previous round
    if not this_game.round_over:
        flash('Only load intake board once per round.', 'error')
    elif this_game.intake:
        flash('Only load intake board once per round.', 'error')
    # If already at round 5, round 6 would be started by load_intake
    elif this_game.round_count > 4:
        flash('Only load intake board once per round.', 'error')
    else:
        collection, available = get_random_bead(50, this_game.available)
        this_game.intake = collection
        this_game.available = available

        # Now the round has begun, so up-counter and toggle flag
        this_game.round_count += 1
        this_game.round_over = False
        db.session.add(this_game)
        db.session.commit()

    return redirect(url_for('status', game_id=this_game.id))


@app.route('/play_intake/<game_id>')
def play_intake(game_id):
    this_game = Game.query.get_or_404(int(game_id))

    # Validation
    if not this_game.intake:
        flash('Load intake board to start round.', 'error')
    elif this_game.round_over:
        flash('Load intake board to start round.', 'error')
    else:
        intake = this_game.intake
        unsheltered = this_game.unsheltered

        this_emergency = db.session.query(
            Emergency).filter_by(game_id=game_id).first()
        surplus, intake,\
            emergency = single_board_transfer(10, intake,
                                              this_emergency.board,
                                              this_emergency.maximum)
        print('after load, this_emergency.board=' + str(emergency))

        this_emergency.board = emergency
        db.session.add(this_emergency)
        db.session.commit()
        print('After emergency, ' + str(surplus) + ' extra beads')

        intake, unsheltered = move_beads(10, intake, unsheltered)

        # extra, intake,\
        #     emergency.board = single_board_transfer(30, intake,
        #                                             emergency.board,
        #                                             emergency.maximum)
        # db.session.add(emergency)
        # print('After emergency #2, ' + str(extra) + ' extra beads')

        # rapid = Rapid.query.filter_by(game_id=game_id).first()
        # extra, intake, rapid.board = single_board_transfer(extra, intake,
        #                                                    rapid.board,
        #                                                    rapid.maximum)
        # db.session.add(rapid)
        # print('After rapid, ' + str(extra) + ' extra beads')

        # transitional = Transitional.query.filter_by(game_id=game_id).first()
        # extra, intake,\
        #     transitional.board = single_board_transfer(extra, intake,
        #                                                transitional.board,
        #                                                transitional.maximum)
        # db.session.add(transitional)
        # print('After transitional, ' + str(extra) + ' extra beads')

        # permanent = Permanent.query.filter_by(game_id=game_id).first()
        # extra, intake,\
        #     permanent.board = single_board_transfer(extra, intake,
        #                                             permanent.board,
        #                                             permanent.maximum)
        # db.session.add(permanent)
        # print('After permanent, ' + str(extra) + ' extra beads')

        # surplus += extra
        # print('Move ' + str(surplus) + ' beads to unsheltered')
        # intake, unsheltered = move_beads(surplus, intake, unsheltered)

        this_game.intake = intake
        this_game.unsheltered = unsheltered
        db.session.add(this_game)
        print('Intake = ' + str(len(this_game.intake)) + ' beads')

        db.session.commit()

    return redirect(url_for('status', game_id=this_game.id))
