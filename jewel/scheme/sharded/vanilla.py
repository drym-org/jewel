from .base import ShardedStorageScheme
from ..striped import StripedStorageScheme
from ...sharding import register_shards, lookup_shards, download_shards, fuse_shards
from ...file import write_file
from ...block import make_block
from io import BytesIO


class VanillaSharding(ShardedStorageScheme, StripedStorageScheme):
    """
    This scheme splits the original file into K pieces or "shards" before
    storing them on N hosts. On its own, there is no redundancy entailed
    here. The point of sharding is to gain the flexibility to customize aspects
    of storage and retrieval, including the use of nontrivial error recovery
    schemes and downloading strategies.

    To store the file, we discover live peers, select N of them, shard the file
    into K pieces, and distribute ("stripe") the K shards across the N peers.
    To retrieve the file, we lookup the shards for the file (via the
    fileserver), discover the peers hosting each shard, and download each shard
    from its hosting peer. Finally, we reconstitute the file by concatenating
    the shards, verifying the checksum with the fileserver, and then saving it.

    Note that this isn't the simplest possible sharding scheme, since it does
    use striping. We could have sharding and put all the shards on the same
    host, but that would be exactly equivalent to simple hosting without
    sharding.
    """

    name = 'vanilla'

    _N = None
    _K = None

    def __init__(self, number_of_peers, number_of_shards):
        self.number_of_peers = number_of_peers
        self.number_of_shards = number_of_shards

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

    def store(self, file):
        """ The main entry point to store a file using this scheme. """
        block, peer_uids = self.handshake_store(file)

        # ordered list of shards
        shards = self.shard(block)
        self.stripe(shards, peer_uids)

    def get(self, filename):
        """ The main entry point to get a file that was stored using this
        scheme. """
        # TODO: this handshake asks which peers have the file
        # but we don't need to do that yet with sharding
        block_name, _ = self.handshake_get(filename)
        shards = lookup_shards(block_name)  # checksums
        shards = download_shards(shards)  # blocks
        block = fuse_shards(shards)
        assert block_name == block.checksum
        # write it with the original filename
        # instead of the block name
        write_file(filename, block.data)