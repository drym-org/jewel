import Pyro5.api
import base64
from collections import defaultdict
from itertools import cycle
from random import choice
from .base import StorageScheme
from ..checksum import compute_checksum
from ..models import Block
from ..block import make_block, store_block
from ..metadata import make_metadata
from ..networking import peers_available_to_host, hosting_peers
from ..file import write_file


class Hosting(StorageScheme):

    def store(self, file):
        """ The main entry point to store a file using this scheme. """
        block = make_block(file.data)
        metadata = make_metadata(block, file.name)
        peer_uids = peers_available_to_host(metadata)
        host = choice(peer_uids)
        store_block(block, host)

    def get(self, filename):
        """ The main entry point to get a file that was stored using this
        scheme. """
        peers = hosting_peers(filename)
        chosen_peer = peers[0]
        with Pyro5.api.Proxy(chosen_peer) as peer:
            # TODO: need to also retrieve the metadata
            # to compare the checksum
            file_contents = peer.retrieve(filename)
            decoded = base64.decodebytes(bytes(file_contents['data'], 'utf-8'))
            write_file(filename, decoded)
