import os
from random import sample
from .vanilla import VanillaSharding
from ..redundant import RedundantStorageScheme
from ...sharding import download_shards, fuse_shards, lookup_shards, register_shards
from ...networking import block_catalog_lookup
from ...block import make_block
from ...bytes import bytes_xor
from ...models import Block
from ...metadata import make_metadata
from ...file import write_file
from ...log import log


class ParitySharding(VanillaSharding, RedundantStorageScheme):
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
            log(NAME, f"Original shards received, no recovery necessary.")
            blocks.sort(key=lambda b: regular_block_checksums.index(b.checksum))
            return blocks

    def store(self, file):
        """ The main entry point to store a file using this scheme. """
        block, peer_uids = self.handshake_store(file)

        # ordered list of shards
        original_shards = self.shard(block)
        shards = self.introduce_redundancy(original_shards)
        regular_shards = [s for s in shards if s in original_shards]
        recovery_shards = [s for s in shards if s not in original_shards]
        regular_shard_mds = [make_metadata(s) for s in regular_shards]
        recovery_shard_mds = [make_metadata(s, is_recovery=True) for s in recovery_shards]
        shard_mds = regular_shard_mds + recovery_shard_mds
        register_shards(block, shard_mds)
        self.stripe(shards, peer_uids)

    def get(self, filename):
        """ The main entry point to get a file that was stored using this
        scheme. """
        block_name = self.handshake_get(filename)
        shards = lookup_shards(block_name)  # checksums
        # download any K shards, whether recovery or regular, since we can
        # assume that recovering a regular shard from a recovery shard is a
        # secondary concern (and a much lower cost) to getting the data
        # efficiently from the network. So in practice, we would probably
        # get a random selection of shards here (whichever happen to be the
        # most expedient), and that's why we just randomly select shards from
        # the full set
        shards = sample(shards, self.number_of_shards)
        shards = download_shards(shards)  # blocks
        shards = self.recover(block_name, shards)
        block = fuse_shards(shards)
        assert block_name == block.checksum
        # write it with the original filename
        # instead of the block name
        write_file(filename, block.data)
