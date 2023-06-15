#!/usr/bin/env bash

echo "Resetting network..."
rm -rf live*
mkdir -p live/client/disk live/fileserver/disk
cp client.py live/client
cp models.py live/client
cp names.py live/client
cp checksum.py live/client
# TODO: different files on clients / different peers
cp disk/a.txt live/client/disk
cp fileserver.py live/fileserver
cp models.py live/fileserver
cp names.py live/fileserver
cp checksum.py live/fileserver
# TODO: separate peer initialization
mkdir -p live/peer/disk
cp peer.py live/peer
cp models.py live/peer
cp names.py live/peer
cp checksum.py live/peer
