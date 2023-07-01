from functools import reduce
from operator import xor

NULL_BYTE = b'\0'


# Modified from:
# https://nitratine.net/blog/post/xor-python-byte-strings/
def bytes_xor(*bytestrings):
    return bytes([reduce(xor, bytes) for bytes in zip(*bytestrings)])


def pad_bytes(data, num_bytes):
    return data + NULL_BYTE * num_bytes


def unpad(data):
    return data.strip(NULL_BYTE)


def concat(bytestrings):
    return b''.join(bytestrings)


def null_bytes(length):
    return NULL_BYTE * length
