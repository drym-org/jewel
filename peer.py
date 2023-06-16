#!/usr/bin/env python
import Pyro5.api
import os
import base64
from models import BlockMetadata
from checksum import compute_checksum
from names import unique_name
from log import log
from functools import partial

DISK = 'disk'
# every node on the network needs to have a distinct name
# so we define namespaces and derive the final name by
# appending the name of the current directory
NAMESPACE = 'jewel.peer'
PWD = os.path.basename(os.getcwd())
NAME = unique_name(NAMESPACE, PWD)

log = partial(log, NAME)


def write_file(filename, contents):
    with open(os.path.join(DISK, filename), 'wb') as f:
        f.write(contents)


def make_metadata(filename, contents):
    checksum = compute_checksum(contents)
    return BlockMetadata(checksum, name=filename)


def file_contents(filename):
    with open(os.path.join(DISK, filename), 'rb') as f:
        return f.read()


def request(metadata: BlockMetadata):
    """
    The 'handshake' phase where we submit a request to store a file to the file
    server and receive a list of live peers.
    """
    log(f"Requesting to store {metadata.name}...")
    with Pyro5.api.Proxy("PYRONAME:jewel.fileserver") as server:
        peers = server.request(metadata.__dict__)
        if NAME in peers:
            del peers[NAME]
        log(peers)
        return list(peers.values())


@Pyro5.api.expose
class Peer:
    def ping(self):
        return True

    def dir(self):
        return os.listdir(DISK)

    def store(self, metadata, contents):
        """ Store a file on this peer (note that this method is called by
        _another_ peer when that peer wants to store the file here)."""
        m = BlockMetadata(**metadata)
        if not m.name:
            m.name = m.checksum
        decoded = base64.decodebytes(bytes(contents['data'], 'utf-8'))
        checksum = compute_checksum(decoded)
        assert checksum == m.checksum
        write_file(m.name, decoded)
        log(f"Hello! I've saved {m.name}.\n")

    def delete(self, filename):
        try:
            os.remove(os.path.join(DISK, filename))
        except FileNotFoundError:
            log(f"{filename} not found!")
        else:
            log(f"{filename} deleted!")

    def make_request(self, filename):
        """ 'Request' is ambiguous, but here we're talking about making a
        request to store a file on the network. """
        try:
            contents = file_contents(filename)
        except FileNotFoundError:
            log(f"{filename} not found!")
        else:
            metadata = make_metadata(filename, contents)
            peers = request(metadata)
            chosen_peer = peers[0]
            with Pyro5.api.Proxy(chosen_peer) as peer:
                peer.store(metadata.__dict__, contents)


def main():
    daemon = Pyro5.api.Daemon()
    # register Peer as a Pyro object
    uri = daemon.register(Peer)
    # register the object with a name in the name server
    ns = Pyro5.api.locate_ns()
    ns.register(NAME, uri, metadata={"peer"})
    log("Ready.")
    # start the event loop of the server to wait for calls
    daemon.requestLoop()


if __name__ == '__main__':
    main()
