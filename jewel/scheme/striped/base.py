from ..base import StorageScheme
from abc import abstractmethod


class StripedStorageScheme(StorageScheme):

    @property
    @abstractmethod
    def number_of_peers(self):
        pass

    @abstractmethod
    def allocate(self, blocks: list, hosts: list) -> dict:
        """ Allocate blocks to hosts. """
        pass
