import pickle
from flask import request, render_template, redirect, url_for, flash
from app import app, db
from .models.game import Game
from .utils.boardplay import DISPATCHER_DEFAULT
from .utils.lists import BOARD_LIST
from .utils.misc import gen_board_string_list, gen_progs_for_sys_event
from .utils.misc import set_board_to_play
from .utils.recordkeeping import end_round
from .utils.statusloads import load_board_lens_and_maxes, load_decisions
from .utils.statusloads import load_counts, load_changes
from .utils.content import tips


@app.route('/')
@app.route('/index')
def home():
    # Unfinished games have a final_score of 0 by default
    open_games = Game.query.filter(Game.final_score == 0
                                   ).order_by(Game.start_datetime.desc())
    complete_games = Game.query.filter(Game.final_score > 0
                                       ).order_by(Game.final_score)
    return render_template('home.html', open_games=open_games,
                           complete_games=complete_games)


@app.route('/new_game', methods=['POST'])
def new_game():
    new_game = Game.setup()
    return redirect(url_for('status', game_id=new_game.id))


@app.route('/status/<game_id>')
def status(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    board_num_list = pickle.loads(this_game.board_num_list_pickle)
    current_board_list = gen_board_string_list(board_num_list)
    programs = []
    # If time for system event, populate programs
    if this_game.board_to_play == 9:
        programs = gen_progs_for_sys_event(current_board_list)
    # Load other game data for status page
    board_lens, maxes = load_board_lens_and_maxes(game_id, current_board_list)
    counts = load_counts(game_id, board_num_list)
    changes = load_changes(game_id, board_num_list)
    decisions = load_decisions(game_id)
    return render_template('status.html', tips=tips, game=this_game,
                           board_list=current_board_list,
                           programs=programs, board_lens=board_lens,
                           maxes=maxes, counts=counts, changes=changes,
                           decisions=decisions)


@app.route('/play_round/<game_id>')
def play_round(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    if this_game.round_count < 6:
        board_num_list = pickle.loads(this_game.board_num_list_pickle)
        for board_num in board_num_list:
            play_board(this_game, board_num, board_num_list)
        return redirect(url_for('status', game_id=game_id))
    else:
        flash(u'Game over - no more plays.', 'warning')
    return redirect(url_for('status', game_id=game_id))


def play_board(game, board_num, board_num_list):
    # Play the board specified
    print("Playing " + str(board_num) + ", " + BOARD_LIST[board_num])
    DISPATCHER_DEFAULT[board_num](game)
    # Set next board_to_play
    game.board_to_play = set_board_to_play(board_num, board_num_list)
    # If board list is exhausted (set to 6 by previous method)
    if game.board_to_play == 6:
        round_count = end_round(game)
    # If game is over, time to calculate Final Score
        if round_count == 6:
            final_score = game.generate_score()
            game.final_score = final_score
    db.session.commit()
    return redirect(url_for('status', game_id=game.id))


@app.route('/event/<game_id>', methods=['POST'])
def event(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    if this_game.round_count == 2:
        program = request.form.get('program')
        this_game.open_new(program)
    elif this_game.round_count == 3 or this_game.round_count == 4:
        from_program = request.form.get('from_program')
        to_program = request.form.get('to_program')
        this_game.convert_program(from_program, to_program)
    # Set board_to_play to 0
    this_game.board_to_play = 0
    db.session.commit()
    return redirect(url_for('status', game_id=game_id))


@app.route('/about_boards/<game_id>')
def about_boards(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    return render_template('about-boards.html', game=this_game)

# TODO: Check eval(prog) for numbers
# TODO: After round, nav to splash screen showing where intake went
# TODO: Add system events to splash screen
# TODO: do we need logs again?
# TODO: One-button run simulation version with side-by-side comparison
# TODO: add animation
