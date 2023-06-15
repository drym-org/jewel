#!/usr/bin/env python
import Pyro5.api
from models import BlockMetadata
from names import unique_name


DISK = 'disk'
NAMESPACE = 'jewel.fileserver'


@Pyro5.api.expose
class FileServer:
    def request(self, metadata):
        m = BlockMetadata(**metadata)
        if not m.name:
            m.name = m.checksum
        # find all registered peers
        ns = Pyro5.api.locate_ns()
        peers = ns.yplookup({"peer"}, return_metadata=False)
        live_peers = []
        print(peers)
        for _, uid in peers.items():
            with Pyro5.api.Proxy(uid) as peer:
                if peer.ping():
                    live_peers.append(uid)
        # ping each of them
        return f"Hello! I've received your request to store {m.name}. The following peers are live: {live_peers}\n"


def main():
    daemon = Pyro5.api.Daemon()
    # register FileServer as a Pyro object
    uri = daemon.register(FileServer)
    # register the object with a name in the name server
    ns = Pyro5.api.locate_ns()
    name = unique_name(NAMESPACE, "")  # TODO: consistency
    ns.register(name, uri, metadata={"fileserver"})
    print("Ready.")
    # start the event loop of the server to wait for calls
    daemon.requestLoop()


if __name__ == '__main__':
    main()
