import os

DISK = 'disk'


def delete_file(filename):
    try:
        os.remove(os.path.join(DISK, filename))
    except FileNotFoundError:
        raise


def write_file(filename, contents):
    with open(os.path.join(DISK, filename), 'wb') as f:
        f.write(contents)


def file_contents(filename):
    with open(os.path.join(DISK, filename), 'rb') as f:
        return f.read()


def dir():
    return os.listdir(DISK)
