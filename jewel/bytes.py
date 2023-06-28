from functools import reduce
from operator import xor


# Modified from:
# https://nitratine.net/blog/post/xor-python-byte-strings/
def bytes_xor(*bytestrings):
    return bytes([reduce(xor, bytes) for bytes in zip(*bytestrings)])
