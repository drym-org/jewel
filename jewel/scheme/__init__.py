from .hosting import Hosting
from .redundant import NaiveDuplication
from .sharded import VanillaSharding
# from .parity import ShardingWithParity
# from .reedsolomon import ReedSolomon

__all__ = ("Hosting", "NaiveDuplication", "VanillaSharding")
