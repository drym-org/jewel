# Installation

This proof-of-concept uses Pyro5 to model a P2P filesharing network, and regular shell scripts to manage the various network components concurrently.

``` shell
$ pip install Pyro5
```

# How to use

## In one terminal window

``` shell
$ ./init.sh
```

This initializes the network (the fileserver and peers) by copying all of the necessary files to the ``live`` folder, overwriting any local changes.

Now spin up your network:

``` shell
$ ./run.sh
```

This starts the nameserver, fileserver and peers.

## In another terminal window

``` shell
$ ./do.py
```

This allows you to do things like have one peer store a file on another.

## Looking at things

All logs go to the first terminal window, the one where you ran ``run.sh``.

You can also ask the nameserver about live nodes on the network:

``` shell
$ pyro5-nsc list
```
