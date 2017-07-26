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

    def test_find_room(self):
        from app.utils.beadmoves import find_room
        # arrange
        board = list(range(1, 11))
        board_max = 15

        # act, assert
        room = find_room(board_max, board)
        assert room == 5
        return

    def test_use_room_more_room(self):
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

    def test_use_room_more_beads(self):
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


class TestMisc(unittest.TestCase):

    def test_message_for(self):
        from app.utils.misc import message_for
        # arrange
        beads_moved = 5
        board_name = "Emergency"

        # act, assert
        message = message_for(beads_moved, board_name)
        assert message == "5 beads to Emergency"
        return

    def test_gen_progs_for_sys_event(self):
        from app.utils.misc import gen_progs_for_sys_event
        import pickle
        # arrange
        test_list = ['Intake', 'a', 'b', 'c', 'd']
        test_list_pickle = pickle.dumps(test_list)
        verification_dict = {
            'a': ['b', 'c', 'd'],
            'b': ['a', 'c', 'd'],
            'c': ['a', 'b', 'd'],
            'd': ['a', 'b', 'c']}

        # act, assert
        test_dict = gen_progs_for_sys_event(test_list_pickle)
        assert test_dict == verification_dict
        return


# Test POST assert does not raise exception
# Tests in classes by topic
# view tests, model tests, api tests, unit tests
# expect exception
# create test database - have manage.py manage that too. define in config.py
# Test for each helper method
# Test for each database interaction (create, GET, update)


if __name__ == '__main__':
    unittest.main()
