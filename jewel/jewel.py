#!/usr/bin/env python
import Pyro5.api
from simple_term_menu import TerminalMenu
from .networking import discover_peers
from sys import exit
import re
from time import sleep


def error(message):
    print()
    print(message)
    print()
    sleep(0.5)


def _extract_number(str):
    return re.findall(r'\d+', str)[0]


def _show_peer_menu():
    # TODO: do we need to suppress logging here?
    peers = discover_peers()
    peers = list(peers.keys())
    peers.sort()
    peer_options = [f"[{_extract_number(p)}] {p}" for p in peers]
    menu = TerminalMenu(peer_options, title="Which peer?")
    peer_index = menu.show()
    peer_name = peers[peer_index]
    return peer_name


def _show_file_menu(peer):
    files = peer.dir()
    if not files:
        return None
    menu = TerminalMenu(files, title="Which file?")
    index = menu.show()
    filename = files[index]
    return filename


def _show_schemes_menu(peer):
    schemes = peer.list_schemes()
    if not schemes:
        return None
    menu = TerminalMenu(schemes, title="Which scheme?")
    index = menu.show()
    scheme = schemes[index]
    return scheme


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
        if filename:
            print(f"OK. {peer_name} is requesting to store {filename} ...\n")
            peer.request_to_store(filename)
        else:
            error(f"No files present on {peer_name}!")


def delete_file():
    """ Ask a peer to delete a file. """
    peer_name = _show_peer_menu()
    with Pyro5.api.Proxy(f"PYRONAME:{peer_name}") as peer:
        filename = _show_file_menu(peer)
        if filename:
            peer.delete(filename)
        else:
            error(f"No files present on {peer_name}!")


def get_file():
    """ Have a peer request to get a file. """
    peer_name = _show_peer_menu()
    with Pyro5.api.Proxy(f"PYRONAME:{peer_name}") as peer:
        filename = input("What file would you like to get? ").strip()
        print(f"OK. {peer_name} is requesting to get {filename} ...\n")
        peer.request_to_get(filename)


def get_storage_scheme():
    """ Get a peer's current storage scheme. """
    peer_name = _show_peer_menu()

    with Pyro5.api.Proxy(f"PYRONAME:{peer_name}") as peer:
        scheme = peer.current_scheme()
        if scheme:
            print(f"Storage scheme for {peer_name} is {scheme} ...\n")
        else:
            error(f"Unrecognized scheme advertised by {peer_name}!")


def set_storage_scheme():
    """ Set a peer's storage scheme. """
    peer_name = _show_peer_menu()

    with Pyro5.api.Proxy(f"PYRONAME:{peer_name}") as peer:
        scheme = _show_schemes_menu(peer)
        if scheme:
            print(f"OK. Setting storage scheme for {peer_name} to {scheme} ...\n")
            peer.set_storage_scheme(scheme)
        else:
            error(f"No schemes advertised by {peer_name}!")


def show_help():
    info = ["[d] Dir - show files stored on a peer",
            "[s] Store a file - instruct a peer to request to store a file on the network",
            "[x] Delete a file - remove a file from a specific peer",
            "[g] Get a file - instruct a peer to request a file stored on the network",
            "[v] Get storage scheme - see a peer's current storage scheme (e.g. naive duplication, sharding, etc.)",
            "[u] Set storage scheme - set peer's storage scheme",
            "[?] Help - show this menu",
            "[q] Quit - exit to the shell"]
    print("\n".join(info))


def main_menu():
    options = ["[d] Dir",
               "[s] Store a file",
               "[x] Delete a file",
               "[g] Get a file",
               "[v] Get storage scheme",
               "[u] Set storage scheme",
               "[?] Help",
               "[q] Quit"]
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
    elif selected_index == 4:
        get_storage_scheme()
    elif selected_index == 5:
        set_storage_scheme()
    elif selected_index == 6:
        show_help()
    elif selected_index == 7:
        exit(0)
    else:
        exit(0)


def main():
    while True:
        main_menu()


if __name__ == '__main__':
    main()
