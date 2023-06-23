# Installation

This proof-of-concept uses python and Pyro5 to model a P2P filesharing network, simple-term-menu to power a command-line menu-driven interface, and regular shell scripts to manage the various network components concurrently.

``` shell
$ make build
```

# How to use

First, ensure that you are at the root path of the cloned ``jewel`` repo.

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
$ jewel
```

This allows you to do things like have one peer store a file on another.

## Looking at things

All logs go to the first terminal window, the one where you ran ``run.sh``.

You can also ask the nameserver about live nodes on the network:

``` shell
$ pyro5-nsc list
```

You can inspect the files stored in each peer by looking in the ``disk`` folder in each peer, e.g. ``live/peer/disk``, or simply use the ``dir`` feature in the Jewel main menu.

## Debugging

In addition to trace logs using using the project's ``log`` utility, adding ad hoc print statements is a reasonable way to debug things, and any such output would show up in the logging/``run`` window. I'm not sure if there is a way to use a debugger like ``pudb`` except via (currently non-existent) unit tests.

You can also run scripts at any path within the repo by running it from the repo root via:

``` shell
$ python -m jewel.path.to.my.module
```

This ensures that the module will be able to use relative imports within the package namespace the same way as any other Jewel module.

# The Code

## The Network

There are two main python modules -- ``peer.py`` and ``fileserver.py``. When deployed using ``init.sh``, these modules are placed in dedicated folders to model distinct nodes or machines on a network. These folders also each contain a ``disk`` subfolder that represents the node's hard drive.

Both of these modules use Pyro5 to interact over the network. This library allows us to do simple method invocations on remote objects -- a really seamless RPC framework, basically.

Besides these two modules, everything else is just supporting modules.

## The Interface

The ``do.py`` module is the user interface to this whole thing. It uses a nifty library called ``simple-term-menu``, and the selected options appear in the code as indexes that we can use to take appropriate action. Remember to ``run.sh`` first so that the network is up.

## Automation

Spinning up a network in various configurations would be time-consuming and error prone, so we use bash scripts to do it. Specifically, ``init.sh`` creates the network in the ``live`` directory by simply copying over files into distinct folders representing nodes or machines, and ``run.sh`` spins everything up once deployed.

# Supporting this Project

Please make any financial contributions in one of the following ways:

- by Venmo to ``@Sid-K``
- by Paypal to skasivaj at gmail dot com

Please mention "Jewel" in your message.

This project follows Attribution-Based Economics as described in [drym-org/foundation](https://github.com/drym-org/foundation). Any financial contributions will be distributed to contributors and antecedents as agreed-upon in a collective process that anyone may participate in. To see the current distributions, take a look at [abe/attributions.txt](https://github.com/countvajhula/jewel/blob/main/abe/attributions.txt). To see payments made into and out of the project, see the [abe](https://github.com/countvajhula/jewel/blob/main/abe/) folder. If your payment is not reflected there within 3 days, or if you would prefer to, you are welcome to submit an issue or pull request to report the payment yourself -- all payments into and out of the repository are to be publicly reported (but may be anonymized if desired).

Additionally, if your voluntary payments exceed the agreed-upon "market price" of the project (see [price.txt](https://github.com/countvajhula/jewel/blob/main/abe/price.txt)), that additional amount will be treated as an investment, entitling you to a share in future revenues, including payments made to the project in the future or attributive revenue from other projects.

This project will distribute payments according to the ABE guidelines specified in the constitution. In particular, it may take up to 90 days to distribute the initial payments if DIA has not already been conducted for this project. After that, payments will be distributed to contributors (including investors) at each meeting of the [DIA congress](https://github.com/drym-org/dia-old-abe) (e.g. approximately quarterly).

# Non-Ownership

This work is not owned by anyone. Please see the [Declaration of Non-Ownership](https://github.com/drym-org/foundation/blob/main/Declaration_of_Non_Ownership.md).
