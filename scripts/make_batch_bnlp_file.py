# Utility script to take a directory of text files and
# produce the formatted output for BookNLP's BatchBookNLP
# File.

import argparse
import os

def main():
	p = argparse.ArgumentParser()

	p.add_argument("textdir", help="Path to a directory with text files")

	args = p.parse_args()

	files = [f for f in os.listdir(args.textdir) if f[-4:] == '.txt']

	identifiers = [f[:-4] for f in files]

	for fname, ident in zip(files, identifiers):
		line = ident + '\t' + os.path.join(args.textdir, fname)
		print(line)

if __name__ == "__main__":
	main()