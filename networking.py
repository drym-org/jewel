import Pyro5.api
from Pyro5.errors import CommunicationError
from log import log


def discover_peers(caller_name):
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
