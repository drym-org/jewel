from models import BlockMetadata


def make_metadata(block, name=None):
    checksum = block.checksum
    if not name:
        name = checksum
    return BlockMetadata(checksum, name)
