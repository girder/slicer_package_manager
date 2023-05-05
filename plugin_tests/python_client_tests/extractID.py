import re


def extractID(file):
    with open(file) as f:
        res = re.search(r'\([a-z0-9]*\)', f.read())
        if res:
            _id = res.group(0)
            return _id[1:-1]


if __name__ == '__main__':
    from sys import argv
    print(extractID(argv[1]))
