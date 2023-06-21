from collections import defaultdict
from itertools import cycle
from .networking import upload


def round_robin_striping(peer_uids, blocks):
    """ Store blocks on a specific peer. """
    allocations = defaultdict(list)
    # round robin allocation
    for h in cycle(peer_uids):
        if not blocks:
            break
        allocations[h].append(blocks.pop())
    return allocations
