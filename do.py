#!/usr/bin/env python
import Pyro5.api


def main():
    # filename = input("What file would you like to store? ").strip()
    # TODO: loop to select (1) peer (2) file
    # Add logging to peer and fileserver to include its name
    filename = "a.txt"
    with Pyro5.api.Proxy("PYRONAME:jewel.peer.peer") as peer:
        peer.make_request(filename)


if __name__ == '__main__':
    main()
