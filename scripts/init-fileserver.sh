#!/usr/bin/env bash

# NOTE: this expects to be run from the repo root folder
# e.g. as ./scripts/init-peers.sh
# and the paths here are relative to that root

mkdir -p live/fileserver/disk

cp fileserver.py live/fileserver
cp models.py live/fileserver
cp names.py live/fileserver
cp checksum.py live/fileserver
cp networking.py live/fileserver
cp log.py live/fileserver
cp file.py live/fileserver
cp config.py live/fileserver
cp striping.py live/fileserver
cp -R scheme live/$1
