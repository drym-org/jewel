# Installation

This proof-of-concept uses python and Pyro5 to model a P2P filesharing network, simple-term-menu to power a command-line menu-driven interface, and regular shell scripts to manage the various network components concurrently.

``` shell
$ pip install Pyro5
$ pip install simple-term-menu
```

# How to use

## In one terminal window

``` shell
$ ./init.sh [N]
```

This initializes the network (the fileserver and peers) by copying all of the necessary files to the ``live`` folder, overwriting any local changes. The argument ``N`` indicates how many peers you want.

Now spin up your network:

``` shell
$ ./run.sh [N]
```

This starts the nameserver, fileserver and peers. The ``N`` argument indicates how many of the peers you'd like to spin up.

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

You can inspect the files stored in each peer by looking in the ``disk`` folder in each peer, e.g. ``live/peer/disk``.

# The Code

## The Network

There are two main python modules -- ``peer.py`` and ``fileserver.py``. When deployed using ``init.sh``, these modules are placed in dedicated folders to model distinct nodes or machines on a network. These folders also each contain a ``disk`` subfolder that represents the node's hard drive.

Both of these modules use Pyro5 to interact over the network. This library allows us to do simple method invocations on remote objects -- a really seamless RPC framework, basically.

Besides these two modules, everything else is just supporting modules.

## The Interface

The ``do.py`` module is the user interface to this whole thing. It uses a nifty library called ``simple-term-menu``, and the selected options appear in the code as indexes that we can use to take appropriate action. Remember to ``run.sh`` first so that the network is up.

## Automation

Spinning up a network in various configurations would be time-consuming and error prone, so we use bash scripts to do it. Specifically, ``init.sh`` creates the network in the ``live`` directory by simply copying over files into distinct folders representing nodes or machines, and ``run.sh`` spins everything up once deployed.
