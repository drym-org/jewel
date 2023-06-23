from abc import abstractmethod
from ..base import StorageScheme
from ...striping import round_robin_striping
from ...networking import upload


class StripedStorageScheme(StorageScheme):

    """ A storage scheme that stores blocks across multiple peers.  This could
    be entire files duplicated, or shards of a file distributed across the
    peers. """

    @property
    @abstractmethod
    def number_of_peers(self):
        pass

    def stripe(self, blocks: list, host_uids: list) -> dict:
        """ Allocate blocks to hosts. """
        peer_allocation = round_robin_striping(host_uids, blocks)
        for peer_uid in peer_allocation:
            peer_blocks = peer_allocation[peer_uid]  # list of blocks
            for block in peer_blocks:
                upload(block, peer_uid)
