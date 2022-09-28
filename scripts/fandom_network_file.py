# Make a network file for each screenplay

from hannstats import utils
from argparse import ArgumentParser
import pandas as pd
import os
import json

_SCRIPT_DIR = os.path.dirname(__file__)
_CHAR_BINS = os.path.join(_SCRIPT_DIR, "..", "character_bins.json")


def main():
    parser = ArgumentParser()

    parser.add_argument("fandom_file", help=".json file from a fandom")
    parser.add_argument("outpath", help="Where to output")

    args = parser.parse_args()


    with open(args.fandom_file) as fp:
        data = json.load(fp)

    fandom_net = utils.fandom_network(data, _CHAR_BINS)

    fandom_net.to_csv(args.outpath, sep='\t', index=False)

if __name__ == "__main__":
    main()