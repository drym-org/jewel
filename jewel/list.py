from itertools import chain
from math import ceil


def flatten(lst):
    return list(chain(*lst))


def chunks(it, size):
    input_length = len(it)
    num_chunks = ceil(input_length/size)
    return [it[i*size: i*size+size] for i in range(num_chunks)]


def tessellate(shards):
    """ This is just a matrix transpose, if we consider that the shards, as a
    2d array (list of lists), form a matrix. As transpose, this operation is
    its own inverse. """
    num_shards = len(shards)
    repetition_length = len(shards[0])
    shards = flatten(shards)
    jewels = []
    total_length = num_shards * repetition_length
    for i in range(repetition_length):
        ith_shards = shards[i:total_length:repetition_length]
        jewels.append(ith_shards)
    return jewels
