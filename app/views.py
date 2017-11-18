import pickle
from app import app, db
from flask import request, redirect, url_for, render_template, flash
from .models.game import Game
from .utils.boardplay import PLAY_BOARD
from .utils.content import tips
from .utils.lists import ALL_BOARDS
from .utils.lists import gen_progs_for_sys_event, set_board_to_play
from .utils.recordkeeping import end_round
from .utils.statusloads import load_board_lens_and_maxes, load_decisions
from .utils.statusloads import load_changes, load_counts, load_intake_dest


@app.route('/')
@app.route('/index')
def home():
    # Unfinished games have final_score set to 0
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


@app.route('/status/game<game_id>')
def status(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    print('Loading status for game ' + str(game_id) + ', round ' +
          str(this_game.round_count) + ' ...')
    board_num_list = pickle.loads(this_game.board_num_list_pickle)
#    print('board_num_list is ' + str(board_num_list))
    # If time for system event, populate programs
    programs = []
    if this_game.board_to_play == 9:
        programs = gen_progs_for_sys_event(board_num_list)
    # Load other game data for status page
    # TODO: Look at what I'm passing and why
    board_lens, maxes = load_board_lens_and_maxes(game_id)
    counts = load_counts(game_id)
    changes = load_changes(game_id, this_game.round_count)
    intake_dest = load_intake_dest(game_id, this_game.round_count - 1)
    decisions = load_decisions(game_id)
    return render_template('status.html', tips=tips, game=this_game,
                           board_list=board_num_list,
                           programs=programs, board_lens=board_lens,
                           maxes=maxes, counts=counts, changes=changes,
                           intake_dest=intake_dest, decisions=decisions)


@app.route('/play_round/<game_id>')
def play_round(game_id):
    this_game = Game.query.get_or_404(int(game_id))
    # Ensure there are beads to play
    available_beads = pickle.loads(this_game.available_pickle)
    if len(available_beads) == 0:
        flash(u'Game over - no more plays.', 'warning')
    elif this_game.round_count < 6:
        board_num_list = pickle.loads(this_game.board_num_list_pickle)
        for board_num in board_num_list:
            play_board(this_game, board_num, board_num_list)
    else:
        flash(u'Game over - no more plays.', 'warning')
    return redirect(url_for('status', game_id=game_id))


def play_board(game, board_num, board_num_list):
    # Play the board specified
    print("Playing " + str(board_num) + ", " + ALL_BOARDS[board_num])
    PLAY_BOARD[board_num](game)
    # Set next board_to_play
    game.board_to_play = set_board_to_play(board_num, board_num_list)
    db.session.commit()
    # If board list is exhausted, end round and return to status page
    if game.board_to_play == 6:
        end_round(game)
        return redirect(url_for('status', game_id=game.id))
    else:
        return  # control to play_round


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


# TODO: After round, status pops modal showing where intake went
# TODO: Stacked bar graphs showing where people in various programs came from
#       and went to
# TODO: Let user decide random vs. ordered 'place anywhere' program order
# TODO: Red beads!?!?
# TODO: Make notes about the information missing for novice users
# TODO: Add system events to post-round modal
# TODO: Something's wrong with Line charts (some boards dropping out early)
# TODO: Add recalc score, just in case
# TODO: Sticky header?
# TODO: Improve Run Round button/link - move to header
# TODO: Check eval(prog) for numbers
# TODO: do we need logs again?
# TODO: One-button run simulation version with side-by-side comparison
