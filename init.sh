#!/usr/bin/env bash

echo "Initializing network..."
rm -rf live*
./scripts/init-fileserver.sh
./scripts/init-peers.sh
echo "... done."
