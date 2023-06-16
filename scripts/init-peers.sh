#!/usr/bin/env bash

# NOTE: this expects to be run from the repo root folder
# e.g. as ./scripts/init-peers.sh
# and the paths here are relative to that root

# TODO: different files on different peers

# Number of peers to spin up
N=$1

if [ "$N" -gt 0 ]; then
  # Spin up the peers
  for i in $(seq 1 $N); do
    ./scripts/init-peer.sh $i
  done
else
  echo "Error: The number of peers must be a positive integer."
fi

# Set up some initial files on the peers
# Note that we assume here that at least some peers exist.
# For now, it's safe to assume that at least two peers exist.
# It would be useful to have a separate script to distribute
# files across the peers, based on the actual peer configuration.
cp disk/a.txt live/1/disk
