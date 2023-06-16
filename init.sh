#!/usr/bin/env bash

echo "Initializing network..."
rm -rf live*
./scripts/init-client.sh
./scripts/init-fileserver.sh
# TODO: different files on clients / different peers
./scripts/init-peers.sh
echo "... done."
