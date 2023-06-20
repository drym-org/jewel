#!/usr/bin/env python
import Pyro5.api
from models import BlockMetadata
from names import unique_name
from networking import discover_peers
from log import log
from functools import partial


DISK = 'disk'
NAMESPACE = 'jewel.fileserver'
NAME = unique_name(NAMESPACE, "")  # TODO: consistency

log = partial(log, NAME)


@Pyro5.api.expose
class FileServer:
    def peers_available_to_host(self, metadata):
        m = BlockMetadata(**metadata)
        if not m.name:
            m.name = m.checksum
        # find all registered peers
        # for now that's all this does. But
        # we could tailor the response to the
        # details of the request here
        # or cache the result for better
        # performance, etc.
        return discover_peers(NAME)

    def hosting_peers(self, filename):
        # find all peers currently hosting this file
        peers_dict = discover_peers(NAME)
        peers = list(peers_dict.keys())
        hosts = []
        for peer_name in peers:
            with Pyro5.api.Proxy(f"PYRONAME:{peer_name}") as peer:
                if peer.has_file(filename):
                    hosts.append(peer_name)
        # kind of kludgy but we're just getting the "sub-dict" of the peer dict
        # containing only those peers that are hosting the file
        hosts = {k: v for k, v in peers_dict.items() if k in hosts}
        return hosts


def main():
    daemon = Pyro5.api.Daemon()
    # register FileServer as a Pyro object
    uri = daemon.register(FileServer)
    # register the object with a name in the name server
    ns = Pyro5.api.locate_ns()
    ns.register(NAME, uri, metadata={"fileserver"})
    log("Ready.")
    # start the event loop of the server to wait for calls
    daemon.requestLoop()


if __name__ == '__main__':
    main()
