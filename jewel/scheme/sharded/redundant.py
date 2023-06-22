from .base import ShardedStorageScheme
from ..striped import StripedStorageScheme
from ..redundant import RedundantStorageScheme
from ...sharding import register_shards
from ...block import make_block
from io import BytesIO
from itertools import chain


class RedundantSharding(ShardedStorageScheme, StripedStorageScheme, RedundantStorageScheme):
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
        register_shards(block, shards)
        return shards

    def introduce_redundancy(self, blocks):
        """ Add redundancy to the blocks (shards) to facilitate error
        recovery. """
        blocks = [[block] * self.redundancy
                  for block in blocks]
        blocks = list(chain(*blocks))  # flatten
        return blocks

    def store(self, file):
        """ The main entry point to store a file using this scheme. """
        block, peer_uids = self.handshake_store(file)

        # ordered list of shards
        shards = self.shard(block)
        shards = self.introduce_redundancy(shards)
        self.stripe(shards, peer_uids)
