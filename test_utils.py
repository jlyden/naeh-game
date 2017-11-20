# Reference: http://pythontesting.net/framework/pytest/pytest-introduction/
import unittest


class TestBeadmoves(unittest.TestCase):

    def test_move_beads_no_red_false(self):
        from app.utils.beadmoves import move_beads
        # arrange
        from_board_original = list(range(1, 51))
        from_board = from_board_original[:]
        to_board = []
        no_red = False

        # act
        extra_beads, to_board = move_beads(10, from_board, to_board, no_red)

        # assert - check contents
        assert set(extra_beads).issubset(from_board_original)
        assert set(to_board).issubset(from_board_original)
        assert set(extra_beads).isdisjoint(to_board)
        assert set(extra_beads).__eq__(from_board)
        # assert - check randomness
        to_board_sorted = sorted(to_board)
        assert to_board_sorted != to_board
        return

    def test_move_beads_no_red_true(self):
        from app.utils.beadmoves import move_beads
        # arrange beads around 65, the dividing line for reds
        original_from_board = list(range(51, 101))
        from_board = original_from_board[:]
        to_board = []
        no_red = True

        # act
        extra_beads, to_board = move_beads(10, from_board, to_board, no_red)

        # assert - check contents
        assert set(extra_beads).issubset(original_from_board)
        assert set(to_board).issubset(original_from_board)
        assert set(extra_beads).isdisjoint(to_board)
        assert set(extra_beads).__eq__(from_board)
        # assert - check randomness
        to_board_sorted = sorted(to_board)
        assert to_board != to_board_sorted
        # assert - check for reds
        to_board_no_red = [x for x in to_board if x >= 65]
        assert to_board.__eq__(to_board_no_red)
        return

# TODO: Add tests move 1 bead, 0 beads, all beads

    def test_find_room(self):
        from app.utils.beadmoves import find_room
        # arrange
        board = list(range(1, 11))
        board_max = 15

        # act, assert
        room = find_room(board_max, board)
        assert room == 5
        return

    def test_use_room_when_more_room(self):
        from app.utils.beadmoves import use_room
        # arrange
        room = 15
        number_beads = 10
        from_board_original = list(range(1, 51))
        from_board = from_board_original[:]
        to_board = []
        no_red = False

        # act
        extra, from_board, to_board = use_room(room,
                                               number_beads,
                                               from_board,
                                               to_board,
                                               no_red)

        # assert - check contents
        assert set(from_board).issubset(from_board_original)
        assert set(to_board).issubset(from_board_original)
        assert set(from_board).isdisjoint(to_board)
        # assert - check randomness
        to_board_sorted = sorted(to_board)
        assert to_board_sorted != to_board
        # assert - check extra
        assert extra == 0
        return

    def test_use_room_when_more_beads(self):
        from app.utils.beadmoves import use_room
        # arrange
        room = 5
        number_beads = 10
        from_board_original = list(range(1, 51))
        from_board = from_board_original[:]
        to_board = []
        no_red = False

        # act
        extra, from_board, to_board = use_room(room,
                                               number_beads,
                                               from_board,
                                               to_board,
                                               no_red)

        # assert - check contents
        assert set(from_board).issubset(from_board_original)
        assert set(to_board).issubset(from_board_original)
        assert set(from_board).isdisjoint(to_board)
        # assert - check randomness
        to_board_sorted = sorted(to_board)
        assert to_board_sorted != to_board
        # assert - check extra
        assert extra == 5
        return


class TestLists(unittest.TestCase):

    def test_gen_anywhere_list_no_Outreach(self):
        from app.utils.lists import gen_anywhere_list
        import pickle
        # arrange
        pre_test_list = [0, 1, 2, 4]
        test_list_pickle = pickle.dumps(pre_test_list)
        verification_list = [1, 2, 4]

        # act
        test_list = gen_anywhere_list(test_list_pickle)

        # assert - check contents
        assert len(test_list) == len(pre_test_list) - 1
        assert set(test_list).issubset(pre_test_list)
        assert set(test_list).issubset(verification_list)
        assert 0 not in test_list
        # assert - check randomness
        test_list_sorted = sorted(test_list)
        assert test_list_sorted != test_list
        return

    def test_gen_anywhere_list_yes_Outreach(self):
        from app.utils.lists import gen_anywhere_list
        import pickle
        # arrange
        pre_test_list = [0, 1, 2, 3, 4, 5]
        test_list_pickle = pickle.dumps(pre_test_list)
        verification_list = [1, 2, 4, 5]

        # act
        test_list = gen_anywhere_list(test_list_pickle)

        # assert - check contents
        assert len(test_list) == len(pre_test_list) - 2
        assert set(test_list).issubset(pre_test_list)
        assert set(test_list).issubset(verification_list)
        assert 0 not in test_list
        assert 3 not in test_list
        # assert - check randomness
        test_list_sorted = sorted(test_list)
        assert test_list_sorted != test_list
        return

    def test_gen_board_string_list_all_progs(self):
        from app.utils.lists import gen_board_string_list
        # arrange
        pre_test_list = [0, 1, 2, 3, 4, 5]
        verification_list = ['Intake', 'Emergency', 'Rapid', 'Outreach',
            'Transitional', 'Permanent']

        # act, assert
        test_list = gen_board_string_list(pre_test_list)
        assert test_list == verification_list
        return

    def test_gen_board_string_list_some_progs(self):
        from app.utils.lists import gen_board_string_list
        # arrange
        pre_test_list = [0, 2, 3, 4]
        verification_list = ['Intake', 'Rapid', 'Outreach', 'Transitional']

        # act, assert
        test_list = gen_board_string_list(pre_test_list)
        assert test_list == verification_list
        return

    def test_gen_progs_for_sys_event(self):
        from app.utils.lists import gen_progs_for_sys_event
        # arrange
        pre_test_list = [0, 1, 2, 4]
        verification_dict = {
            'Emergency': ['Rapid', 'Transitional'],
            'Rapid': ['Emergency', 'Transitional'],
            'Transitional': ['Emergency', 'Rapid']}

        # act, assert
        test_dict = gen_progs_for_sys_event(pre_test_list)
        assert test_dict == verification_dict
        return

    def test_set_board_to_play_from_all_boards_intake(self):
        from app.utils.lists import set_board_to_play
        # arrange
        pre_test_list = [0, 1, 2, 3, 4, 5]
        last_board_played = 5
        verification_string = 'Intake'

        # act, assert
        test_string = set_board_to_play(last_board_played, pre_test_list)
        assert test_string == verification_string
        return

# Test POST assert does not raise exception
# view tests, model tests, api tests, unit tests
# expect exception
# create test database - have manage.py manage that too. define in config.py
# Test for each database interaction (create, GET, update)


if __name__ == '__main__':
    unittest.main()
