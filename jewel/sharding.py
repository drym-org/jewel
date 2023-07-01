import Pyro5.api
import os
from sys import exit
from io import BytesIO
from itertools import cycle
from collections import defaultdict
from math import ceil
from .networking import download_from_peer, hosting_peers
from .log import log
from .bytes import pad_bytes, unpad, concat


def create_shards_of_length(data, shard_length, pad=True):
    """ Divide some data (in the form of bytes) into shards of a specific
    size. """
    shards = []
    f = BytesIO(data)
    data = f.read(shard_length)
    while data:
        shards.append(data)
        data = f.read(shard_length)
    # the final shard may be shorter than the others
    # so we pad it to the desired shard length with null bytes
    if pad:
        last_block = shards.pop()
        padding = shard_length - len(last_block)
        last_block = pad_bytes(last_block, padding)
        shards.append(last_block)
        for d in shards:
            assert len(d) == shard_length
    return shards


def create_shards(data, number_of_shards, pad=True):
    """ Divide some data (in the form of bytes) into a given number of
    non-overlapping contiguous bytestrings. """
    block_length = len(data)
    # we round up here since otherwise we'd have a final
    # shard with almost no data and all padding, and it
    # would be one more shard than we wanted
    shard_length = ceil(block_length / number_of_shards)
    shards = create_shards_of_length(data, shard_length, pad)
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


def shard_index(shard, shards):
    """ Given the full (ordered) list of shards and a block corresponding to a
    shard, return the index of the shard. """
    return shards.index(shard.checksum)


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
            exit(1)
        shards_remaining = peer_shards[uid]
        while shards_remaining:
            chosen_shard = shards_remaining.pop()
            if chosen_shard in shards:
                new_peer_shards[uid].append(chosen_shard)
                shards.remove(chosen_shard)
                break
    log(NAME, f"Prepared download itinerary: {new_peer_shards}.")
    return new_peer_shards


def available_shards(block_name):
    """ Find which shards are currently available for a given block.

    Ideally we should return the hosts as well, so that we can download from
    those peers on the next step instead of polling for hosts again in
    download_shards. """
    shard_checksums = lookup_shards(block_name)
    available = []
    for checksum in shard_checksums:
        hosts = hosting_peers(checksum)
        if hosts:
            available.append(checksum)
    return available


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


def fuse_shards(shards, strip=True):
    """ Merge contiguous shards to form a larger block. """
    # strip any null padding that may have been added
    # before joining the shards
    if strip:
        shards = [unpad(s) for s in shards]
    data = concat(shards)
    return data
