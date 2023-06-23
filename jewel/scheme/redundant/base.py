from ..base import StorageScheme
from abc import abstractmethod


class RedundantStorageScheme(StorageScheme):

    """ A storage scheme that duplicates blocks.

    This differs from error recovery in that this is defined over a single
    block, where the block is typically simply duplicated. On the other hand,
    error recovery is defined on a set of blocks, and may generate additional
    blocks that become part of that set.

    For instance, we could have a scheme that adds error recovery shards
    where each shard is also duplicated. """

    @property
    @abstractmethod
    def redundancy(self):
        pass

    # TODO: we do define this on a set of blocks, so maybe it should be merged
    # with ErrorRecoveryScheme after all, and "redundancy" (above) would
    # perhaps only make sense as a property of the naive duplication scheme
    # rather than any redundancy scheme
    @abstractmethod
    def introduce_redundancy(self, blocks: list) -> list:
        """ Add redundancy to the blocks to facilitate error recovery. """
        pass
