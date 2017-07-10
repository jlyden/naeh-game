# Reference: http://pythontesting.net/framework/pytest/pytest-introduction/
import unittest


class TestGameplay(unittest.TestCase):

    def test_move_beads(self):
        from app.utils import move_beads
        no_red = False
        original_from_board = list(range(1, 11))
        from_board = original_from_board[:]
        to_board = []
        remaining_beads, to_board = move_beads(5, from_board, to_board, no_red)
        to_board_sorted = sorted(to_board)
        assert set(remaining_beads).issubset(from_board)
        assert set(to_board).issubset(original_from_board)
        assert set(remaining_beads).isdisjoint(to_board)
        assert to_board_sorted != to_board

# def test_move_beads():
#     from_board = list(range(1, 11))
#     to_board = []

# Test POST assert does not raise exception
# Tests in classes by topic
# view tests, model tests, api tests, unit tests
# expect exception
# create test database - have manage.py manage that too. define in config.py
#

# Test for each helper method
# Test for each database interaction (create, GET, update)


if __name__ == '__main__':
    unittest.main()
