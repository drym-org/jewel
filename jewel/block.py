import Pyro5
from .models import Block
from .checksum import compute_checksum
from .metadata import make_metadata


def make_block(contents):
    checksum = compute_checksum(contents)
    return Block(checksum, contents)
