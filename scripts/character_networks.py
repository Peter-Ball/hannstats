# This is where I build the character networks!
from argparse import ArgumentParser
import networkx as nx
import pandas as pd
from pyvis.network import Network
import os, json
from hannstats import utils

_SCRIPT_DIR = os.path.dirname(__file__)
_CHAR_BINS = os.path.join(_SCRIPT_DIR, "..", "character_bins.json")

def main():
    parser = ArgumentParser()

    parser.add_argument("-n", "--novels", help="Folder with network files for novels", required=True)
    parser.add_argument("-s", "--screenplays", help="Folder with network files for screenplays", required=True)
    parser.add_argument("-f", "--fanfic", help="Folder with network files for fanfic", required=True)

    args = parser.parse_args()

    n_paths = [os.path.join(args.novels, file) for file in os.listdir(args.novels)]
    s_paths = [os.path.join(args.screenplays, file) for file in os.listdir(args.screenplays)]
    f_paths = [os.path.join(args.fanfic, file) for file in os.listdir(args.fanfic)]

    n_frames = [pd.read_csv(np, sep='\t') for np in n_paths]
    f_frames = [pd.read_csv(fp, sep='\t') for fp in f_paths]
    s_frames = [pd.read_csv(sp, sep='\t') for sp in s_paths]

    n_corp = pd.concat(n_frames)
    f_corp = pd.concat(f_frames)
    s_corp = pd.concat(s_frames)
    print(s_corp)

    df = f_corp
    with open(_CHAR_BINS) as fp:
        cbins = json.load(fp)
    #df = df[(df['source'].isin(cbins)) & (df['target'].isin(cbins))]

    df = df[df['weight']>=10]
    G = nx.from_pandas_edgelist(df,
                                source="source",
                                target="target",
                                edge_attr="weight")

    net = Network(height='100%', width='100%', bgcolor='#222222', font_color='white')
    net.from_nx(G)
    net.barnes_hut()

    net.show("example.html")


if __name__ == "__main__":
    main()