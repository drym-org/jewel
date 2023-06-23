import Pyro5.api
import os
from .log import log


def register_recovery_blocks(block, rblocks):
    """ Tell the server about the recovery blocks for this block so that when
    it comes time to get it back from the network, the server will know what
    the pieces are (and consequently, where to find them). """
    NAME = os.environ.get('JEWEL_NODE_NAME')
    log(NAME, f"Registering recovery blocks for {block.checksum}...")
    block_names = [s.checksum for s in rblocks]
    with Pyro5.api.Proxy("PYRONAME:jewel.fileserver") as server:
        server.register_recovery_blocks(block.checksum, block_names)


def lookup_recovery_blocks(block_name):
    """ Lookup the recovery blocks for this block.

    Note that only blocks can have recovery blocks - not files (directly). """
    NAME = os.environ.get('JEWEL_NODE_NAME')
    log(NAME, f"Looking up recovery blocks for {block_name}...")
    blocks = []
    with Pyro5.api.Proxy("PYRONAME:jewel.fileserver") as server:
        blocks = server.lookup_recovery_blocks(block_name)
        return blocks
