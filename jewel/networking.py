import Pyro5.api
from Pyro5.errors import CommunicationError
from .models import BlockMetadata
from .log import log


def discover_peers(caller_name=None):
    """ Query the nameserver to get a list of all known peers.
    The caller_name argument is the name of the network entity invoking this
    function. This is to facilitate clear logging.
    """
    ns = Pyro5.api.locate_ns()
    peers = ns.yplookup({"peer"}, return_metadata=False)
    live_peers = {}
    for name, uid in peers.items():
        with Pyro5.api.Proxy(uid) as peer:
            # ping each of them
            try:
                peer.ping()
            except CommunicationError:
                log(caller_name,
                    f"Peer {name} not responding. "
                    "Asked the nameserver to remove it.")
                ns.remove(name)
            else:
                live_peers[name] = uid
    log(caller_name, f"Discovered peers {live_peers}")
    return live_peers


def peers_available_to_host(metadata: BlockMetadata, caller_name=None):
    """
    The 'handshake' phase where we submit a request to store a file to the file
    server and receive a list of live peers (as UIDs).
    """
    log(caller_name, f"Requesting to store {metadata.checksum}...")
    with Pyro5.api.Proxy("PYRONAME:jewel.fileserver") as server:
        peers = server.peers_available_to_host(metadata.__dict__)
        if caller_name in peers:
            del peers[caller_name]
        log(caller_name, f"Peers available to host {metadata.checksum} are {peers}")
        return list(peers.values())


def hosting_peers(filename):
    """ The filename here could be any "block" name. When we add sharding, a
    shard would have a name (its SHA1 hash, by default), and we would pass that
    here to retrieve that shard just like any other file.
    """
    log(f"Requesting to get {filename}...")
    with Pyro5.api.Proxy("PYRONAME:jewel.fileserver") as server:
        peers = server.hosting_peers(filename)
        # since we're checking whether we have the file before asking the
        # server, we don't need to check again here that we aren't in the
        # returned list of peers hosting this file (as we do in
        # peers_available_to_host)
        log(f"Peers hosting {filename} are {peers}")
        return list(peers.values())
