#!/usr/bin/env python
import click
import subprocess
from .do import do


@click.command(
    help=(
        "Initialize P2P network at the path `live/`.\n\n"
        "This must be run while in the repo root folder."
    )
)
@click.argument("n", required=True)
def init(n):
    subprocess.call(f"./init.sh {n}", shell=True)


@click.command(
    help=(
        "Spin up the P2P network at the path `live/`.\n\n"
        "N is the number of peers to spin up.\n\n"
        "This must be run while in the repo root folder."
    )
)
@click.argument("n", required=True)
def run(n):
    subprocess.call(f"./run.sh {n}", shell=True)


@click.group(help="Jewel - prototype P2P storage schemes.")
def main():
    pass


main.add_command(init)
main.add_command(run)
main.add_command(do)


if __name__ == '__main__':
    main()
