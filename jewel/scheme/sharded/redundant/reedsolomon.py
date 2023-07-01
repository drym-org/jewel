import os
from reedsolo import RSCodec, ReedSolomonError
from math import ceil
from collections import defaultdict
from .base import RedundantSharding
from ..vanilla import VanillaSharding
from ....sharding import fuse_shards, lookup_shards, create_shards, shard_index, register_shards, create_shards_of_length
from ....block import make_block
from ....metadata import make_metadata
from ....models import Block
from ....log import log
from ....list import chunks, tessellate
from ....bytes import null_bytes
from ....sharding import available_shards, download_shards
from random import sample
from ....file import write_file

# TODO: use explicitly
RS_BLOCK_SIZE = 255


def shard_rs_blocks(msg, k):
    shards = []
    for block in chunks(msg, RS_BLOCK_SIZE):
        # TODO: maybe we do need to pad?
        shards.append(create_shards(block, k, pad=False))
    # returns shards as e.g. [1,2,3],[1,2,3],[1,2,3],...
    return shards


class ReedSolomon(RedundantSharding, VanillaSharding):
    """
    In addition to sharding, this encodes the input data using Reed Solomon
    encoding to generate extra error-recovery shards.
    """

    name = 'reedsolomon'

    _J = None
    # Reed-Solomon codec
    rsc = None

    def __init__(self, number_of_peers, number_of_shards, minimum_jewels):
        """ 'Jewels' are RS error-recovery shards. All 'shards' in this scheme are jewels. """
        self.number_of_peers = number_of_peers
        self.number_of_shards = number_of_shards
        self.minimum_jewels = minimum_jewels
        error_tolerance = ceil(((number_of_shards - minimum_jewels) / number_of_shards) * RS_BLOCK_SIZE)
        self.rsc = RSCodec(error_tolerance)

    @property
    def number_of_jewels(self):
        return self._J

    @number_of_jewels.setter
    def number_of_jewels(self, J):
        self._J = J

    def introduce_redundancy(self, _shards):
        """ DUMMY - TODO: fix the class hierarchy or abstract as needed to
        properly capture the difference in operation of RS vs the other
        redundant schemes. Among other things, maybe the recover method should
        return the recovered block rather than recovered shards. """
        return _shards

    def encode(self, data):
        return self.rsc.encode(data)

    def store(self, file):
        """ The main entry point to store a file using this scheme. """
        block, peer_uids = self.handshake_store(file)

        # ordered list of shards
        encoded = self.encode(block.data)
        rs_block_shards = shard_rs_blocks(encoded, self.number_of_shards)
        jewels = tessellate(rs_block_shards)
        jewels = [fuse_shards(j, strip=False) for j in jewels]
        jewels = [make_block(j) for j in jewels]
        jewel_mds = [make_metadata(j, is_recovery=True) for j in jewels]
        register_shards(block, jewel_mds)
        self.stripe(jewels, peer_uids)

    def recover(self, block_name, blocks: list[Block]) -> list[Block]:
        """ The input blocks here could be either regular blocks or error
        recovery blocks. This method is responsible for figuring out what
        they are and recover the original data blocks. """
        NAME = os.environ.get('JEWEL_NODE_NAME')
        if len(blocks) < self.minimum_jewels:
            raise Exception("Can't recover as we need at least {self.minimum_jewels} blocks!")

        jewel_length = len(blocks[0].data)
        # 1. identify the jewels we got by index
        # 2. create J null jewels and put them in the holes
        shard_checksums = lookup_shards(block_name)
        shards_by_index = defaultdict(lambda: null_bytes(jewel_length))
        present_indices = []
        for s in blocks:
            index = shard_index(s, shard_checksums)
            shards_by_index[index] = s.data
            present_indices.append(index)
        arranged_shards = [shards_by_index[i] for i in range(self.number_of_shards)]
        arranged_shards = [create_shards_of_length(s, ceil(RS_BLOCK_SIZE / self.number_of_shards), pad=False) for s in arranged_shards]
        # tessellate
        arranged_shards = tessellate(arranged_shards)
        arranged_shards = [fuse_shards(s, strip=False) for s in arranged_shards]
        # 3. fuse the shards
        masked_codeword = fuse_shards(arranged_shards, strip=False)
        # 4. decode
        missing_indices = list(set(range(self.number_of_shards)) - set(present_indices))
        missing_indices.sort()

        masked_codeword_length = len(masked_codeword)
        number_of_encoded_blocks = ceil(masked_codeword_length / RS_BLOCK_SIZE)
        shard_length = ceil(RS_BLOCK_SIZE / self.number_of_shards)
        erasures = []
        for ib in range(number_of_encoded_blocks):
            for i in missing_indices:
                if ib == number_of_encoded_blocks - 1:
                    max_length = RS_BLOCK_SIZE * number_of_encoded_blocks
                    shard_length = ceil((RS_BLOCK_SIZE - (max_length - masked_codeword_length)) / self.number_of_shards)
                start = ib * RS_BLOCK_SIZE + i * shard_length
                erasures += list(range(start, start + shard_length))

        try:
            decoded = self.rsc.decode(masked_codeword, erase_pos=erasures)
        except ReedSolomonError as e:
            log(NAME, f"Error: {e}")
            raise
        decoded = decoded[0]
        decoded = bytes(decoded)
        original_block = make_block(decoded)

        log(NAME, f"Recovered block {original_block.checksum} using Reed-Solomon.")
        return decoded

    def get(self, filename):
        """ Temporary override - fix class hierarchy. """
        block_name = self.handshake_get(filename)
        shards = available_shards(block_name)  # checksums
        shards = sample(shards, self.minimum_jewels)
        shards = download_shards(shards)  # blocks
        block_data = self.recover(block_name, shards)
        block = make_block(block_data)
        assert block_name == block.checksum
        # write it with the original filename
        # instead of the block name
        write_file(filename, block.data)
