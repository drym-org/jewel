#!/usr/bin/env python
import Pyro5.api
from Pyro5.errors import CommunicationError
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
        for name, uid in peers.items():
            with Pyro5.api.Proxy(uid) as peer:
                # ping each of them
                try:
                    peer.ping()
                except CommunicationError:
                    ns.remove(name)
                else:
                    live_peers.append(uid)
        print(live_peers)
        return live_peers


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
