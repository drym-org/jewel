from .models import Block
from .checksum import compute_checksum


def make_block(contents):
    checksum = compute_checksum(contents)
    return Block(checksum, contents)
