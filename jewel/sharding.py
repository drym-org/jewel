import Pyro5.api
import os
from collections import defaultdict
from .networking import download_from_peer, hosting_peers
from .checksum import compute_checksum
from .models import Block
from .log import log


def register_shards(block, shards):
    """ Tell the server about the shards for this file so that we it comes time
    to get it back from the network, the server will know what the pieces are
    (and consequently, where to find them). """
    NAME = os.environ.get('JEWEL_NODE_NAME')
    log(NAME, f"Registering shards for {block.checksum}...")
    shard_names = [s.checksum for s in shards]
    with Pyro5.api.Proxy("PYRONAME:jewel.fileserver") as server:
        server.register_shards(block.checksum, shard_names)


def lookup_shards(block_name):
    """ Lookup the shards for this block.

    Note that only blocks can have shards - not files (directly). """
    NAME = os.environ.get('JEWEL_NODE_NAME')
    log(NAME, f"Looking up shards for {block_name}...")
    shards = []
    with Pyro5.api.Proxy("PYRONAME:jewel.fileserver") as server:
        shards = server.lookup_shards(block_name)
        return shards


def download_shards(shards):
    """ Given a list of shards (as block checksums, and presumed to be in
    order), download all of them from the network. """
    peer_shards = defaultdict(list)
    for block_name in shards:
        hosts = hosting_peers(block_name)
        for host_uid in hosts:
            peer_shards[host_uid].append(block_name)
    downloaded_shards = []
    for uid in peer_shards:
        downloaded_shards += download_from_peer(peer_shards[uid], uid)
    downloaded_shards.sort(key=lambda b: shards.index(b.checksum))
    return downloaded_shards


def fuse_shards(shards):
    """ Merge contiguous shards to form a larger block. """
    data = b''.join([s.data for s in shards])
    checksum = compute_checksum(data)
    return Block(checksum, data)
