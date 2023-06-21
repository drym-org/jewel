import Pyro5.api
import base64
import os
from random import choice
from .base import StorageScheme
from ..block import make_block, store_block
from ..metadata import make_metadata
from ..file import write_file
from ..log import log


class Hosting(StorageScheme):
    """
    The simplest possible network storage scheme, where a single peer is
    selected to host the file.

    To store the file, we discover live peers, select one, and store it there.
    To retrieve the file, we contact the hosting peer and download it.
    """

    def store(self, file):
        """ The main entry point to store a file using this scheme. """
        block, peer_uids = self.handshake_store(file)
        host = choice(peer_uids)
        store_block(block, host)

    def get(self, filename):
        """ The main entry point to get a file that was stored using this
        scheme. """
        NAME = os.environ.get('JEWEL_NODE_NAME')
        block_name, peers = self.handshake_get(filename)
        if len(peers) > 1:
            log(NAME,
                "Warning: Storage scheme is simple hosting "
                "but file was found on more than one (specifically, "
                f"{len(peers)}) hosts!")
        chosen_peer = peers[0]
        with Pyro5.api.Proxy(chosen_peer) as peer:
            # TODO: need to also retrieve the metadata
            # to compare the checksum
            file_contents = peer.retrieve(block_name)
            decoded = base64.decodebytes(bytes(file_contents['data'], 'utf-8'))
            # write it with the original filename
            # instead of the block name
            write_file(filename, decoded)
