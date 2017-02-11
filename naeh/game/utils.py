# game/utils.py
import random
from ast import literal_eval


def get_random_bead(number, available_beads):
    # Convert strs to ints
    beads = literal_eval(available_beads)
    collection = []

    for i in range(number):
        # grab a random element
        selection = random.choice(beads)
        # add random element to new list
        collection.append(selection)
        # remove random element from existing list
        beads.remove(selection)

    return collection, available_beads
