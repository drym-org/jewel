#!/usr/bin/env python
import Pyro5.api
import os
import json
from functools import partial
from .names import unique_name
from .networking import discover_peers
from .models import BlockMetadata
from .log import log


DISK = 'disk'
FILESYSTEM = 'filesystem.json'
NAMESPACE = 'jewel.fileserver'
NAME = unique_name(NAMESPACE, "")  # TODO: consistency
# so that all logs by this process show
# where they're coming from
os.environ["JEWEL_NODE_NAME"] = NAME

log = partial(log, NAME)


def load_filesystem():
    filesystem = {}
    if os.path.exists(FILESYSTEM):
        with open(FILESYSTEM, 'r') as f:
            filesystem = json.load(f)
    return filesystem


def persist_filesystem(filesystem):
    with open(FILESYSTEM, 'w') as f:
        json.dump(filesystem, f)


filesystem = load_filesystem()


@Pyro5.api.expose
class FileServer:
    """ Fantastic files and where to find them. """

    def block_name_for_file(self, filename):
        """ Transactions with the fileserver are typically in terms of block
        name rather than filename, so we get the block name for a file first as
        part of any communications about it.

        Every file has a corresponding block, but not every block is (an
        entire) file. More than one file may correspond to the same block if
        they contain the same data.

        The filesystem internally only cares about blocks. """
        try:
            return filesystem[filename]
        except KeyError:
            log(f"Unknown file {filename}!")

    def peers_available_to_host(self, metadata):
        """ Identify all peers available to host a file that a client desires
        to store on the network. """
        m = BlockMetadata(**metadata)
        if m.name != m.checksum:
            # this is a named block, i.e. a file that a user cares about
            # so we retain a mapping of it to its block name so that
            # clients may refer to it using the filename rather than the
            # block name
            filesystem[m.name] = m.checksum
            # TODO: use sqlite
            persist_filesystem(filesystem)
        # find all registered peers
        # for now that's all this does. But
        # we could tailor the response to the
        # details of the request here
        # or cache the result for better
        # performance, etc.
        return discover_peers()

    def hosting_peers(self, block_name):
        """ Identify all peers hosting a given block. The block name is the
        checksum of the contents of the block -- not a simple
        filename. Typically, the client first asks the fileserver the block
        name for a particular filename as the first step of the handshake, and
        only then invokes this interface. Filenames are only relevant at the
        initial and final stages of interaction with the filesystem, and
        internally, the operation is entirely in terms of blocks.

        Currently, we poll all peers to see who has the block, but, TODO: it
        would be better to maintain a 'block book' mapping blocks to hosting
        peers, for performance. This would require peers to notify the server
        whenever they receive a new file."""
        # find all peers currently hosting this file
        peers_dict = discover_peers()
        peers = list(peers_dict.keys())
        hosts = []
        for peer_name in peers:
            with Pyro5.api.Proxy(f"PYRONAME:{peer_name}") as peer:
                if peer.has_block(block_name):
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
