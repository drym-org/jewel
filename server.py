#!/usr/bin/env python
import Pyro5.api

@Pyro5.api.expose
class Peer(object):
    def store(self, name):
        return f"Hello! I've saved {name}.\n"


daemon = Pyro5.api.Daemon()             # make a Pyro daemon
uri = daemon.register(Peer)             # register the peer as a Pyro object
ns = Pyro5.api.locate_ns()              # find the name server
ns.register("example.peer", uri)        # register the object with a name in the name server

print("Ready.")
daemon.requestLoop()                    # start the event loop of the server to wait for calls
