#!/usr/bin/env python
import Pyro5.api
import os
import base64
from functools import partial
from .models import BlockMetadata, File
from .checksum import compute_checksum
from .names import unique_name
from .log import log
from .scheme import Hosting, NaiveDuplication
from .file import file_contents, write_file, dir, delete_file

# every node on the network needs to have a distinct name
# so we define namespaces and derive the final name by
# appending the name of the current directory
NAMESPACE = 'jewel.peer'
PWD = os.path.basename(os.getcwd())
NAME = unique_name(NAMESPACE, PWD)
# so that all logs by this process show
# where they're coming from
os.environ["JEWEL_NODE_NAME"] = NAME

CONFIG_FILE = 'config.ini'
SCHEME = NaiveDuplication(2)  # load_peer_config(CONFIG_FILE)
# SCHEME = Hosting()  # load_peer_config(CONFIG_FILE)

log = partial(log, NAME)


@Pyro5.api.expose
class Peer:
    def ping(self):
        return True

    def dir(self):
        return dir()

    def has_file(self, filename):
        """ This should be used exclusively by the fileserver, and exclusively
        to check for the presence of blocks via block ids - not naive
        filenames. """
        # TODO: rename to has_block
        files = self.dir()
        return (filename in files)

    def store(self, metadata, contents):
        """ Store a file on this peer (note that this method is called by
        _another_ peer when that peer wants to store the file here)."""
        m = BlockMetadata(**metadata)
        decoded = base64.decodebytes(bytes(contents['data'], 'utf-8'))
        checksum = compute_checksum(decoded)
        assert checksum == m.checksum
        write_file(m.checksum, decoded)
        log(f"Hello! I've saved {m.checksum}.\n")

    def retrieve(self, filename):
        try:
            contents = file_contents(filename)
        except FileNotFoundError:
            log(f"{filename} not found!")
        else:
            log(f"I'm sending {filename}.\n")
            return contents

    def delete(self, filename):
        try:
            delete_file(filename)
        except FileNotFoundError:
            log(f"{filename} not found!")
        else:
            log(f"{filename} deleted!")

    def request_to_get(self, filename):
        """ Make a request to retrieve a file from the network.

        This is a control method, allowing us to remotely
        instruct this peer to perform actions, in this case,
        to request to get a file stored on the network.
        """
        if self.has_file(filename):
            log(f"Already have {filename}!\n")
        else:
            SCHEME.get(filename)
            log(f"{filename} received.\n")

    def request_to_store(self, filename):
        """ Make a request to store a file on the network.

        This is a control method, allowing us to remotely
        instruct this peer to perform actions, in this case,
        to request to store a file on the network.
        """
        try:
            contents = file_contents(filename)
        except FileNotFoundError:
            log(f"{filename} not found!")
        else:
            file = File(filename, contents)
            SCHEME.store(file)


def main():
    daemon = Pyro5.api.Daemon()
    # register Peer as a Pyro object
    uri = daemon.register(Peer)
    # register the object with a name in the name server
    ns = Pyro5.api.locate_ns()
    ns.register(NAME, uri, metadata={"peer"})
    log("Ready.")
    # start the event loop of the server to wait for calls
    daemon.requestLoop()


if __name__ == '__main__':
    main()
