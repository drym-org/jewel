#!/usr/bin/env python
import Pyro5.api
import os
from models import Metadata
from hashlib import sha1


DISK = 'disk/client'


def main():
    filename = input("What file would you like to store? ").strip()

    with Pyro5.api.Proxy("PYRONAME:example.peer") as peer:
        with open(os.path.join(DISK, filename), 'rb') as f:
            contents = f.read()
            checksum = sha1()
            checksum.update(contents)
            m = Metadata(filename, checksum.hexdigest())
            print(peer.store(m.__dict__, contents))


if __name__ == '__main__':
    main()
