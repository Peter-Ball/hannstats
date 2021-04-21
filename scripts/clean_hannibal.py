## This is my procedure for cleaning the scrape from the 'Hannibal (TV)' tag

import argparse
import json
import numpy as np
from hannstats import utils

def main():
    p = argparse.ArgumentParser()

    p.add_argument("data", help="path to the Hannibal data (json format)")

    args = p.parse_args()

    with open(args.data) as fp:
        data = json.load(fp)

    # REDUCE SET SIZE
    ## limit for only fics where Hannibal is the primary fandom
    data = [story for story in data if story['fandoms'][0] == 'Hannibal (TV)']

    ## Remove of fan-art and podcasts (something totally worth looking at
    ## in a follow-up project!)
    unwanted_tags = ['Fanart', 'Podfic']

    data = [story for story in data if all(tag not in story['additional_tags'] for tag in unwanted_tags)]

    ## Finally, limit length to between the 5th and 95th quantile to remove outliers
    word_counts = np.array([story['words'] for story in data])
    q_05 = np.quantile(word_counts, 0.05)
    q_95 = np.quantile(word_counts, 0.95)

    data = [story for story in data if q_05 < story['words'] and story['words'] < q_95]

    # CLEAN TEXT
    for story in data:
        for chapter in story['chapters']:
            chapter['text'] = utils.clean_AO3_text(chapter['text'])

    # PRINT

    print(json.dumps(data))



if __name__ == "__main__":
    main()