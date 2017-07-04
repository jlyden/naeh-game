# Reference: http://pythontesting.net/framework/pytest/pytest-introduction/
from models import get_random_bead


def test_get_random_bead():
    available_beads = list(range(1, 11))
    remaining_beads, collection = get_random_bead(5, available_beads)
    collection_sorted = sorted(collection)
    assert set(remaining_beads).issubset(available_beads)
    assert set(collection).issubset(available_beads)
    assert set(remaining_beads).isdisjoint(collection)
    assert collection_sorted != collection

# def test_move_beads():
#     from_board = list(range(1, 11))
#     to_board = []
