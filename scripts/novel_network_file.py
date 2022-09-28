# Mkae a network file for each novel

from hannstats import utils
from argparse import ArgumentParser
import pandas as pd
import os
import json

_SCRIPT_DIR = os.path.dirname(__file__)
_CHAR_BINS = os.path.join(_SCRIPT_DIR, "..", "character_bins.json")


def main():
    parser = ArgumentParser()

    parser.add_argument("tokensdir", help="Directory where the .tokens files are stored")
    parser.add_argument("bookdir", help="Directory where the .book files are stored")
    parser.add_argument("outdir", help="Where to output")
    parser.add_argument("--dist", required=False, nargs='?', default=15, const=15, type=int,
                        help="How big should the sliding window be for determining connection")

    args = parser.parse_args()

    token_files = [os.path.join(args.tokensdir, file) for file in os.listdir(args.tokensdir)]
    book_files = [os.path.join(args.bookdir, file) for file in os.listdir(args.bookdir)]
    novel_names = [fname.split('.')[0] for fname in os.listdir(args.tokensdir)]
    novel_nets = [utils.tokens_to_network(t,b,_CHAR_BINS,args.dist) for t,b, in zip(token_files, book_files)]

    # Output the files:
    for net, name in zip(novel_nets, novel_names):
        net.to_csv(os.path.join(args.outdir, name + '_network.tsv'), sep='\t', index=False)




if __name__ == "__main__":
    main()