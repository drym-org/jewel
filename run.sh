#!/usr/bin/env bash

# TODO: support an "all" argument or leaving out
# the argument to spin up all peers (would require
# the script to discover the peer folders present in
# `live` -- not too hard since they are just numbers)

if [[ $# -eq 0 ]]; then
    echo "Usage: ./run.sh [number of peers]"
    echo "The number should not exceed the number you used with the init script."
    exit 1
fi

if [ "$1" -le 0 ]; then
  echo "Error: The number of peers must be a positive integer."
  exit 1
fi

echo "Starting nameserver and file server..."
echo ""

# Based on: https://stackoverflow.com/a/52033580
(trap 'kill 0' SIGINT;
 pyro5-ns &
 cd live/fileserver && ./fileserver.py &
 ./scripts/run-peers.sh $1 &
 wait)
# TODO: separate peer initialization

echo ""
echo "Bye."
