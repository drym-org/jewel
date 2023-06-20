from dataclasses import dataclass


@dataclass
class BlockMetadata:
    checksum: str
    size: int = None


@dataclass
class Block:
    checksum: str
    data: bytes


@dataclass
class File:
    name: str
    data: bytes

# TODO: PeerMetadata
