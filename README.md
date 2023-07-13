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

This initializes the network (the fileserver and peers) by copying all of the necessary files to the ``live`` folder, overwriting any local changes. The argument ``N`` indicates how many peers you want. ``5`` is a good number for testing nontrivial functionality without it being too hard to keep track of.

Now spin up your network:

``` shell
$ ./run.sh [N]
```

This starts the nameserver, fileserver and peers. The ``N`` argument indicates how many of the peers you'd like to spin up. Typically, you'd spin up all of the peers you created, e.g. ``5``.

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

``` shell
jewel
│
├── block.py
├── bytes.py
├── checksum.py
├── config.py
├── file.py
├── fileserver.py
├── jewel.py
├── list.py
├── log.py
├── metadata.py
├── models.py
├── names.py
├── networking.py
├── peer.py
├── scheme
│   ├── __init__.py
│   ├── base.py
│   ├── hosting.py
│   ├── redundant
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── naive.py
│   ├── sharded
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── redundant
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── parity.py
│   │   │   ├── reedsolomon.py
│   │   │   └── shardshard.py
│   │   └── vanilla.py
│   └── striped
│       ├── __init__.py
│       └── base.py
├── sharding.py
├── striping.py
```

## The Network

There are two main python modules -- ``peer.py`` and ``fileserver.py``. The former implements a peer on the network that may upload or download files, while the latter keeps track of files on the network. When deployed using ``init.sh``, these modules are placed in dedicated folders to model distinct nodes or machines on a network. These folders also each contain a ``disk`` subfolder that represents the node's hard drive.

Both of these modules use Pyro5 to interact over the network. This library allows us to do simple method invocations on remote objects -- a really seamless RPC framework, basically.

Besides these two modules, everything else is just supporting modules.

## The Interface

The ``jewel.py`` module is the user interface to this whole thing. It uses a nifty library called ``simple-term-menu``, and the selected options appear in the code as indexes that we can use to take appropriate action. Remember to ``run.sh`` first so that the network is up.

## Storage schemes

Storage schemes are defined in terms of a class hierarchy in the `schemes` folder and their usage contract is simply to provide ``store`` and ``get`` method implementations. The former method uploads the file to the network, and the latter downloads it -- *how* this is done is defined by the particular storage scheme used and is abstracted from the caller. Most concerns in a storage scheme, like striping, sharding, and error recovery, are reasonably well bounded and orthogonal to one another, so they are implemented as mixins in the class hierarchy.

