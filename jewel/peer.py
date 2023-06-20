#!/usr/bin/env python
import Pyro5.api
import os
import base64
from functools import partial
from .models import Block, BlockMetadata, File
from .checksum import compute_checksum
from .names import unique_name
from .log import log
from .scheme.naive import NaiveDuplication
from .networking import peers_available_to_host, hosting_peers
from .file import file_contents, write_file

DISK = 'disk'
# every node on the network needs to have a distinct name
# so we define namespaces and derive the final name by
# appending the name of the current directory
NAMESPACE = 'jewel.peer'
PWD = os.path.basename(os.getcwd())
NAME = unique_name(NAMESPACE, PWD)

CONFIG_FILE = 'config.ini'
SCHEME = NaiveDuplication(1)  # load_peer_config(CONFIG_FILE)

log = partial(log, NAME)


@Pyro5.api.expose
class Peer:
    def ping(self):
        return True

    def dir(self):
        return os.listdir(DISK)

    def has_file(self, filename):
        files = self.dir()
        return (filename in files)

    def store(self, metadata, contents):
        """ Store a file on this peer (note that this method is called by
        _another_ peer when that peer wants to store the file here)."""
        m = BlockMetadata(**metadata)
        decoded = base64.decodebytes(bytes(contents['data'], 'utf-8'))
        checksum = compute_checksum(decoded)
        assert checksum == m.checksum
        write_file(DISK, m.checksum, decoded)
        log(f"Hello! I've saved {m.checksum}.\n")

    def retrieve(self, filename):
        try:
            contents = file_contents(DISK, filename)
        except FileNotFoundError:
            log(f"{filename} not found!")
        else:
            return contents

    def delete(self, filename):
        try:
            os.remove(os.path.join(DISK, filename))
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
            return
        peers = hosting_peers(filename)
        chosen_peer = peers[0]
        with Pyro5.api.Proxy(chosen_peer) as peer:
            # TODO: need to also retrieve the metadata
            # to compare the checksum
            file_contents = peer.retrieve(filename)
            decoded = base64.decodebytes(bytes(file_contents['data'], 'utf-8'))
            write_file(DISK, filename, decoded)
            log(f"{filename} received.\n")

    def request_to_store(self, filename):
        """ Make a request to store a file on the network.

        This is a control method, allowing us to remotely
        instruct this peer to perform actions, in this case,
        to request to store a file on the network.
        """
        try:
            contents = file_contents(DISK, filename)
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