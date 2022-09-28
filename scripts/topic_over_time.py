from argparse import ArgumentParser
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def get_args():
    p = ArgumentParser()

    p.add_argument("topic_frame")
    p.add_argument("topic_num")
    p.add_argument("--character_list", nargs="+",)

    args = p.parse_args()

    return args

def main():

    args = get_args()

    df = pd.read_csv(args.topic_frame, sep='\t')
    df["Episode"] = df["item_num"] + 1
    df["Topic %"] = df[args.topic_num] * 100

    df = df[df["speaker"].isin(args.character_list)]

    sns.lineplot(data=df, x='Episode', y="Topic %", hue="speaker")

    plt.title("Percentage of Dialog Sourced from Topic {}".format(args.topic_num))

    plt.show()




if __name__ == "__main__":
    main()