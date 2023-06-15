#!/usr/bin/env python
import Pyro5.api
import os
from models import BlockMetadata
from checksum import compute_checksum


DISK = 'disk/client'


def make_metadata(filename):
    with open(os.path.join(DISK, filename), 'rb') as f:
        contents = f.read()
        checksum = compute_checksum(contents)
        return BlockMetadata(checksum, name=filename)


def discover(metadata: BlockMetadata):
    """
    The 'handshake' phase where we submit a request to store a file to the file
    server and receive a list of live peers.
    """
    with Pyro5.api.Proxy("PYRONAME:jewel.fileserver") as server:
        return server.request(metadata.__dict__)


def store_file(filename):
    metadata = make_metadata(filename)
    peers = discover(metadata)
    print(peers)


def main():
    # filename = input("What file would you like to store? ").strip()
    filename = "a.txt"
    store_file(filename)


if __name__ == '__main__':
    main()
