#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from pathlib import Path
import sys

import requests


def argparser():
    """Set up argparser"""
    ap = argparse.ArgumentParser(prog="REST Request to Time Log Flask Service")
    ap.argument("files", metavar="FILE", type=str, nargs="+", help="Time Logs to convert to JSON")
    return ap


def main(f: Path) -> int:
    """Main function"""
    with open(f.absolute()) as fp:
        lines = fp.readlines()
    timelog = {
        "filename": f.name,
        "timelog": lines
    }
    tl_json = json.dumps(timelog)
    response = requests.post("localhost:5000/parse_timelog", json=tl_json)
    return response.status_code


if __name__ == "__main__":
    args = argparser().parse_args()
    for filename in args.files:
        f = Path(filename)
        if f.exists() and f.is_file():
            rc = main(f)
            print(f"Return Code: {rc}")

    sys.exit(-1)
