#!/usr/bin/env bash

# NOTE: this expects to be run from the repo root folder
# e.g. as ./scripts/init-peers.sh
# and the paths here are relative to that root

# TODO: different files on different peers
# TODO: copy all py files to a src folder so they can be copied over
# wholesale

mkdir -p live/$1/disk
cp peer.py live/$1
cp models.py live/$1
cp names.py live/$1
cp checksum.py live/$1
cp networking.py live/$1
cp log.py live/$1
cp file.py live/$1
cp config.py live/$1
cp striping.py live/$1
cp -R scheme live/$1
