#!/usr/bin/env bash

echo "Starting nameserver and file server..."
echo ""

(trap 'kill 0' SIGINT; pyro5-ns & cd live/fileserver && ./fileserver.py & cd live/peer && ./peer.py & wait)
# TODO: separate peer initialization

echo ""
echo "Bye."
