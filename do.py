#!/usr/bin/env python
import Pyro5.api
from simple_term_menu import TerminalMenu
from networking import discover_peers
from sys import exit


def store_file():
    peers = discover_peers()
    peers = list(peers.keys())
    menu = TerminalMenu(peers, title="Which peer?")
    peer_index = menu.show()
    filename = input("What file would you like to store? ").strip()
    peer_name = peers[peer_index]
    print(f"OK. Having {peer_name} request to store {filename} ...\n")
    with Pyro5.api.Proxy(f"PYRONAME:{peer_name}") as peer:
        peer.make_request(filename)


def main_menu():
    options = ["[d] dir", "[s] Store a file", "[x] Delete a file", "[q] quit"]
    menu = TerminalMenu(options, title="What would you like to do?")
    selected_index = menu.show()
    if selected_index == 0:
        print("Lots of files!")
    elif selected_index == 1:
        store_file()
    elif selected_index == 2:
        print("Delete!")
    else:
        exit(0)


def main():
    while True:
        main_menu()


if __name__ == '__main__':
    main()
