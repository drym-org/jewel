from collections import defaultdict
from itertools import cycle


def round_robin_striping(peer_uids, blocks):
    """ Assign blocks to be stored across many peers.  This divvies up blocks
    by assigning them to peers one by one until there are no blocks left to
    assign, i.e. in the same manner that we would deal cards in a card game."""
    allocations = defaultdict(list)
    # round robin allocation
    for h in cycle(peer_uids):
        if not blocks:
            break
        allocations[h].append(blocks.pop())
    return allocations
