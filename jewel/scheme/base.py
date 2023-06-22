from abc import ABC, abstractmethod
from ..networking import block_name_for_file, hosting_peers, peers_available_to_host
from ..block import make_block
from ..metadata import make_metadata


class StorageScheme(ABC):

    name = ''

    def handshake_store(self, file):
        block = make_block(file.data)
        metadata = make_metadata(block, file.name)
        peer_uids = peers_available_to_host(metadata)
        return block, peer_uids

    def handshake_get(self, filename):
        block_name = block_name_for_file(filename)
        if not block_name:
            raise FileNotFoundError
        peers = hosting_peers(block_name)
        return block_name, peers

    @abstractmethod
    def store(self, filename, contents, peer_uids):
        """ The main entry point to store a file using this scheme. """
        pass

    @abstractmethod
    def get(self, filename):
        """ The main entry point to get a file that was stored using this
        scheme. """
        pass
