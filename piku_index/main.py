#!/usr/bin/env python3
import argparse
from . import index


def main():
    # create parser
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-u', '--upload', action='store_true', help='upload updated index when completed')

    # parse and execute
    args = parser.parse_args()

    # update index
    index.update()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('')
