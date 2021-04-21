# Given a .book file or screenplay .txt, produce a cleaned dialog table
import pandas as pd
from hannstats import utils
from argparse import ArgumentParser
import os
import json

_SCRIPT_DIR = os.path.dirname(__file__)
_CHAR_BINS = os.path.join(_SCRIPT_DIR, "..", "character_bins.json")

def main():
    parser = ArgumentParser()

    parser.add_argument("datapath", help="path to a directory of .book or .txt files")
    parser.add_argument("outdir", help="output directory")
    parser.add_argument("--type", help="Is it a .book file or a screenplay? Options: ['book', 'screenplay']", required=True)

    args = parser.parse_args()
    files = os.listdir(args.datapath)

    if args.type == 'book':
        paths = [os.path.join(args.datapath, fname) for fname in files if fname[-5:] == '.book']
        frames = [utils.load_bnlp_dialog(np) for np in paths]
    elif args.type == 'screenplay':
        paths = [os.path.join(args.datapath, fname) for fname in files if fname[-4:] == '.txt']
        texts = []
        for p in paths:
            with open(p) as fp:
                texts.append(fp.read())
        frames = [utils.screenplay_to_dialog_table(t) for t in texts]
        
    else:
        print("That is not a valid type")
        exit(0)

    with open(_CHAR_BINS) as fp:
        char_bins = utils.flip_mapping(json.load(fp))

    for frame in frames:
        frame["speaker"] = frame["speaker"].str.lower()
        frame["speaker"] = frame["speaker"].map(lambda x: char_bins[x] if x in char_bins else x)
        #frame["dialog"] = frame["dialog"].map(lambda x: x.strip('"'))
        #frame["processed_dialog"] = frame["dialog"].str.lower()

    for file, frame in zip(files, frames):
        fname = file.split('.')[0] + '_dialog.tsv'
        outpath = os.path.join(args.outdir, fname)
        frame.to_csv(outpath, index=False, sep='\t')


if __name__ == "__main__":
    main()