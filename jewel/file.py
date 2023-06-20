import os


def write_file(base_path, filename, contents):
    with open(os.path.join(base_path, filename), 'wb') as f:
        f.write(contents)


def file_contents(base_path, filename):
    with open(os.path.join(base_path, filename), 'rb') as f:
        return f.read()
