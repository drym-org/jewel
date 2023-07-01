from ..base import StorageScheme
from abc import abstractmethod
from ...sharding import lookup_shards, download_shards, fuse_shards, create_shards, register_shards
from ...file import write_file
from ...block import make_block
from ...metadata import make_metadata


class ShardedStorageScheme(StorageScheme):

    """ A storage scheme where a file is divided into shards and then
    reconstituted from them.

    Typically, these shards would be striped across many peers in the
    network (see "striped" scheme)."""

    @property
    @abstractmethod
    def number_of_shards(self):
        pass

    def shard(self, block) -> list:
        """ Divide the input file into non-overlapping blocks. """
        shards = create_shards(block.data, self.number_of_shards)
        shards = [make_block(s) for s in shards]
        # could potentially provide a size as an override instead of
        # computing it independently for each shard
        shard_mds = [make_metadata(s) for s in shards]
        register_shards(block, shard_mds)
        return shards

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
