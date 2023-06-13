#!/usr/bin/env python
import Pyro5.api

data = input("What data would you like to store? ").strip()

with Pyro5.api.Proxy("PYRONAME:example.peer") as peer:
    print(peer.store(data))
