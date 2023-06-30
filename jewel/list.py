from itertools import chain


def flatten(lst):
    return list(chain(*lst))
