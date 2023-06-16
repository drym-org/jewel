#!/usr/bin/env python
import Pyro5.api
from simple_term_menu import TerminalMenu
from networking import discover_peers
from sys import exit


def dir():
    """ List files on a selected peer. """
    peers = discover_peers()
    peers = list(peers.keys())
    menu = TerminalMenu(peers, title="Which peer?")
    peer_index = menu.show()
    peer_name = peers[peer_index]
    with Pyro5.api.Proxy(f"PYRONAME:{peer_name}") as peer:
        print(peer.dir())


def store_file():
    """ Have a peer request to store a file. """
    peers = discover_peers()
    peers = list(peers.keys())
    menu = TerminalMenu(peers, title="Which peer?")
    peer_index = menu.show()
    filename = input("What file would you like to store? ").strip()
    peer_name = peers[peer_index]
    print(f"OK. {peer_name} is requesting to store {filename} ...\n")
    with Pyro5.api.Proxy(f"PYRONAME:{peer_name}") as peer:
        peer.make_request(filename)


def delete_file():
    """ Ask a peer to delete a file. """
    peers = discover_peers()
    peers = list(peers.keys())
    menu = TerminalMenu(peers, title="Which peer?")
    peer_index = menu.show()
    peer_name = peers[peer_index]
    with Pyro5.api.Proxy(f"PYRONAME:{peer_name}") as peer:
        files = peer.dir()
        menu = TerminalMenu(files, title="Which file?")
        file_index = menu.show()
        filename = files[file_index]
        peer.delete(filename)


def main_menu():
    options = ["[d] dir", "[s] Store a file", "[x] Delete a file", "[q] quit"]
    menu = TerminalMenu(options, title="What would you like to do?")
    selected_index = menu.show()
    if selected_index == 0:
        dir()
    elif selected_index == 1:
        store_file()
    elif selected_index == 2:
        delete_file()
    else:
        exit(0)


def main():
    while True:
        main_menu()


if __name__ == '__main__':
    main()
