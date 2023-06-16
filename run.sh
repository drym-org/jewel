#!/usr/bin/env bash

echo "Starting nameserver and file server..."
echo ""

# Based on: https://stackoverflow.com/a/52033580
(trap 'kill 0' SIGINT;
 pyro5-ns &
 cd live/fileserver && ./fileserver.py &
 cd live/peer && ./peer.py &
 cd live/peer2 && ./peer.py &
 wait)
# TODO: separate peer initialization

echo ""
echo "Bye."
