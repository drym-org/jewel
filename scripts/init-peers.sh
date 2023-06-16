#!/usr/bin/env bash

# NOTE: this expects to be run from the repo root folder
# e.g. as ./scripts/init-peers.sh
# and the paths here are relative to that root

mkdir -p live/peer/disk
cp peer.py live/peer
cp models.py live/peer
cp names.py live/peer
cp checksum.py live/peer
