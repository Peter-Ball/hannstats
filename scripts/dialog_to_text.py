# Here I take character dialog and bin it into text files to be used for topic modelling

import argparse
import os
import pandas as pd
import json

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("dialog_tables", help="directory of dialog tables (usually all the dtables from a given corpus)")
    parser.add_argument("outpath", help="where to output the resulting df and text files")
    parser.add_argument("-c", "--corpus_name", help="Give a name to this corpus (for better output tables)")
    parser.add_argument("--character_list", help=".json with a list of characters to focus on")

    args = parser.parse_args()

    paths = list(reversed([os.path.join(args.dialog_tables, fname) for fname in os.listdir(args.dialog_tables) if fname[-4:] == '.tsv']))
    frames = [pd.read_csv(np, sep='\t') for np in paths]

    print(paths[0])

    # Limiting to the central characters across the texts (leaving in Starling to examine substitution hypothesis)
    with open(args.character_list) as fp:
        characters = json.load(fp)

    data = {"speaker": [],
            "item_num": [], # What frame was it from?
            "path": []}

    for i in range(len(frames)):
        for char in characters:
            frame = frames[i]
            cf = frame.loc[frame['speaker'] == char]
            # Skip characters who don't speak at all
            if cf.shape[0] > 0:
                fname = f"{i}_{char}.txt"
                text_path = os.path.join(args.outpath, fname)

                # Not bothering to pre-process, my topic modelling code does that
                all_dialog='\n'.join(cf['dialog'])
                with open(text_path, 'w') as fp:
                    fp.write(all_dialog)

                data["speaker"].append(char)
                data["item_num"].append(i)
                data["path"].append(os.path.join(args.outpath, fname))

    if args.corpus_name:
        data['corpus_name'] = [args.corpus_name for s in data["speaker"]]

    df_path = os.path.join(args.outpath, "table.tsv")

    df = pd.DataFrame(data)
    df.to_csv(df_path, index=False, sep='\t')





if __name__ == "__main__":
    main()