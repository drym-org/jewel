from dataclasses import dataclass


@dataclass
class BlockMetadata:
    checksum: str
    name: str = None
    size: int = None
    is_recovery: bool = False


@dataclass
class Block:
    checksum: str
    data: bytes


@dataclass
class File:
    name: str
    data: bytes


@dataclass
class PeerMetadata:
    scheme: str
    n: int
    k: int
    m: int
    j: int