To implement a new scheme, simply subclass the mixins you need and implement their abstract methods to gain the relevant functionality, or add a new base class (e.g. subclassing python's abstract base class ``abc.ABC``) to add novel functionality.

## The filesystem

The filesystem's operations are in terms of *blocks* rather than files. The only time that filenames are employed is in interactions with peers who may only know the filename rather than the block name (and we assume for simplicity that filenames are unique on the network). A block may correspond to a file or even a shard of a file, or, in principle, even a stray fragment that is simply a contiguous byte range within a file. All of these are blocks.

Blocks are identified by their contents, so that two files with different names but the same contents would correspond to the same block (this is similar to the concept of "blobs" in Git). The reason to use blocks is that the core operations of the filesystem may be uniformly and parsimoniously described in terms of blocks, so that "files" and "shards" are higher level concepts that are not relevant to these core operations of storage and recovery.

The filesystem maintains four data structures (currently all residing on the fileserver):

1. The *index*, which maps a filename to the corresponding whole block.
2. The *blocktree*, which maps a block to other blocks that are its "shards." Root blocks in the block tree correspond to complete files, and shards may have shards themselves.
3. The *block catalog*, which is the opposite of the block tree, mapping blocks to other blocks that they are a part of.
4. The *block book*, which is a mapping of blocks to peers hosting them. Currently, this isn't implemented and we just poll all peers each time a block is requested.

## Automation

Spinning up a network in various configurations would be time-consuming and error prone, so we use bash scripts to do it. Specifically, ``init.sh`` creates the network in the ``live`` directory by simply copying over files into distinct folders representing nodes or machines, and ``run.sh`` spins everything up once deployed.

# Concepts

## "Jewels"

This proof-of-concept is primarily intended to demonstrate the concept of "jewels" and how they may be used to gain a simple and tractable customization "knob" on the storage scheme in order to fulfill changing needs of availability and throughput.

A jewel is any piece of data that is functionally equivalent to any other jewel with regard to reconstructing your original data, so that the only thing that matters is _how many_ of them you have, not which ones. To be clear, this doesn't mean that the jewels are indistinguishable from one another (e.g. like electrons) -- just that they are substitutable for one another when collected together. Each jewel reflects the whole and every other jewel, like in Indra's Net (hence the name).

More precisely, any subset of the full set of jewels is equivalent to any other subset of the same size.

## The construction of jewels

Jewels are currently implemented using Reed-Solomon encoding, but it's more the idea that is important, and it's possible that other encoding schemes can achieve the same goals.

Reed-Solomon codes encode data in _blocks_ of a certain size (e.g. 255 bytes -- and note these "blocks" are unrelated to the concept of block as described elsewhere in this project). These blocks are typically much smaller than the data we wish to encode, so for data of arbitrary size, it is typically "chunked" and encoded independently into blocks.

For a large file, we'd like to store it in smaller "shards" across many machines, but if these shards are larger than the RS block size and if even one of them is missing, then entire blocks will be missing and there is no way to recover them even if we have all of the other shards and even if we employ high redundancy in our encoding, since there is no recovery information present at a higher level than individual blocks.

To get around this, we could either invent a higher-level encoding scheme that operates across blocks or across shards, or we could store the blocks in a special way so that entire blocks cannot go missing. This latter approach is what we follow here.

Specifically, once the file is encoded, instead of dividing the entire resulting file into K shards, we divide _each block within that file_ into K shards and then concatenate these shards by position to obtain our final shards, or jewels. That is, jewels are composed of the shards of each block by index, and there are as many jewels as there are shards. If K=3, then there will be three shards of each block, and three corresponding jewels made up of the first shards, the second shards, and the third shards.

# Motivation

**Problem**: How can we store data on a peer-to-peer network so that you can reliably access it from anywhere at any time while minimizing the amount of storage used as well as the time taken to retrieve it?

**Solution A (naive duplication)**: store a copy of the file on N peers. Then, as long as at least 1 peer is available, you can get your file.

The way to make this solution more reliable is to increase N, and we can get arbitrarily close to 100% availability. The cost is high redundancy. If we define a redundancy factor D as the amount of data stored compared to the original size of the data, then for this solution, D = N.

**Solution B (naive sharding)**: divide the file into K shards and store them, as before, across N peers. Individual peers may have more than one shard, but not necessarily the entire file. As a result, with this scheme, we'd need at least M peers to be online in order to get our data.

The main value of this solution is _decoupling_. It decouples N, D, and M, giving us the flexibility to tune these to our liking (even, possibly, learn or dynamically tune the values in response to network health). In particular, this reduces to solution A in a boundary case where we store the full set of shards on each peer.

As an example, say we'd like to store a file across 3 peers, so N=3. In solution A, this means that D=3 as well, i.e. we are storing 3x as much data as the size of the file.

For solution B, if we divide the file into 3 shards and then stripe them across the 3 peers as [1,2,3],[1,2,3],[1,2,3], then this is identical to solution A. But we could also stripe the shards as [1,2],[2,3],[3,1], and in this case, D=2 (since we have two copies of every shard), and we need at least 2 peers to be online to get our file.

The point is, this solution decouples things. It opens up new possibilities, as exemplified by the remaining solutions.

**Solution C (sharding with parity)**: Same as solution B, but in addition to the M shards, we also create an extra "parity" shard which is the XOR of all of the M shards. This is similar to one of the options used by RAID arrays, where one of the many identically-sized disks in the array is designated as the parity disk. The purpose of this parity shard is to be able to reconstruct any of the other shards if one happens to be unavailable. This is done by simply XOR'ing all of the available M-1 shards together with the parity shard -- the result is the missing M'th shard.

This solution improves on B since, ordinarily, if we wanted extra redundancy, we'd need to duplicate all shards at least one extra time, otherwise any shards that have fewer copies than other shards would be "weak links" in the system. The parity approach allows us to create a single extra shard that gives us extra redundancy in _any_ shard.

The problem is, we can only afford to lose one shard -- either one of the original M shards, or the parity shard. If more than one distinct shard is unavailable, then this solution cannot recover.

**Solution D ("Jewels," or sharding with Reed-Solomon encoding)**: Once again, similar to Solution B, but here, we first encode the data using Reed-Solomon encoding and then store the resulting encoded data (rather than the original data) in specially constructed shards called "jewels." First, a bit about Reed-Solomon codes.

Reed-Solomon is the encoding used in storing data on CDs (among other things), which is why they can still work even after being badly scratched -- it's not that the scratches don't always destroy data, but that the encoding is able to recover the original data even though some of it is lost. The general idea of Reed-Solomon is that for any N numbers, there is a unique polynomial of order N-1 that takes on those values at positions 1,2,3, ..., N. Once we determine this polynomial, we can compute any number of extra values on this curve and store those as "recovery" numbers. If any of the original numbers are lost, as long as you still have at least N numbers, you can compute the polynomial and then get the original values at positions 1 through N back. There are some practical nuances to the implementation, for instance the use of a Galois Field instead of the usual set of integers, but this is the general idea. In this way, Reed Solomon decoding recovers _the larger pattern_ (the polynomial), of which your original data is a part. [This video](https://www.youtube.com/watch?v=1pQJkt7-R4Q "What are Reed-Solomon codes?") is a good overview of the ideas involved.

Now, due to certain practical matters (see the discussion of "jewels" under "Concepts"), we can't naively shard the encoded data the way we do for the unencoded data. By constructing the "jewels" so that they are made up of pieces of encoded data in just the right way, we ensure that every jewel equally reflects the overall pattern and can be used to reconstruct it.

The nice thing about this solution is that the jewels are all equivalent to one another for the purposes of recovering our data, giving us maximum flexibility in tuning and balancing redundancy with availability. For instance, if we would naively have had 5 shards without encoding, then if we create 10 jewels, we can lose any 5 of them and still recover the original data. We could gain differentially higher availability for a minimum cost in redundancy by simply increasing the number of jewels by one, instead of in batches at a high cost in redundancy as we would need to with naive shards. As these jewels are simply blocks from the perspective of the filesystem, just like shards, they can be distributed across the peers using any appropriate scheme for distributing shards, such as one that we might use in solution B.

Finally, any of the solutions can benefit from the introduction of the concept of a ["fragment"](https://github.com/drym-org/jewel/issues/1) at the filesystem level, which would allow for partial and parallel downloads.

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
