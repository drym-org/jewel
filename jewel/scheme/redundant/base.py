from ..base import StorageScheme
from abc import abstractmethod


class RedundantStorageScheme(StorageScheme):

    @property
    @abstractmethod
    def number_of_peers(self):
        pass

    @abstractmethod
    def allocate(self, blocks, hosts) -> dict:
        """ Allocate blocks to hosts. """
        pass

    @abstractmethod
    def introduce_redundancy(self, blocks):
        """ Add redundancy to the blocks to facilitate error recovery. """
        pass
