#!/usr/bin/env bash

# NOTE: this expects to be run from the repo root folder
# e.g. as ./scripts/init-peers.sh
# and the paths here are relative to that root

mkdir -p live/client/disk

cp client.py live/client
cp models.py live/client
cp names.py live/client
cp checksum.py live/client

cp disk/a.txt live/client/disk
