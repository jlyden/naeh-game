# Reference: http://pythontesting.net/framework/pytest/pytest-introduction/
import unittest


class TestUtils():

    def int_to_whole(number):
        if number < 0:
            number = 0
        return number


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
        from_board_original = list(range(51, 101))
        from_board = from_board_original[:]
        to_board = []
        no_red = True

        # act
        extra_beads, to_board = move_beads(10, from_board, to_board, no_red)

        # assert - check contents
        assert set(extra_beads).issubset(from_board_original)
        assert set(to_board).issubset(from_board_original)
        assert set(extra_beads).isdisjoint(to_board)
        assert set(extra_beads).__eq__(from_board)
        # assert - check randomness
        to_board_sorted = sorted(to_board)
        assert to_board != to_board_sorted
        # assert - check for reds
        to_board_no_red = [x for x in to_board if x >= 65]
        assert to_board.__eq__(to_board_no_red)
        return

    def test_move_beads_zero(self):
        from app.utils.beadmoves import move_beads
        # arrange
        from_board_original = list(range(1, 51))
        from_board = from_board_original[:]
        to_board = []
        no_red = False

        # act
        extra_beads, to_board = move_beads(0, from_board, to_board, no_red)

        # assert - check contents
        assert set(extra_beads).issubset(from_board_original)
        assert set(to_board).issubset(from_board_original)
        assert set(extra_beads).isdisjoint(to_board)
        assert set(extra_beads).__eq__(from_board)
        return

    def test_move_beads_one(self):
        from app.utils.beadmoves import move_beads
        # arrange
        from_board_original = list(range(1, 51))
        from_board = from_board_original[:]
        to_board = []
        no_red = False

        # act
        extra_beads, to_board = move_beads(1, from_board, to_board, no_red)

        # assert - check contents
        assert set(extra_beads).issubset(from_board_original)
        assert set(to_board).issubset(from_board_original)
        assert set(extra_beads).isdisjoint(to_board)
        assert set(extra_beads).__eq__(from_board)
        return

    def test_move_beads_all(self):
        from app.utils.beadmoves import move_beads
        # arrange
        from_board_original = list(range(1, 51))
        from_board = from_board_original[:]
        to_board = []
        no_red = False

        # act
        extra_beads, to_board = move_beads(len(from_board), from_board,
                                           to_board, no_red)

        # assert - check contents
        assert set(extra_beads).issubset(from_board_original)
        assert set(to_board).issubset(from_board_original)
        assert set(extra_beads).isdisjoint(to_board)
        assert set(extra_beads).__eq__(from_board)
        # assert - check randomness
        to_board_sorted = sorted(to_board)
        assert to_board_sorted != to_board
        return

    def test_find_room(self):
        from app.utils.beadmoves import find_room
        # arrange
        board = list(range(1, 11))
        board_max = 15

        # act, assert
        room = find_room(board_max, board)
        assert room == 5
        return

    def test_find_room_no_room(self):
        from app.utils.beadmoves import find_room
        # arrange
        board = list(range(1, 11))
        board_max = 10

        # act, assert
        room = find_room(board_max, board)
        assert room == 0
        return

    def test_find_room_all_room(self):
        from app.utils.beadmoves import find_room
        # arrange
        board = list()
        board_max = 15

        # act, assert
        room = find_room(board_max, board)
        assert room == 15
        return

    def test_use_room_when_more_room(self):
        from app.utils.beadmoves import use_room
        from app.utils.beadmoves import find_room
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
        # assert - check sizes
        assert len(to_board).__eq__(number_beads)
        assert extra == TestUtils.int_to_whole(number_beads - room)
        assert find_room(room, to_board
                         ).__eq__(
                         TestUtils.int_to_whole(room - number_beads))
        return

    def test_use_room_when_more_beads(self):
        from app.utils.beadmoves import use_room
        from app.utils.beadmoves import find_room
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
        # assert - check sizes
        assert len(to_board).__eq__(room)
        assert extra == TestUtils.int_to_whole(number_beads - room)
        assert find_room(room, to_board
                         ).__eq__(
                         TestUtils.int_to_whole(room - number_beads))
        return

    def test_use_room_when_no_room(self):
        from app.utils.beadmoves import use_room
        from app.utils.beadmoves import find_room
        # arrange
        room = 0
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
        assert set(from_board).__eq__(from_board_original)
        assert set(to_board).__eq__([])
        # assert - check sizes
        assert len(to_board).__eq__(0)
        assert extra == TestUtils.int_to_whole(number_beads - room)
        assert find_room(room, to_board
                         ).__eq__(
                         TestUtils.int_to_whole(room - number_beads))
        return


