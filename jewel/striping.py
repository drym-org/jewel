from .block import store_block


def stripe_blocks(peer_uid, blocks):
    """ Distribute blocks across peers. """
    for block in blocks:
        store_block(block, peer_uid)
