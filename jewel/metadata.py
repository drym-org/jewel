from .models import BlockMetadata


def make_metadata(block, is_recovery=False, name=None):
    checksum = block.checksum
    if not name:
        name = checksum
    size = len(block.data)
    return BlockMetadata(checksum,
                         is_recovery=is_recovery,
                         name=name,
                         size=size)
