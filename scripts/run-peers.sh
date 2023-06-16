#!/usr/bin/env bash

# NOTE: this expects to be run from the repo root folder
# e.g. as ./scripts/init-peers.sh
# and the paths here are relative to that root

# Number of peers to spin up
N=$1

if [ "$N" -gt 0 ]; then
  # Spin up the peers
  for i in $(seq 1 $N); do
    # note the & here at the end;
    # it's so that the loop will continue
    # and the peers will be spun up
    # in parallel
    ./scripts/run-peer.sh $i &
  done
else
  echo "Error: The number of peers must be a positive integer."
fi
