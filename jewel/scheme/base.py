from abc import ABC, abstractmethod
from ..networking import block_name_for_file, peers_available_to_host
from ..block import make_block
from ..models import File
from ..metadata import make_metadata


class StorageScheme(ABC):

    name = ''

    def handshake_store(self, file: File):
        """ Create a block for the file we are interested in storing, and get a
        list of peers available to host it.

        The first step in requesting to store a file is to create a block
        because internally, the filesystem's operation is entirely in terms of
        blocks rather than files. Some of these blocks may correspond to full
        files, while others may be shards of files, and still others may be
        stray fragments of files. The filesystem does not know the difference,
        and the relationships of blocks to files is a higher-level concern of
        the storage scheme that is employed in storing and retrieving files,
        which is managed by the peers themselves in coordination with the
        fileserver.
        """
        block = make_block(file.data)
        metadata = make_metadata(block, name=file.name)
        peer_uids = peers_available_to_host(metadata)
        return block, peer_uids

    def handshake_get(self, filename):
        """ Lookup the block corresponding to the filename, and identify peers
        on the network that are hosting the block.

        Note that this only searches for peers hosting the full file. For any
        more nuanced scheme, the peer will issue separate network requests for
        peers hosting blocks corresponding to e.g. shards. So technically, the
        request for hosting peers needn't be part of the handshake at the level
        of the full file, and should only be done when we actually have a block
        we are interested in downloading. """
        block_name = block_name_for_file(filename)
        if not block_name:
            raise FileNotFoundError
        return block_name

    @abstractmethod
    def store(self, filename, contents, peer_uids):
        """ The main entry point to store a file using this scheme. """
        pass

    @abstractmethod
    def get(self, filename):
        """ The main entry point to get a file that was stored using this
        scheme. """
        pass
