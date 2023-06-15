#!/usr/bin/env python
import Pyro5.api
import os
import base64
from models import BlockMetadata
from checksum import compute_checksum
from names import unique_name


DISK = 'disk'
# every node on the network needs to have a distinct name
# so we define namespaces and derive the final name by
# appending the name of the current directory
NAMESPACE = 'jewel.peer'


def write_file(filename, contents):
    with open(os.path.join(DISK, filename), 'wb') as f:
        f.write(contents)


@Pyro5.api.expose
class Peer:
    def store(self, metadata, contents):
        m = BlockMetadata(**metadata)
        if not m.name:
            m.name = m.checksum
        with open(os.path.join(DISK, m.name), 'wb') as f:
            decoded = base64.decodebytes(bytes(contents['data'], 'utf-8'))
            checksum = compute_checksum(decoded)
            assert checksum == m.checksum
            write_file(m.name, decoded)
            return f"Hello! I've saved {m.name}.\n"

    def ping(self):
        return True


def main():
    daemon = Pyro5.api.Daemon()
    # register Peer as a Pyro object
    uri = daemon.register(Peer)
    # register the object with a name in the name server
    ns = Pyro5.api.locate_ns()
    pwd = os.path.basename(os.getcwd())
    name = unique_name(NAMESPACE, pwd)
    ns.register(name, uri, metadata={"peer"})
    print("Ready.")
    # start the event loop of the server to wait for calls
    daemon.requestLoop()


if __name__ == '__main__':
    main()
