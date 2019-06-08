import random

ID_array = []


def generate_ID():

    ID = random.randint()
    if ID not in ID_array:
        return ID
    else:
        generate_ID()
