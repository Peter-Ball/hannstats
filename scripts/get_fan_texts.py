import argparse
import json
import os

def main():
	parser = argparse.ArgumentParser()

	parser.add_argument("data", help="Path to the .json file with the fandom data")
	parser.add_argument("outdir", help="Path to the output directory")

	args = parser.parse_args()

	with open(args.data) as fp:
		data = json.load(fp)

	for story in data:
		fname = story['id'] + '.txt'
		outpath = os.path.join(args.outdir, fname)

		full_text = '\n'.join([chap['text'] for chap in story['chapters']])

		with open(outpath, 'w') as fp:
			fp.write(full_text)


if __name__ == "__main__":
	main()