from random import choice
from .base import RedundantStorageScheme
from ..striped import StripedStorageScheme
from ...file import write_file
from ...models import Block
from ...networking import download, hosting_peers


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
    _M = None

    def __init__(self, number_of_peers):
        self.number_of_peers = number_of_peers
        self.redundancy = number_of_peers

    @property
    def number_of_peers(self):
        return self._N

    @number_of_peers.setter
    def number_of_peers(self, N):
        self._N = N

    @property
    def redundancy(self):
        return self._M

    @redundancy.setter
    def redundancy(self, M):
        self._M = M

    def introduce_redundancy(self, blocks):
        """ Add redundancy to the blocks to facilitate error recovery. """
        # just repeat the block N times, where N
        # is the number of peers
        # we expect there to be exactly one block
        # with this scheme
        return blocks * self.redundancy

    def recover(self, block_name, blocks: list[Block]) -> list[Block]:
        """ Since this is simple duplication, we assume the blocks here are
        just the single block we care about that corresponds to the stored
        file, and return them as is. """
        return blocks

    def store(self, file):
        """ The main entry point to store a file using this scheme. """
        block, peer_uids = self.handshake_store(file)
        blocks = [block]
        blocks = self.introduce_redundancy(blocks)
        self.stripe(blocks, peer_uids)

    def get(self, filename):
        """ The main entry point to get a file that was stored using this
        scheme. """
        block_name = self.handshake_get(filename)
        peers = hosting_peers(block_name)
        # TODO: when peer metadata is added, we can select the
        # "best" peer here instead of a random peer
        chosen_peer = choice(peers)
        block = download(block_name, chosen_peer)
        # we don't need to call recover, but just
        # for uniformity
        block = self.recover(block_name, [block])[0]
        # write it with the original filename
        # instead of the block name
        write_file(filename, block.data)
