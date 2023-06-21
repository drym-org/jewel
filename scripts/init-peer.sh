#!/usr/bin/env bash

# NOTE: this expects to be run from the repo root folder
# e.g. as ./scripts/init-peers.sh
# and the paths here are relative to that root

# TODO: different files on different peers

mkdir -p live/$1/disk
cp config.ini live/$1
