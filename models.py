from dataclasses import dataclass


@dataclass
class Metadata:
    filename: str
    checksum: str
