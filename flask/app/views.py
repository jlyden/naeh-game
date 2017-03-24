from flask import request, render_template, redirect, url_for, flash
from app import app, db
from .models import Game
from .utils import get_random_bead, play_round


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


@app.route('/play/<game_id>')
def play(game_id):
    play_round(game_id)
    return redirect(url_for('status', game_id=game_id))
