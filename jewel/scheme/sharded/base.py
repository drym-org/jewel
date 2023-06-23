from ..base import StorageScheme
from abc import abstractmethod
from ...sharding import lookup_shards, download_shards, fuse_shards
from ...file import write_file


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
