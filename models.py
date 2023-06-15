from dataclasses import dataclass


@dataclass
class BlockMetadata:
    checksum: str
    name: str = None
    size: int = None


# TODO: PeerMetadata
