# Calculate and visualize the dialog surprise metric

import argparse
import pandas as pd
from scipy.stats import entropy
from hannstats import visuals
import matplotlib.pyplot as plt

font_sizes = {
    "fig": 20.0,
    "subfig": 14.0
}

def represents_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("topics_file", help="A .tsv with a speaker column, a corpus_name topic, and a column for each topic numbered 0 to n-1")

    args = parser.parse_args()

    df = pd.read_csv(args.topics_file, sep='\t')

    topics = [column for column in df.columns if represents_int(column)]
    characters = df['speaker'].unique()

    # Get a separate frame for each corpus, and the corpus names while we're at it
    frames = []
    corpora = ['novels', 'screenplays', 'fanfic']
    for corpus in corpora:
        frames.append(df.loc[df['corpus_name'] == corpus].copy())

    for char in characters:
        print(f"Top topics for {char}:")
        for i in range(len(frames)):
            corp = corpora[i]
            char_corp = frames[i][frames[i]['speaker'] == char]
            if char_corp.shape[0] > 0:
                top_topic = char_corp["Dominant Topic"].mode().iloc[0]
                print(f"\t{corp}: {top_topic}")

    for char in characters:
        print(f"{char}:")
        for i in range(len(frames)-1):
            a = frames[i].loc[frames[i]['speaker'] == char][topics].copy()
            b = frames[i+1].loc[frames[i+1]['speaker'] == char][topics].copy()
            a_vec = a.sum() / a.shape[0]
            b_vec = b.sum() / b.shape[0]
            ent = entropy(a_vec, b_vec)
            print(f"Entropy between {corpora[i]} and {corpora[i+1]}: {ent}")

    # Ok lets get serious and make a plot
    entropy_data = {"character": [], "novel-screenplay entropy": [], "screenplay-fanfic entropy": [], "novel-fanfic entropy": []}
    for char in characters:
        entropy_data["character"].append(char)
        novels = frames[0].loc[frames[0]['speaker'] == char][topics].copy()
        screenplays = frames[1].loc[frames[1]['speaker'] == char][topics].copy()
        fanfic = frames[2].loc[frames[2]['speaker'] == char][topics].copy()
        n_vec = novels.sum() / novels.shape[0]
        s_vec = screenplays.sum() / screenplays.shape[0]
        f_vec = fanfic.sum() / fanfic.shape[0]

        entropy_data["novel-screenplay entropy"].append(entropy(n_vec, s_vec))
        entropy_data["screenplay-fanfic entropy"].append(entropy(s_vec, f_vec))
        entropy_data["novel-fanfic entropy"].append(entropy(n_vec, f_vec))

    ent_df = pd.DataFrame(entropy_data)
    for ent_measure in ["novel-screenplay entropy", "screenplay-fanfic entropy", "novel-fanfic entropy"]:
        fig = plt.figure(figsize=(10,6))
        measure_df = ent_df[ent_df[ent_measure] > 0].copy()
        ax = visuals.barh(measure_df["character"], measure_df[ent_measure])
        ax.set_ylabel("Character")
        ax.set_xlabel("Entropy")
        ax.set_xlim(0.0, 4)
        fig.suptitle(ent_measure, fontsize=font_sizes['fig'])
        plt.tight_layout()
        plt.show()
        plt.clf()







if __name__ == "__main__":
    main()