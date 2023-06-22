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
    return PeerMetadata(scheme, n, k)


def main():
    # for this to work when run as a script (e.g. for testing), uncomment the
    # use of the relative import, and just return the values
    print(load_peer_config())


if __name__ == '__main__':
    main()
