from abc import abstractmethod
from ..base import StorageScheme
from ...models import Block


class RedundantStorageScheme(StorageScheme):

    """ A storage scheme that duplicates blocks.

    This differs from error recovery in that this is defined over a single
    block, where the block is typically simply duplicated. On the other hand,
    error recovery is defined on a set of blocks, and may generate additional
    blocks that become part of that set.

    For instance, we could have a scheme that adds error recovery shards
    where each shard is also duplicated. """

    @abstractmethod
    def introduce_redundancy(self, blocks: list) -> list:
        """ Add redundancy to the blocks to facilitate error recovery. """
        pass

    @abstractmethod
    def recover(self, block_name, blocks: list[Block]) -> list[Block]:
        """ The input blocks here could be either regular blocks or error
        recovery blocks. This method is responsible for figuring out what
        they are and recover the original data blocks. """
        pass
