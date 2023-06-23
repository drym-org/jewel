from functools import reduce
from operator import xor


# Modified from:
# https://nitratine.net/blog/post/xor-python-byte-strings/
def bytes_xor(*bs):
    return bytes([reduce(xor, bbs) for bbs in zip(*bs)])
