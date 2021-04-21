import argparse
import random
import json
def main():
	p = argparse.ArgumentParser()

	p.add_argument('data', help='path to a json file')
	p.add_argument("-n", "--num", type=int, help="Size of the sample", required=True)

	args = p.parse_args()

	with open(args.data) as fp:
		data = json.load(fp)

	sample = random.sample(data, args.num)

	jstring = json.dumps(sample)

	print(jstring)



if __name__ == "__main__":
	main()