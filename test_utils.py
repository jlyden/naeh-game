# Reference: http://pythontesting.net/framework/pytest/pytest-introduction/
import unittest


class TestGameplay(unittest.TestCase):

    def test_move_beads_no_red_false(self):
        from app.utils import move_beads
        # setup
        from_board_original = list(range(1, 51))
        from_board = from_board_original[:]
        to_board = []
        no_red = False

        extra_beads, to_board = move_beads(10, from_board, to_board, no_red)

        # check contents
        assert set(extra_beads).issubset(from_board_original)
        assert set(to_board).issubset(from_board_original)
        assert set(extra_beads).isdisjoint(to_board)
        assert set(extra_beads).__eq__(from_board)

        # check randomness
        to_board_sorted = sorted(to_board)
        assert to_board_sorted != to_board
        return

    def test_move_beads_no_red_true(self):
        from app.utils import move_beads
        # setup beads around 65, the dividing line for reds
        original_from_board = list(range(51, 101))
        from_board = original_from_board[:]
        to_board = []
        no_red = True

        extra_beads, to_board = move_beads(10, from_board, to_board, no_red)

        # check contents
        assert set(extra_beads).issubset(original_from_board)
        assert set(to_board).issubset(original_from_board)
        assert set(extra_beads).isdisjoint(to_board)
        assert set(extra_beads).__eq__(from_board)

        # check randomness
        to_board_sorted = sorted(to_board)
        assert to_board != to_board_sorted

        # check for reds
        to_board_no_red = [x for x in to_board if x >= 65]
        assert to_board.__eq__(to_board_no_red)
        return

    def test_find_room(self):
        from app.utils import find_room
        # setup
        board = list(range(1, 11))
        board_max = 15

        room = find_room(board_max, board)
        assert room == 5
        return

    def test_use_room_more_room(self):
        from app.utils import use_room
        # setup
        room = 15
        number_beads = 10
        from_board_original = list(range(1, 51))
        from_board = from_board_original[:]
        to_board = []
        no_red = False

        extra, from_board, to_board = use_room(room,
                                               number_beads,
                                               from_board,
                                               to_board,
                                               no_red)

        # check contents
        assert set(from_board).issubset(from_board_original)
        assert set(to_board).issubset(from_board_original)
        assert set(from_board).isdisjoint(to_board)

        # check randomness
        to_board_sorted = sorted(to_board)
        assert to_board_sorted != to_board

        # check extra
        assert extra == 0
        return

    def test_use_room_more_beads(self):
        from app.utils import use_room
        # setup
        room = 5
        number_beads = 10
        from_board_original = list(range(1, 51))
        from_board = from_board_original[:]
        to_board = []
        no_red = False

        extra, from_board, to_board = use_room(room,
                                               number_beads,
                                               from_board,
                                               to_board,
                                               no_red)

        # check contents
        assert set(from_board).issubset(from_board_original)
        assert set(to_board).issubset(from_board_original)
        assert set(from_board).isdisjoint(to_board)

        # check randomness
        to_board_sorted = sorted(to_board)
        assert to_board_sorted != to_board

        # check extra
        assert extra == 5
        return

    def test_message_for(self):
        from app.utils import message_for
        # setup
        beads_moved = 5
        board_name = "Emergency"
        message = message_for(beads_moved, board_name)

        assert message == "5 beads to Emergency"
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
