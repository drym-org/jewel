#!/usr/bin/env python
import Pyro5.api
from simple_term_menu import TerminalMenu
from networking import discover_peers
from sys import exit
import re


def _extract_number(str):
    return re.findall(r'\d+', str)[0]


def _show_peer_menu():
    peers = discover_peers()
    peers = list(peers.keys())
    peer_options = [f"[{_extract_number(p)}] {p}" for p in peers]
    menu = TerminalMenu(peer_options, title="Which peer?")
    peer_index = menu.show()
    peer_name = peers[peer_index]
    return peer_name


def _show_file_menu(peer):
    files = peer.dir()
    menu = TerminalMenu(files, title="Which file?")
    file_index = menu.show()
    filename = files[file_index]
    return filename


def dir():
    """ List files on a selected peer. """
    peer_name = _show_peer_menu()
    with Pyro5.api.Proxy(f"PYRONAME:{peer_name}") as peer:
        print(peer.dir())


def store_file():
    """ Have a peer request to store a file. """
    peer_name = _show_peer_menu()
    with Pyro5.api.Proxy(f"PYRONAME:{peer_name}") as peer:
        filename = _show_file_menu(peer)
        print(f"OK. {peer_name} is requesting to store {filename} ...\n")
        peer.request_to_store(filename)


def delete_file():
    """ Ask a peer to delete a file. """
    peer_name = _show_peer_menu()
    with Pyro5.api.Proxy(f"PYRONAME:{peer_name}") as peer:
        filename = _show_file_menu(peer)
        peer.delete(filename)


def get_file():
    """ Have a peer request to get a file. """
    peer_name = _show_peer_menu()
    with Pyro5.api.Proxy(f"PYRONAME:{peer_name}") as peer:
        filename = input("What file would you like to get? ").strip()
        print(f"OK. {peer_name} is requesting to get {filename} ...\n")
        peer.request_to_get(filename)


def main_menu():
    options = ["[d] dir", "[s] Store a file", "[x] Delete a file", "[g] get a file", "[q] quit"]
    menu = TerminalMenu(options, title="What would you like to do?")
    selected_index = menu.show()
    if selected_index == 0:
        dir()
    elif selected_index == 1:
        store_file()
    elif selected_index == 2:
        delete_file()
    elif selected_index == 3:
        get_file()
    else:
        exit(0)


def main():
    while True:
        main_menu()


if __name__ == '__main__':
    main()
