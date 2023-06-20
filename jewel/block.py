import Pyro5
from .models import Block
from .checksum import compute_checksum
from .metadata import make_metadata


def make_block(contents):
    checksum = compute_checksum(contents)
    return Block(checksum, contents)


def store_block(block, peer_uid, name=None):
    """ This interface represents the "blocks" abstraction layer. It does not
    need to know anything about the storage scheme being employed or about
    sharding. It simply stores a "block" of data (which may happen to be a file
    or a shard at a higher level of abstraction) on some peer."""
    metadata = make_metadata(block, name)
    with Pyro5.api.Proxy(peer_uid) as peer:
        peer.store(metadata.__dict__, block.data)
