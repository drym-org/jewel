from ..base import StorageScheme
from abc import abstractmethod


class ShardedStorageScheme(StorageScheme):

    @abstractmethod
    def shard(self, file) -> list:
        """ Divide the input file into non-overlapping blocks. """
        pass
