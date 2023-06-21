import Pyro5.api
import os
from Pyro5.errors import CommunicationError
from .models import BlockMetadata
from .log import log


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
        log(NAME, f"Block name for {filename} is {block_name}")
        return block_name
