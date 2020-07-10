# -*- coding: utf-8 -*-

import re


def extractID(file):
    with open(file, 'r') as f:
        res = re.search(r'\([a-z0-9]*\)', f.read())
        if res:
            id = res.group(0)
            return id[1:-1]


if __name__ == '__main__':
    from sys import argv
    print(extractID(argv[1]))
