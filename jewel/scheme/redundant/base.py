from ..base import StorageScheme
from abc import abstractmethod


class RedundantStorageScheme(StorageScheme):

    @property
    @abstractmethod
    def redundancy(self):
        pass

    @abstractmethod
    def introduce_redundancy(self, blocks: list) -> list:
        """ Add redundancy to the blocks to facilitate error recovery. """
        pass
