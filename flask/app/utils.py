import random


def get_random_bead(number, available_beads):
    collection = []

    for i in range(number):
        # grab a random element
        selection = random.choice(available_beads)
        # add random element to new list
        collection.append(selection)
        # remove random element from existing list
        available_beads.remove(selection)

    return collection, available_beads
