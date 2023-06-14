#!/usr/bin/env python
import Pyro5.api
import os
import base64
from models import Metadata
from checksum import compute_checksum


DISK = 'disk/server'


@Pyro5.api.expose
class Peer:
    def store(self, metadata, contents):
        m = Metadata(**metadata)
        with open(os.path.join(DISK, m.filename), 'wb') as f:
            decoded = base64.decodebytes(bytes(contents['data'], 'utf-8'))
            checksum = compute_checksum(decoded)
            assert checksum == m.checksum
            return f"Hello! I've saved {m.filename}.\n"


def main():
    daemon = Pyro5.api.Daemon()             # make a Pyro daemon
    uri = daemon.register(Peer)             # register the peer as a Pyro object
    ns = Pyro5.api.locate_ns()              # find the name server
    ns.register("example.peer", uri)        # register the object with a name in the name server
    print("Ready.")
    daemon.requestLoop()                    # start the event loop of the server to wait for calls


if __name__ == '__main__':
    main()
