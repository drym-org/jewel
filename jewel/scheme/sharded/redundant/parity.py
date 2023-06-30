import os
from .base import RedundantSharding
from ..vanilla import VanillaSharding
from ....sharding import lookup_shards
from ....networking import block_catalog_lookup
from ....block import make_block
from ....bytes import bytes_xor
from ....models import Block
from ....log import log


class ParitySharding(RedundantSharding, VanillaSharding):
    """
    This is identical to vanilla sharding except that it adds a partity shard
    to the regular set of shards.
    """

    name = 'parity'

    def introduce_redundancy(self, blocks: list[Block]) -> list[Block]:
        """ Accepts a set of blocks and generates one or more recovery
        blocks for them. """
        block_contents = [b.data for b in blocks]
        rblock = make_block(bytes_xor(*block_contents))
        return blocks + [rblock]

    def recover(self, block_name, blocks: list[Block]) -> list[Block]:
        """ The input blocks here could be either regular blocks or error
        recovery blocks. This method is responsible for figuring out what
        they are and recover the original data blocks. """
        NAME = os.environ.get('JEWEL_NODE_NAME')
        if len(blocks) < self.number_of_shards:
            raise Exception("Can't recover as more than one block is missing!")
        metadata = [block_catalog_lookup(b.checksum) for b in blocks]
        recovery_metadata = [m for m in metadata if m.is_recovery]
        recovery_block_present = bool(recovery_metadata)
        regular_block_checksums = lookup_shards(block_name)
        if recovery_block_present:
            rblock_checksum = recovery_metadata[0].checksum  # we expect exactly one recovery block
            block_contents = [b.data for b in blocks]
            original_block = make_block(bytes_xor(*block_contents))
            regular_blocks = [b for b in blocks if not b.checksum == rblock_checksum]
            recovered_blocks = regular_blocks + [original_block]
            recovered_blocks.sort(key=lambda b: regular_block_checksums.index(b.checksum))
            log(NAME, f"Recovered block {original_block.checksum} using parity block {rblock_checksum}.")
            return recovered_blocks
        else:
            log(NAME, "Original shards received, no recovery necessary.")
            blocks.sort(key=lambda b: regular_block_checksums.index(b.checksum))
            return blocks
