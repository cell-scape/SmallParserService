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
    ap.argument("-f", "--files", metavar="FILE", type=str, nargs="+", required=True, help="Time Logs to convert to JSON")
    ap.argument("-u", "--url", metavar="URL", type=str, required=True, help="URL")
    ap.argument("-p", "--port", metavar=PORT, type=int, required=True, help="Target Port")
    return ap


def main(f: Path, url: str, port: int):
    """Main function"""
    with open(f.absolute()) as fp:
        lines = fp.readlines()
    timelog = {
        "filename": f.name,
        "timelog": lines
    }
    tl_json = json.dumps(timelog)
    response = requests.post(f"{url}:{port}/parse_timelog", json=tl_json)
    return response


#if __name__ == "__main__":
#    args = argparser().parse_args()
#    for filename in args.files:
#        f = Path(filename)
#        if f.exists() and f.is_file():
#            response = main(f)
#            print(f"Response: {json.loads(response.json)}}")
#    sys.exit(-1)
