import argparse

parser = argparse.ArgumentParser(description='Unsupervised training')
parser.add_argument("--file", type=str, default="", help="Initialization seed")


params = parser.parse_args()


with open(params.file, "r") as r:
    line = r.readline()
    count = 0
    while line:
        count += 1
        line = r.readline()
    print count
