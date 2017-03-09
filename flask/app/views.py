from flask import render_template, flash, redirect
from app import app
from .forms import NewGameForm


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = NewGameForm()
    if form.validate_on_submit():
        flash('New game requested for %s' % form.team_name.data)
        return redirect('/status')
    return render_template('index.html',
                           form=form)


@app.route('/status', methods=['GET'])
def status():
    team_name = 'Mock'
    return render_template('status.html',
                           team_name=team_name)
