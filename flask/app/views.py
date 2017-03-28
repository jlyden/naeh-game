from flask import request, render_template, redirect, url_for, flash
from app import app, db
from .models import Game, Emergency, Rapid, Transitional, Permanent
from .utils import get_random_bead, single_board_transfer, move_beads


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_game = Game()
        db.session.add(new_game)
        db.session.commit()
        new_game = Game.query.order_by(Game.start_datetime.desc()).first()
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
        flash('Only fill intake board once per round.', 'error')
    elif this_game.intake:
        flash('Only fill intake board once per round.', 'error')
    # If already at round 5, round 6 would be started by load_intake
    elif this_game.round_count > 4:
        flash('Only fill intake board once per round.', 'error')
    else:
        collection, available = get_random_bead(50, this_game.available)
        this_game.intake = collection
        this_game.available = available

        # Now the round has begun, so up-counter and toggle flag
        this_game.round_count += 1
        this_game.round_over = False
        db.session.commit()

    return redirect(url_for('status', game_id=this_game.id))


@app.route('/play_intake/<game_id>')
def play_intake(game_id):
    this_game = Game.query.get_or_404(int(game_id))

    if not this_game.intake:
        flash('Load intake board first!', 'error')
    else:
        emergency = Emergency.query.filter_by(game_id=game_id).first()
        surplus, this_game.intake,\
            emergency.board = single_board_transfer(10, this_game.intake,
                                                    emergency.board,
                                                    emergency.maximum)
        print('After emergency, ' + str(surplus) + 'extra beads')

        this_game.intake,\
            this_game.unsheltered = move_beads(10, this_game.intake,
                                               this_game.unsheltered)

        extra, this_game.intake,\
            emergency.board = single_board_transfer(30, this_game.intake,
                                                    emergency.board,
                                                    emergency.maximum)
        print('After emergency #2, ' + str(extra) + 'extra beads')

        rapid = Rapid.query.filter_by(game_id=game_id).first()
        extra, this_game.intake,\
            rapid.board = single_board_transfer(extra, this_game.intake,
                                                rapid.board,
                                                rapid.maximum)
        print('After rapid, ' + str(extra) + 'extra beads')

        transitional = Transitional.query.filter_by(game_id=game_id).first()
        extra, this_game.intake,\
            transitional.board = single_board_transfer(extra, this_game.intake,
                                                       transitional.board,
                                                       transitional.maximum)
        print('After transitional, ' + str(extra) + 'extra beads')

        permanent = Permanent.query.filter_by(game_id=game_id).first()
        extra, this_game.intake,\
            permanent.board = single_board_transfer(extra, this_game.intake,
                                                    permanent.board,
                                                    permanent.maximum)
        print('After permanent, ' + str(extra) + 'extra beads')

        surplus += extra
        this_game.intake,\
            this_game.unsheltered = move_beads(surplus, this_game.intake,
                                               this_game.unsheltered)
        print('Intake = ' + len(this_game.intake) + 'beads')
        db.session.commit()
    return redirect(url_for('status', game_id=game_id))
