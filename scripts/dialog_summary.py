# Produce summary plots on character distribution and speaking time

# Plots:
# - Distribution over characters by character appearances
# - Who talks the most proportional to len of all dialog combined
# - Dialog sentiment over time in the corpora
# - Topic modelling of the dialog

import argparse
from hannstats import utils,visuals
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
import pandas as pd
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

font_sizes = {
    "fig": 20.0,
    "subfig": 14.0
}

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-n", "--novels", help="Folder with dialog tables for novels", required=True)
    parser.add_argument("-s", "--screenplays", help="Folder with dialog tables for screenplays", required=True)
    parser.add_argument("-f", "--fanfic", help="Folder with dialog tables for fanfic", required=True)

    args = parser.parse_args()

    # Get filepaths of all input files
    n_paths = [os.path.join(args.novels, fname) for fname in os.listdir(args.novels)]
    s_paths = [os.path.join(args.screenplays, fname) for fname in os.listdir(args.screenplays)]
    f_paths = [os.path.join(args.fanfic, fname) for fname in os.listdir(args.fanfic)]

    # Load all the data into pandas dataframes
    n_frames = [pd.read_csv(np, sep='\t') for np in n_paths]
    f_frames = [pd.read_csv(fp, sep='\t') for fp in f_paths]
    s_frames = [pd.read_csv(sp, sep='\t') for sp in s_paths]
    for i in range(len(n_frames)):
        df = n_frames[i]
        df['frame_number'] = i
    for i in range(len(f_frames)):
        df = f_frames[i]
        df['frame_number'] = i
    for i in range(len(s_frames)):
        df = s_frames[i]
        df['frame_number'] = i

    # Also make corpora-level frames for each
    n_corp = pd.concat(n_frames)
    f_corp = pd.concat(f_frames)
    s_corp = pd.concat(s_frames)

    # PLOT 1: Dialog distribution over characters
    novel_chars = n_corp['speaker'].value_counts(normalize=True).iloc[:10]*100
    screenplay_chars = s_corp['speaker'].value_counts(normalize=True).iloc[:10]*100
    fic_chars = f_corp['speaker'].value_counts(normalize=True).iloc[:10]*100
    fig = plt.figure(figsize=(12, 5))
    gs = GridSpec(nrows=1, ncols=3)
    ax0 = fig.add_subplot(gs[0, 0])
    visuals.bar(novel_chars.index, novel_chars, ax=ax0)
    ax0.set_ylabel("% of Dialog")
    ax1 = fig.add_subplot(gs[0,1])
    visuals.bar(screenplay_chars.index, screenplay_chars, ax=ax1)
    ax2 = fig.add_subplot(gs[0,2])
    visuals.bar(fic_chars.index, fic_chars, ax=ax2)

    for ax, name in zip([ax0, ax1, ax2], ["Novels", "TV Show", "Fan Fiction"]):
        ax.set_ylim(0.0, 40)
        ax.set_title(name, fontsize=font_sizes['subfig'])
    
    fig.suptitle('Dialog Distribution: Who Talks the Most?', fontsize=font_sizes['fig'])
    plt.tight_layout()
    plt.show()
    plt.clf()

    # PLOT 2: Dialog Sentiment
    # We'll just track the three main charactesrs from the show
    characters = ['Hannibal', 'Will Graham', 'Jack Crawford']
    vsent = SentimentIntensityAnalyzer()
    cpal = visuals.get_color_palette()
    for frame in s_frames:
        frame['sentiment'] = frame['dialog'].map(lambda x: vsent.polarity_scores(x)['compound'])

    ## First episodes vs last episodes
    s1e1 = s_frames[0].copy()
    s2e1 = s_frames[13].copy()
    s3e1 = s_frames[26].copy()
    s1e13 = s_frames[12].copy()
    s2e13 = s_frames[25].copy()
    s3e13 = s_frames[-1].copy()

    episode_names = ['S1E1: Aperitif', 'S2E1: Kaiseki', 'S3E1: Antipasto', 'S1E13: Savoureux', 'S2E13: Mizumono', 'S3E13: The Wrath of the Lamb']
    frames = [s1e1, s2e1, s3e1, s1e13, s2e13, s3e13]

    fig = plt.figure(figsize=(16,9))
    gs = GridSpec(nrows=2, ncols=3)
    for i in range(len(frames)):
        ax = fig.add_subplot(gs[i//3, i%3])
        df = frames[i]
        for j in range(len(characters)):
            char = characters[j]
            col = cpal[j]
            char_uts = df.loc[df['speaker'] == char].copy()

            # xvals are the dialog's % of the way through the episode (10 bins)
            char_uts['ep_pct'] = (char_uts.index / df.shape[0]) // 0.1 / 0.1

            # Get average sent per bin
            char_uts = char_uts.groupby('ep_pct').mean()

            visuals.line(char_uts.index, char_uts['sentiment'], ax=ax, color=col, label=char)

        ax.set_title(episode_names[i], fontsize=font_sizes['subfig'])
        ax.set_ylim(-0.6, 0.8)

    handles, labels = ax.get_legend_handles_labels()

    fig.legend(handles, labels, loc='upper left')
    fig.suptitle("Dialog Sentiment: First Episodes vs Last Episodes", fontsize = font_sizes['fig'])
    plt.tight_layout()
    plt.show()
    plt.clf()

    ## Whole show
    fig = plt.figure(figsize=(16,9))
    s_corp_mains = s_corp.loc[s_corp['speaker'].isin(characters)].copy()
    s_corp_mains['sentiment'] = s_corp_mains['dialog'].map(lambda x: vsent.polarity_scores(x)['compound'])

    fig = plt.figure(figsize=(12,5))
    ax = plt.gca()
    for i in range(len(characters)):
        char = characters[i]
        col = cpal[i]
        char_uts = s_corp_mains.loc[s_corp_mains['speaker'] == char].copy()

        # Get average sent per episode
        char_uts = char_uts.groupby('frame_number').mean()

        visuals.line(char_uts.index, char_uts['sentiment'], ax=ax, color=col, label=char)

    fig.legend()
    fig.suptitle("Mean Sentiment Across the Whole Show", fontsize = font_sizes['fig'])
    plt.tight_layout()
    plt.show()





    





if __name__ =="__main__":
    main()