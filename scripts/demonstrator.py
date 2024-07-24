#!/usr/bin/env
"""
just a sample script to show expected usage
<replace as needed>

usage:
  pdm run scripts/demonstrator.py
"""

import argparse
import logging
import sys

import feeph.tca953x

LH = logging.getLogger("app")

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname).1s: %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser(prog="demonstrator", description="demonstrate usage")
    parser.add_argument("-i", "--input-value", type=int, default=1)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        LH.setLevel(level=logging.DEBUG)

    LH.debug("start")

    value = feeph.tca953x.function1(args.input_value)
    LH.info("Provided value: %d", value)

    LH.debug("exit")
    sys.exit(0)
