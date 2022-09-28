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

    parser.add_argument("scriptsdir", help="Directory where the screenply .txt files are stored")
    parser.add_argument("outdir", help="Where to output")

    args = parser.parse_args()

    sp_files = [os.path.join(args.scriptsdir, file) for file in os.listdir(args.scriptsdir)]
    sp_texts = utils.load_texts(sp_files)
    episode_names = [fname.split('.')[0] for fname in os.listdir(args.scriptsdir)]
    sp_nets = [utils.script_to_network(s, _CHAR_BINS) for s in sp_texts]


    # Output the files:
    for net, name in zip(sp_nets, episode_names):
        net.to_csv(os.path.join(args.outdir, name + '_network.tsv'), sep='\t', index=False)

if __name__ == "__main__":
    main()