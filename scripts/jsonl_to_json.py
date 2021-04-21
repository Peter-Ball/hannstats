import jsonlines
import json
import argparse

def main():
	p = argparse.ArgumentParser()

	p.add_argument("data", help="path to jsonl")

	args = p.parse_args()

	with jsonlines.open(args.data) as fp:
		data = [obj for obj in fp]

	jstring = json.dumps(data)

	print(jstring)



if __name__ == "__main__":
	main()