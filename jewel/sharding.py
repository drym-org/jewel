import Pyro5.api
import os
from io import BytesIO
from itertools import cycle
from collections import defaultdict
from .networking import download_from_peer, hosting_peers
from .checksum import compute_checksum
from .models import Block
from .log import log
from .block import make_block

NULL_BYTE = b'\0'


def create_shards(block, number_of_shards):
    """ Divide a block into a given number of non-overlapping contiguous
    blocks. """
    block_length = len(block.data)
    shard_length = int(block_length / number_of_shards)
    shard_data = []
    f = BytesIO(block.data)
    for i in range(number_of_shards - 1):
        # read data to create the first n-1 shards
        data = f.read(shard_length)
        shard_data.append(data)
    # create the final, n'th shard from
    # all of the remaining data
    data = f.read()
    last_block_length = len(data)
    # pad shards with null bytes so they are all the same size
    padding = last_block_length - shard_length
    if padding > 0:
        shard_data = [s + NULL_BYTE * padding for s in shard_data]
    for d in shard_data:
        assert len(d) == last_block_length
    shard_data.append(data)
    shards = [make_block(data) for data in shard_data]
    return shards


def register_shards(block, shard_mds):
    """ Tell the server about the shards for this file so that we it comes time
    to get it back from the network, the server will know what the pieces are
    (and consequently, where to find them). """
    NAME = os.environ.get('JEWEL_NODE_NAME')
    log(NAME, f"Registering shards for {block.checksum}...")
    shard_mds = [s.__dict__ for s in shard_mds]
    with Pyro5.api.Proxy("PYRONAME:jewel.fileserver") as server:
        server.register_shards(block.checksum, shard_mds)


def lookup_shards(block_name):
    """ Lookup the shards for this block.

    Note that only blocks can have shards - not files (directly). """
    NAME = os.environ.get('JEWEL_NODE_NAME')
    log(NAME, f"Looking up shards for {block_name}...")
    shards = []
    with Pyro5.api.Proxy("PYRONAME:jewel.fileserver") as server:
        shards = server.lookup_shards(block_name)
        return shards


def _prepare_download_itinerary(shards, peer_shards):
    """
    If the same shard is present on multiple peers, we want to select peers in
    such a way that they are maximally, i.e. uniformly, utilized. To do this,
    we let the peers "take turns" picking shards until all shards have been
    chosen.
    """
    shards = shards.copy()
    peer_shards = peer_shards.copy()
    NAME = os.environ.get('JEWEL_NODE_NAME')
    new_peer_shards = defaultdict(list)
    for i, uid in enumerate(cycle(peer_shards.keys())):
        if not shards:
            break
        if i > 100:
            log(NAME, "Encountered infinite loop! Exiting...")
        shards_remaining = peer_shards[uid]
        while shards_remaining:
            chosen_shard = shards_remaining.pop()
            if chosen_shard in shards:
                new_peer_shards[uid].append(chosen_shard)
                shards.remove(chosen_shard)
                break
    log(NAME, f"Prepared download itinerary: {new_peer_shards}.")
    return new_peer_shards


def download_shards(shards):
    """ Given a list of shards (as block checksums, and presumed to be in
    order), download all of them from the network. """
    peer_shards = defaultdict(list)
    for block_name in shards:
        hosts = hosting_peers(block_name)
        for host_uid in hosts:
            peer_shards[host_uid].append(block_name)
    peer_shards = _prepare_download_itinerary(shards, peer_shards)
    downloaded_shards = []
    for uid in peer_shards:
        downloaded_shards += download_from_peer(peer_shards[uid], uid)
    downloaded_shards.sort(key=lambda b: shards.index(b.checksum))
    return downloaded_shards


def fuse_shards(shards):
    """ Merge contiguous shards to form a larger block. """
    # strip any null padding that may have been added
    # before joining the shards
    data = b''.join([s.data.strip(NULL_BYTE) for s in shards])
    checksum = compute_checksum(data)
    return Block(checksum, data)