class TestLists(unittest.TestCase):

    def test_gen_anywhere_list_no_Outreach(self):
        from app.utils.lists import gen_anywhere_list
        import pickle
        # arrange
        pre_test_list = [0, 1, 2, 4, 5]
        test_list_pickle = pickle.dumps(pre_test_list)
        verification_list = [1, 2, 4, 5]

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

    def test_gen_anywhere_list_values_out_of_bounds(self):
        from app.utils.lists import gen_anywhere_list
        import pickle
        # arrange
        pre_test_list = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        test_list_pickle = pickle.dumps(pre_test_list)
        verification_list = [1, 2, 4, 5]

        # act
        test_list = gen_anywhere_list(test_list_pickle)

        # assert - check contents
        assert len(test_list) == len(pre_test_list) - 5
        assert set(test_list).issubset(pre_test_list)
        assert set(test_list).issubset(verification_list)
        assert set([0, 3, 6, 7, 8]).isdisjoint(verification_list)
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

    def test_gen_progs_for_sys_event_all_progs(self):
        from app.utils.lists import gen_progs_for_sys_event
        # arrange
        pre_test_list = [0, 1, 2, 3, 4, 5]
        verification_dict = {
            'Emergency': ['Rapid', 'Outreach', 'Transitional', 'Permanent'],
            'Rapid': ['Emergency', 'Outreach', 'Transitional', 'Permanent'],
            'Outreach': ['Emergency', 'Rapid', 'Transitional', 'Permanent'],
            'Transitional': ['Emergency', 'Rapid', 'Outreach', 'Permanent'],
            'Permanent': ['Emergency', 'Rapid', 'Outreach', 'Transitional']}

        # act, assert
        test_dict = gen_progs_for_sys_event(pre_test_list)
        assert test_dict == verification_dict
        return

    def test_gen_progs_for_sys_event_some_progs(self):
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

    def test_set_board_to_play_from_all_boards_first(self):
        from app.utils.lists import set_board_to_play
        # arrange
        pre_test_list = [0, 1, 2, 3, 4, 5]
        last_board_played = 0
        verification_int = 1

        # act, assert
        test_int = set_board_to_play(last_board_played, pre_test_list)
        assert test_int == verification_int
        return

    def test_set_board_to_play_from_all_boards_last(self):
        from app.utils.lists import set_board_to_play
        # arrange
        pre_test_list = [0, 1, 2, 3, 4, 5]
        last_board_played = 5
        verification_int = 6

        # act, assert
        test_int = set_board_to_play(last_board_played, pre_test_list)
        assert test_int == verification_int
        return

    def test_set_board_to_play_from_four_boards_first(self):
        from app.utils.lists import set_board_to_play
        # arrange
        pre_test_list = [0, 2, 3, 5]
        last_board_played = 0
        verification_int = 2

        # act, assert
        test_int = set_board_to_play(last_board_played, pre_test_list)
        assert test_int == verification_int
        return

    def test_set_board_to_play_from_four_boards_middle(self):
        from app.utils.lists import set_board_to_play
        # arrange
        pre_test_list = [0, 2, 3, 5]
        last_board_played = 3
        verification_int = 5

        # act, assert
        test_int = set_board_to_play(last_board_played, pre_test_list)
        assert test_int == verification_int
        return

    def test_set_board_to_play_from_four_boards_last(self):
        from app.utils.lists import set_board_to_play
        # arrange
        pre_test_list = [0, 2, 3, 5]
        last_board_played = 5
        verification_int = 6

        # act, assert
        test_int = set_board_to_play(last_board_played, pre_test_list)
        assert test_int == verification_int
        return

# Test POST assert does not raise exception
# view tests, model tests, api tests, unit tests
# expect exception
# create test database - have manage.py manage that too. define in config.py
# Test for each database interaction (create, GET, update)


if __name__ == '__main__':
    unittest.main()
