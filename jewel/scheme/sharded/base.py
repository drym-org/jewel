from ..base import StorageScheme
from abc import abstractmethod


class ShardedStorageScheme(StorageScheme):

    @property
    @abstractmethod
    def number_of_shards(self):
        pass

    @abstractmethod
    def shard(self, block) -> list:
        """ Divide the input file into non-overlapping blocks. """
        pass
