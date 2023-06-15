# Installation

This proof-of-concept uses Pyro5 to model a P2P filesharing network, and GNU Parallel to simplify running the various network components concurrently.

``` shell
$ pip install Pyro5
$ brew install parallel
```

# How to use

``` shell
$ ./run.sh      # start nameserver and fileserver
$ ./client.py   # start client
```

## Looking at things

``` shell
$ pyro5-nsc list      # list the live nodes the nameserver knows about
```
