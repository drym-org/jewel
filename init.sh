#!/usr/bin/env bash

if [[ $# -eq 0 ]]; then
    echo "Usage: ./init.sh [number of peers]"
    exit 1
fi

# at least two because we make that assumption in copying
# initial files over while initializing the peers -- we
# assume that a peer 1 and a peer 2 exist that we can
# place files in. That part could be made less hardcoded.
if [ "$1" -lt 2 ]; then
  echo "Error: The number of peers must be at least 2."
  exit 1
fi

echo "Initializing network..."

# the number of peers to set up
N=$1

rm -rf live*
./scripts/init-fileserver.sh
./scripts/init-peers.sh $N
echo "... done."
