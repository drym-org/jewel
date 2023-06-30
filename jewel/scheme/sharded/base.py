from ..base import StorageScheme
from abc import abstractmethod
from ...sharding import lookup_shards, download_shards, fuse_shards
from ...file import write_file
from ...block import make_block


class ShardedStorageScheme(StorageScheme):

    """ A storage scheme where a file is divided into shards and then
    reconstituted from them.

    Typically, these shards would be striped across many peers in the
    network (see "striped" scheme)."""

    @property
    @abstractmethod
    def number_of_shards(self):
        pass

    @abstractmethod
    def shard(self, block) -> list:
        """ Divide the input file into non-overlapping blocks. """
        pass

    def get(self, filename):
        """ The main entry point to get a file that was stored using this
        scheme. """
        block_name = self.handshake_get(filename)
        shards = lookup_shards(block_name)  # checksums
        shards = download_shards(shards)  # blocks
        shard_data = [s.data for s in shards]
        block_data = fuse_shards(shard_data)
        block = make_block(block_data)
        assert block_name == block.checksum
        # write it with the original filename
        # instead of the block name
        write_file(filename, block.data)
