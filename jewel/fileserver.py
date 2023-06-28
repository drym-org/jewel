#!/usr/bin/env python
import Pyro5.api
import os
import json
from functools import partial
from .names import unique_name
from .networking import discover_peers
from .models import BlockMetadata
from .log import log


# TODO: now that the live folder doesn't contain any code
# we don't really need a disk folder and can just put files
# in the designated peer/filesystem folder, i.e. CWD
# but just in case these scripts are accidentally run in the
# wrong CWD, this would be an added safeguard against
# clobbering local files, so we retain it.
DISK = 'disk'
INDEX = 'index.json'
CATALOG = 'catalog.json'
BLOCKTREE = 'blocktree.json'
NAMESPACE = 'jewel.fileserver'
NAME = unique_name(NAMESPACE, "")  # TODO: consistency
# so that all logs by this process show
# where they're coming from
os.environ["JEWEL_NODE_NAME"] = NAME

log = partial(log, NAME)

# There are 3 main data structures on the fileserver:
#  1. The index, which is a mapping of filenames to blocks.
#     Blocks are identified and named by their contents (via a checksum)
#     so that two files with different names but the same contents
#     would correspond to the same block. There is also a corresponding
#     block catalog that maps block names to block metadata including filenames
#     and whether the block is a regular or a recovery block
#  2. The blocktree, which is a mapping of blocks to other blocks
#     that are its "shards."
#  3. The block book, which is a mapping of blocks to peers
#     hosting them. Currently, this isn't implemented and we
#     just poll all peers each time a file is requested.


def load_from_json_file(filename):
    data = {}
    path = os.path.join(DISK, filename)
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
    return data


def load_index():
    return load_from_json_file(INDEX)


def load_catalog():
    return load_from_json_file(CATALOG)


def load_blocktree():
    return load_from_json_file(BLOCKTREE)


def persist_to_json_file(data, filename):
    path = os.path.join(DISK, filename)
    with open(path, 'w') as f:
        json.dump(data, f)


def persist_index(index):
    persist_to_json_file(index, INDEX)


def persist_catalog(catalog):
    persist_to_json_file(catalog, CATALOG)


def persist_blocktree(blocktree):
    persist_to_json_file(blocktree, BLOCKTREE)


index = load_index()
catalog = load_catalog()
# TODO: we may need more utility functions mapping
# between "filespace" and "blockspace"
blocktree = load_blocktree()


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
            return index[filename]
        except KeyError:
            log(f"Unknown file {filename}!")

    def block_catalog_lookup(self, block_name):
        """ Look up a block in the block catalog. This contains information
        like the checksum and whether the block is a regular block or a
        recovery block. """
        try:
            return catalog[block_name]
        except KeyError:
            log(f"Unknown block {block_name}!")

    def peers_available_to_host(self, metadata):
        """ Identify all peers available to host a file that a client desires
        to store on the network. """
        m = BlockMetadata(**metadata)
        if m.name != m.checksum:
            # this is a named block, i.e. a file that a user cares about
            # so we retain a mapping of it to its block name so that
            # clients may refer to it using the filename rather than the
            # block name
            index[m.name] = m.checksum
            # TODO: use sqlite
            persist_index(index)
        # record an entry for this block in the block catalog
        catalog[m.checksum] = m.__dict__
        persist_catalog(catalog)
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

    def register_shards(self, block_name, shards):
        """ Record shards for a block (as reported by a peer) in the
        blocktree. This will allow us to know what the pieces of a file are and
        also, by consulting the block book (or simply polling peers), where to
        find them. """
        number_of_shards = len(shards)
        shards = [BlockMetadata(**s) for s in shards]
        if number_of_shards == 0:
            log("Warning: there's no sense in registering _no_ shards for "
                f"{block_name}, even though it isn't an error. Not recording "
                "shards.")
            return
        if len(shards) == 1 and shards[0].checksum == block_name:
            log(f"Error: {block_name} cannot be treated as a shard of itself!")
            return

        shard_names = [s.checksum for s in shards]
        if block_name in blocktree:
            previous_shards = blocktree[block_name]
            if previous_shards != shard_names:
                log("Warning: reported shards do not match existing shards. "
                    "Using the new shards...")

        # record an entry for this block in the block catalog
        for shard in shards:
            catalog[shard.checksum] = shard.__dict__
        persist_catalog(catalog)
        # add it to the block tree
        blocktree[block_name] = shard_names
        # TODO: use sqlite
        persist_blocktree(blocktree)
        log(f"Registered shards {shards} for {block_name}.")

    def lookup_shards(self, block_name):
        """ Lookup shards for a given block.

        Returns a list of the checksums of the shards."""
        shards = blocktree.get(block_name)
        if not shards:
            log(f"Warning: No shards found for {block_name}.")
        log(f"Found shards {shards} for {block_name}.")
        return shards


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
