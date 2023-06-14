from hashlib import sha1


def compute_checksum(text):
    checksum = sha1()
    checksum.update(text)
    return checksum.hexdigest()
