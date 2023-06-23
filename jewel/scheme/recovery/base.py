from abc import ABC, abstractmethod
from ...models import Block


class ErrorCorrectionScheme(ABC):

    """ Typically, an error correction scheme will be defined on a set of
    shards of a file, but as the implementation operates simply on a set of
    blocks rather than on something more specific like files or shards, we
    could use the same implementation across a group of multiple files. """

    @abstractmethod
    def make_recovery_blocks(self, blocks: list[Block]) -> list[Block]:
        """ Accepts a set of blocks and generates one or more recovery
        blocks for them. """
        pass

    @abstractmethod
    def recover(self, block_name, blocks: list[Block]) -> list[Block]:
        """ The input blocks here could be either regular blocks or error
        recovery blocks. This method is responsible for figuring out what
        they are and recover the original data blocks. """
        pass
