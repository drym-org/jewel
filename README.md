# Installation

This proof-of-concept uses Pyro5 to model a P2P filesharing network, and regular shell scripts to manage the various network components concurrently.

``` shell
$ pip install Pyro5
```

# How to use

``` shell
$ ./run.sh          # start nameserver, fileserver and peers
$ ./run-client.sh   # start client
```

## Looking at things

``` shell
$ pyro5-nsc list      # list the live nodes the nameserver knows about
```
