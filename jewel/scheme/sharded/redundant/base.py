from random import sample
from ..base import ShardedStorageScheme
from ...striped import StripedStorageScheme
from ...redundant import RedundantStorageScheme
from ....sharding import available_shards, download_shards, fuse_shards, register_shards
from ....file import write_file
from ....block import make_block
from ....metadata import make_metadata


class RedundantSharding(ShardedStorageScheme, StripedStorageScheme, RedundantStorageScheme):

    """ A storage scheme where a file is divided into shards and then
    reconstituted from them.

    Typically, these shards would be striped across many peers in the
    network (see "striped" scheme)."""

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
        scheme.

        This differs from the retrieval strategy for generic sharding schemes
        (i.e. in sharded/base.py) only in that it samples from the full set of
        shards available (since there are recovery shards in addition to the
        original data shards) and then undertakes recovery if it happens to
        download recovery shards. """
        block_name = self.handshake_get(filename)
        shards = available_shards(block_name)  # checksums
        # download any K shards, whether recovery or regular, since we can
        # assume that recovering a regular shard from a recovery shard is a
        # secondary concern (and a much lower cost) to getting the data
        # efficiently from the network. So in practice, we would probably
        # get a random selection of shards here (whichever happen to be the
        # most expedient), and that's why we just randomly select shards from
        # the full set
        # TODO: this is no longer the right thing for RS encoding
        # where we need minimum number instead. We could consider
        # number of shards _as_ the minimum number, and use a different
        # attribute on reedsolomon to hold the total number?
        shards = sample(shards, self.number_of_shards)
        shards = download_shards(shards)  # blocks
        shards = self.recover(block_name, shards)
        shard_data = [s.data for s in shards]  # bytes
        block_data = fuse_shards(shard_data)
        block = make_block(block_data)
        assert block_name == block.checksum
        # write it with the original filename
        # instead of the block name
        write_file(filename, block.data)
