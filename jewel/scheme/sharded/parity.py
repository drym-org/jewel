import os
from random import sample
from .vanilla import VanillaSharding
from ..recovery import ErrorCorrectionScheme
from ...sharding import download_shards, fuse_shards, lookup_shards
from ...block import make_block
from ...bytes import bytes_xor
from ...models import Block
from ...recovery import lookup_recovery_blocks, register_recovery_blocks
from ...file import write_file
from ...log import log


class ParitySharding(VanillaSharding, ErrorCorrectionScheme):
    """
    This is identical to vanilla sharding except that it adds a partity shard
    to the regular set of shards.
    """

    name = 'parity'

    def make_recovery_blocks(self, block, blocks: list[Block]) -> list[Block]:
        """ Accepts a set of blocks and generates one or more recovery
        blocks for them. """
        block_contents = [b.data for b in blocks]
        rblock = make_block(bytes_xor(*block_contents))
        register_recovery_blocks(block, [rblock])
        return [rblock]

    def recover(self, block_name, blocks: list[Block]) -> list[Block]:
        """ The input blocks here could be either regular blocks or error
        recovery blocks. This method is responsible for figuring out what
        they are and recover the original data blocks. """
        NAME = os.environ.get('JEWEL_NODE_NAME')
        if len(blocks) < self.number_of_shards:
            raise Exception("Can't recover as more than one block is missing!")
        rblock_checksum = lookup_recovery_blocks(block_name)[0] # we expect exactly one recovery block
        received_checksums = [block.checksum for block in blocks]
        regular_block_checksums = lookup_shards(block_name)
        if rblock_checksum in received_checksums:
            block_contents = [b.data for b in blocks]
            original_block = make_block(bytes_xor(*block_contents))
            regular_blocks = [b for b in blocks if not b.checksum == rblock_checksum]
            recovered_blocks = regular_blocks + [original_block]
            recovered_blocks.sort(key=lambda b: regular_block_checksums.index(b.checksum))
            log(NAME, f"Recovered block {original_block.checksum} using parity block {rblock_checksum}.")
            return recovered_blocks
        else:
            log(NAME, f"Original shards received, no recovery necessary.")
            blocks.sort(key=lambda b: regular_block_checksums.index(b.checksum))
            return blocks

    def store(self, file):
        """ The main entry point to store a file using this scheme. """
        block, peer_uids = self.handshake_store(file)

        # ordered list of shards
        shards = self.shard(block)
        rblock = self.make_recovery_blocks(block, shards)[0]
        all_blocks = shards + [rblock]
        self.stripe(all_blocks, peer_uids)

    def get(self, filename):
        """ The main entry point to get a file that was stored using this
        scheme. """
        # TODO: this handshake asks which peers have the file
        # but we don't need to do that yet with sharding
        block_name, _ = self.handshake_get(filename)
        shards = lookup_shards(block_name)  # checksums
        rblock = lookup_recovery_blocks(block_name)[0]
        all_shards = shards + [rblock]
        shards = sample(all_shards, self.number_of_shards)
        shards = download_shards(shards)  # blocks
        shards = self.recover(block_name, shards)
        block = fuse_shards(shards)
        assert block_name == block.checksum
        # write it with the original filename
        # instead of the block name
        write_file(filename, block.data)
