from abc import ABC, abstractmethod


class StorageScheme(ABC):

    @abstractmethod
    def store(self, filename, contents, peer_uids):
        """ The main entry point to store a file using this scheme. """
        pass

    @abstractmethod
    def get(self, filename, contents, peer_uids):
        """ The main entry point to get a file that was stored using this
        scheme. """
        pass
