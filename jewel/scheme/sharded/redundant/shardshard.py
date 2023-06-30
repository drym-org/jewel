from .base import RedundantSharding
from ....sharding import register_shards, lookup_shards
from ....block import make_block
from ....models import Block
from ....metadata import make_metadata
from io import BytesIO
from ....list import flatten


class NaiveRedundantSharding(RedundantSharding):
    """
    This is identical to vanilla sharding except that it adds redundancy in
    (i.e. duplicates) each shard a certain number of times.
    """

    name = 'shardshard'

    _N = None
    _K = None
    _M = None

    def __init__(self, number_of_peers, number_of_shards, redundancy):
        self.number_of_peers = number_of_peers
        self.number_of_shards = number_of_shards
        self.redundancy = redundancy

    @property
    def number_of_peers(self):
        return self._N

    @number_of_peers.setter
    def number_of_peers(self, N):
        self._N = N

    @property
    def number_of_shards(self):
        return self._K

    @number_of_shards.setter
    def number_of_shards(self, K):
        self._K = K

    @property
    def redundancy(self):
        return self._M

    @redundancy.setter
    def redundancy(self, M):
        self._M = M

    def shard(self, block) -> list:
        """ Divide the input file into non-overlapping blocks. """
        block_length = len(block.data)
        shard_length = int(block_length / self.number_of_shards)
        shards = []
        f = BytesIO(block.data)
        for i in range(self.number_of_shards - 1):
            # read data to create the first n-1 shards
            data = f.read(shard_length)
            shard = make_block(data)
            shards.append(shard)
        # create the final, n'th shard from
        # all of the remaining data
        data = f.read()
        shard = make_block(data)
        shards.append(shard)
        shard_mds = [make_metadata(s) for s in shards]
        register_shards(block, shard_mds)
        return shards

    def introduce_redundancy(self, blocks):
        """ Add redundancy to the blocks (shards) to facilitate error
        recovery. """
        blocks = [[block] * self.redundancy
                  for block in blocks]
        blocks = flatten(blocks)
        return blocks

    def recover(self, block_name, blocks: list[Block]) -> list[Block]:
        """ Since this scheme simply duplicates shards, we expect the input
        shards here to be the original shards themselves. We just ensure that
        we have them all, and that they are in the right order. """
        if len(blocks) < self.number_of_shards:
            raise Exception("Can't recover as some blocks are missing!")
        block_checksums = lookup_shards(block_name)
        blocks.sort(key=lambda b: block_checksums.index(b.checksum))
        return blocks

    def store(self, file):
        """ Capturing the store behavior in the base class is a bit awkward at
        the moment since the base class assumes the presence of recovery
        shards, etc. So we just override the method here instead."""
        block, peer_uids = self.handshake_store(file)

        # ordered list of shards
        shards = self.shard(block)
        shards = self.introduce_redundancy(shards)
        self.stripe(shards, peer_uids)
