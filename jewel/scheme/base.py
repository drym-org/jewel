from abc import ABC, abstractmethod


class StorageScheme(ABC):

    @property
    @abstractmethod
    def number_of_peers(self):
        pass

    @abstractmethod
    def introduce_redundancy(self, blocks):
        """ Add redundancy to the blocks to facilitate error recovery. """
        pass

    @abstractmethod
    def allocate(self, blocks, hosts) -> dict:
        """ Allocate blocks to hosts. """
        pass

    @abstractmethod
    def store(self, filename, contents, peer_uids):
        """ The main entry point to store a file using this scheme. """
        pass

    @abstractmethod
    def get(self, filename, contents, peer_uids):
        """ The main entry point to get a file that was stored using this
        scheme. """
        pass
