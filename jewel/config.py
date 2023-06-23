import configparser
import csv
from .models import PeerMetadata

CONFIG_FILE = 'config.ini'


def load_peer_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    preferences = dict(config['general'])
    scheme = next(csv.reader([preferences['scheme']]))[0]
    n = int(next(csv.reader([preferences['n']]))[0])
    k = int(next(csv.reader([preferences['k']]))[0])
    m = int(next(csv.reader([preferences['m']]))[0])
    return PeerMetadata(scheme, n, k, m)


def main():
    print(load_peer_config())


if __name__ == '__main__':
    main()
