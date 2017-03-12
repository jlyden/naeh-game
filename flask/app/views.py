from flask import request, render_template, redirect, url_for, flash
from app import app, db
from .forms import NewGameForm
from .models import Game


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/new', methods=['GET', 'POST'])
def new():
    form = NewGameForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            flash('New game requested for %s' % form.team_name.data)
            game = Game()
            game.team_name = form.team_name
            db.session.add(game)
            db.session.commit()
            game = Game.query.get(team_name=form.team_name)
            return redirect('/status/%s' % game.id)


@app.route('/status/<game_id>')
def status(game_id):
    this_game = Game.query.get(int(game_id))
    if this_game is None:
        flash('Game %s not found.' % game_id)
        return redirect(url_for('index'))
    return render_template('status.html', this_game=this_game)
