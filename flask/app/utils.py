import random
from flask import flash
from app import db
from .models import Game, Rules


maximum = {'emergency': 25,
           'rapid': 10,
           'transitional': 20,
           'permanent': 20}


def get_random_bead(number, available_beads):
    collection = []
    for i in range(number):
        selection = random.choice(available_beads)
        collection.append(selection)
        available_beads.remove(selection)
    return collection, available_beads


def move_beads(number, from_board, to_board):
    for i in range(number):
        selection = from_board.pop()
        to_board.append(selection)
    return from_board, to_board


def find_room(board_name, board):
    # Workaround b/c neither of these have a maximum
    if board_name is 'unsheltered' or 'market':
        room = 50
    else:
        room = maximum[board_name] - len(board)
    return room


def use_room(room, beads, from_board, to_board):
    if room > beads:
        from_board, to_board = move_beads(beads, from_board, to_board)
        extra = 0
    elif beads > room:
        from_board, to_board = move_beads(room, from_board, to_board)
        extra = beads - room
    return extra, from_board, to_board


def single_board_transfer(board_name, beads, from_board, to_board):
    room = find_room(board_name, to_board)
    if room is 0:
        flash("No room in %s board!" % board_name)
        extra = beads
    else:
        extra, from_board, to_board = use_room(room, beads, from_board,
                                               to_board)
    return extra, from_board, to_board


def play_round(game_id):
    this_game = Game.query.get_or_404(int(game_id))

    LOOKUP = {'unsheltered': this_game.unsheltered,
              'market': this_game.market,
              'intake': this_game.intake,
              'emergency': this_game.emergency,
              'rapid': this_game.rapid,
              'outreach': this_game.outreach,
              'transitional': this_game.transitional,
              'permanent': this_game.permanent}

    REV_LOOKUP = {this_game.unsheltered: 'unsheltered',
                  this_game.market: 'market',
                  this_game.intake: 'intake',
                  this_game.emergency: 'emergency',
                  this_game.rapid: 'rapid',
                  this_game.outreach: 'outreach',
                  this_game.transitional: 'transitional',
                  this_game.permanent: 'permanent'}

    # Get moves for this round
    moves = Rules.query.filter_by(round_count=this_game.round_count).all()
    for move in moves:
        if move.to_board == 'unsheltered':
            print('Moving ' + str(move.bead_count) + ' beads to unsheltered')
            LOOKUP[move.from_board], \
                LOOKUP[move.to_board] = move_beads(move.bead_count,
                                                   LOOKUP[move.from_board],
                                                   LOOKUP['unsheltered'])
            print(LOOKUP[move.from_board], LOOKUP[move.to_board])
            from_board_name = REV_LOOKUP[LOOKUP[move.from_board]]
            to_board_name = REV_LOOKUP[LOOKUP[move.to_board]]
            print(from_board_name, to_board_name)
            this_game.intake = LOOKUP[move.from_board]
            this_game.unsheltered = LOOKUP[move.to_board]
            db.session.commit()
        # elif move.to_board == 'somewhere':
        #     print('Moving ' + str(move.bead_count) + ' beads somewhere')
        #     extra = move.bead_count
        #     for key in maximum:
        #         print('Moving ' + str(extra) + ' beads to ' + key)
        #         extra, LOOKUP[move.from_board], \
        #             LOOKUP[key] = single_board_transfer(key, extra,
        #                                                 LOOKUP[move.from_board],
        #                                                 LOOKUP[key])
        #     if extra > 0:
        #         LOOKUP[move.from_board], \
        #             LOOKUP['unsheltered'] = move_beads(extra,
        #                                                LOOKUP[move.from_board],
        #                                                LOOKUP['unsheltered'])
        #     db.session.commit()
        # elif move.to_board != 'somewhere':
        #     print('Moving ' + str(move.bead_count) + ' beads to ' +
        #           move.to_board)
        #     # if not somewhere, then to_board is specified
        #     extra, LOOKUP[move.from_board], \
        #         LOOKUP[move.to_board] = single_board_transfer(move.to_board,
        #                                                       move.bead_count,
        #                                                       LOOKUP[move.from_board],
        #                                                       LOOKUP[move.to_board])
        #     if extra > 0:
        #         LOOKUP[move.from_board], \
        #             LOOKUP['unsheltered'] = move_beads(extra,
        #                                                LOOKUP[move.from_board],
        #                                                LOOKUP['unsheltered'])
        #     db.session.commit()
        # # Now the round is over, so toggle flag
        # this_game.round_over = True
        # db.session.commit()
