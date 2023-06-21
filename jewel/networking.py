import Pyro5.api
import os
import base64
from Pyro5.errors import CommunicationError
from .models import BlockMetadata, Block
from .log import log
from .metadata import make_metadata
from .checksum import compute_checksum


def discover_peers():
    """ Query the nameserver to get a list of all known peers. """
    NAME = os.environ.get('JEWEL_NODE_NAME')
    ns = Pyro5.api.locate_ns()
    peers = ns.yplookup({"peer"}, return_metadata=False)
    live_peers = {}
    for name, uid in peers.items():
        with Pyro5.api.Proxy(uid) as peer:
            # ping each of them
            try:
                peer.ping()
            except CommunicationError:
                log(NAME,
                    f"Peer {name} not responding. "
                    "Asked the nameserver to remove it.")
                ns.remove(name)
            else:
                live_peers[name] = uid
    log(NAME, f"Discovered peers {list(live_peers.keys())}")
    return live_peers


def peers_available_to_host(metadata: BlockMetadata):
    """
    The 'handshake' phase where we submit a request to store a file to the file
    server and receive a list of live peers (as UIDs).
    """
    NAME = os.environ.get('JEWEL_NODE_NAME')
    log(NAME, f"Requesting to store {metadata.checksum}...")
    with Pyro5.api.Proxy("PYRONAME:jewel.fileserver") as server:
        peers = server.peers_available_to_host(metadata.__dict__)
        if NAME in peers:
            del peers[NAME]
        log(NAME, f"Peers available to host {metadata.checksum} are {list(peers.keys())}")
        return list(peers.values())


def hosting_peers(filename):
    """ The filename here could be any "block" name. When we add sharding, a
    shard would have a name (its SHA1 hash, by default), and we would pass that
    here to retrieve that shard just like any other file.
    """
    NAME = os.environ.get('JEWEL_NODE_NAME')
    log(NAME, f"Requesting to get {filename}...")
    with Pyro5.api.Proxy("PYRONAME:jewel.fileserver") as server:
        peers = server.hosting_peers(filename)
        # since we're checking whether we have the file before asking the
        # server, we don't need to check again here that we aren't in the
        # returned list of peers hosting this file (as we do in
        # peers_available_to_host)
        log(NAME, f"Peers hosting {filename} are {list(peers.keys())}")
        return list(peers.values())


def block_name_for_file(filename):
    """ Ask the server if it knows this file and what the block name
    is. Internally to the filesystem, we operate exclusively in terms of blocks
    rather than filenames. """
    NAME = os.environ.get('JEWEL_NODE_NAME')
    log(NAME, f"Querying block name for {filename}...")
    with Pyro5.api.Proxy("PYRONAME:jewel.fileserver") as server:
        block_name = server.block_name_for_file(filename)
        if block_name:
            log(NAME, f"Block name for {filename} is {block_name}")
        else:
            log(NAME, f"{filename} has no block name.")
        return block_name


def download(block_name, peer_uid) -> Block:
    """ Download a block from a peer. """
    with Pyro5.api.Proxy(peer_uid) as peer:
        file_contents = peer.retrieve(block_name)
        decoded = base64.decodebytes(bytes(file_contents['data'], 'utf-8'))
        checksum = compute_checksum(decoded)
        assert checksum == block_name
        return Block(block_name, decoded)


def upload(block, peer_uid, name=None):
    """ This interface represents the "blocks" abstraction layer. It does not
    need to know anything about the storage scheme being employed or about
    sharding. It simply stores a "block" of data (which may happen to be a file
    or a shard at a higher level of abstraction) on some peer."""
    metadata = make_metadata(block, name)
    with Pyro5.api.Proxy(peer_uid) as peer:
        peer.store(metadata.__dict__, block.data)
