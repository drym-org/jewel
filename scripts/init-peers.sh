#!/usr/bin/env bash

# NOTE: this expects to be run from the repo root folder
# e.g. as ./scripts/init-peers.sh
# and the paths here are relative to that root

# TODO: different files on different peers

mkdir -p live/peer/disk
cp peer.py live/peer
cp models.py live/peer
cp names.py live/peer
cp checksum.py live/peer
cp networking.py live/peer
cp log.py live/peer

cp disk/a.txt live/peer/disk

mkdir -p live/peer2/disk
cp peer.py live/peer2
cp models.py live/peer2
cp names.py live/peer2
cp checksum.py live/peer2
cp networking.py live/peer2
cp log.py live/peer2
