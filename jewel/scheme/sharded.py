from .base import StorageScheme
from ..checksum import compute_checksum
from ..models import Block
from ..striping import stripe_blocks
from ..block import make_block
from ..metadata import make_metadata
from collections import defaultdict
from itertools import cycle
from ..networking import peers_available_to_host


class ShardedDuplication(StorageScheme):

    def __init__(self, number_of_peers):
        self.number_of_peers = number_of_peers

    def shard(self, file) -> list:
        """ Divide the input file into non-overlapping blocks. """
        return [Block(compute_checksum(file), file)]

    def introduce_redundancy(self, shards):
        """ Add redundancy to the shards to facilitate error recovery. """
        return shards

    def allocate(self, blocks, host_uids) -> dict:
        """ Allocate all blocks to the available hosts."""
        allocations = defaultdict(list)
        # round robin allocation
        for h in cycle(host_uids):
            if not blocks:
                break
            allocations[h] += blocks.pop()
        return allocations

    def store(self, file):
        """ The main entry point to store a file using this scheme. """
        # TODO: should this accept a block and metadata instead,
        # and do the handshake with the server here instead
        # of accepting a list of peer ids?
        # -> yes I think so.
        # ordered list of shards
        block = make_block(file.data)
        metadata = make_metadata(block, file.name)
        peer_uids = peers_available_to_host(metadata)

        shards = self.shard(file.data)
        # (unordered) lookup shard by checksum
        shard_index = {s.checksum: s for s in shards}
        peer_allocation = self.allocate(shards, peer_uids)
        for peer_uid in peer_allocation:
            peer_shards = peer_allocation[peer_uid]  # list of checksums
            peer_shards = [shard_index[sid] for sid in peer_shards]
            stripe_blocks(peer_uid, peer_shards)

    def get(self, filename, contents, peer_uids):
        """ The main entry point to get a file that was stored using this
        scheme. """
        # TODO
        pass
