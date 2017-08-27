import pickle


def get_board_contents(game_id, program_name):
    prog_table = eval(program_name)
    program = prog_table.query.filter_by(game_id=game_id).first()
    prog_board = pickle.loads(program.board)
    return program, prog_board
