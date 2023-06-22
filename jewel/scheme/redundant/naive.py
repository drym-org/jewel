import Pyro5.api
import base64
from random import choice
from .base import RedundantStorageScheme
from ..striped import StripedStorageScheme
from ...block import make_block
from ...metadata import make_metadata
from ...file import write_file
from ...networking import download


class NaiveDuplication(RedundantStorageScheme, StripedStorageScheme):
    """
    This scheme adds redundancy to increase the availability of the file by
    simply duplicating the file across N peers. It differs from the "hosting"
    scheme in that it stores the file on N peers instead of just one.

    To store the file, we discover live peers, select N of them, and store a
    copy of the file on each of them ("stripe" the copies across the peers).
    To retrieve the file, we discover all hosting peers and download the file
    from one (any) of them.
    """

    name = 'naive'

    _N = None

    def __init__(self, number_of_peers):
        self.number_of_peers = number_of_peers

    @property
    def number_of_peers(self):
        return self._N

    @number_of_peers.setter
    def number_of_peers(self, N):
        self._N = N

    def introduce_redundancy(self, blocks):
        """ Add redundancy to the blocks to facilitate error recovery. """
        # just repeat the block N times, where N
        # is the number of peers
        # we expect there to be exactly one block
        # with this scheme
        block = blocks[0]
        return [block for _i in range(self.number_of_peers)]

    def store(self, file):
        """ The main entry point to store a file using this scheme. """
        block, peer_uids = self.handshake_store(file)
        blocks = [block]
        blocks = self.introduce_redundancy(blocks)
        self.stripe(blocks, peer_uids)
        # TODO: store filename: root_block_checksum on FS
        # TODO: store block checksum: [block_checksum]-or-peer_uid/name
        # try to implement the block tree and file dir
        # in a short feedback loop - in REPL for instance
        # note two files with different names but the same contents would reuse

    def get(self, filename):
        """ The main entry point to get a file that was stored using this
        scheme. """
        block_name, peers = self.handshake_get(filename)
        # TODO: when peer metadata is added, we can select the
        # "best" peer here instead of a random peer
        chosen_peer = choice(peers)
        block = download(block_name, chosen_peer)
        # write it with the original filename
        # instead of the block name
        write_file(filename, block.data)
