#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from pathlib import Path
import sys

import requests


def tl_request(timelog: dict, dest: str) -> str:
    """Send timelog parse request"""
    timelog = json.dumps(timelog)
    return requests.post(dest, json=timelog)


def argparser():
    """Set up argparser"""
    ap = argparse.ArgumentParser(prog="REST Request to Time Log Flask Service")
    ap.add_argument("-f", "--files", metavar="FILE", type=str, nargs="+", required=True, help="Time Logs to convert to JSON")
    ap.add_argument("-u", "--url", metavar="URL", type=str, required=True, help="URL")
    ap.add_argument("-p", "--port", metavar="PORT", type=int, required=True, help="Target Port")
    ap.add_argument("-e", "--endpoint", metavar="PATH", type=str, required=True, help="Target resource path")
    return ap


def main(f: Path, url: str, port: int, endpoint: str) -> int:
    """Main function"""
    with open(f.absolute()) as fp:
        lines = fp.readlines()
    timelog = {
        "filename": f.name,
        "timelog": lines
    }
    dest = f"{url}:{port}/{endpoint}"
    response = tl_request(timelog, dest)
    print("\n".join(response.json()['output']))
    return response.status_code


if __name__ == "__main__":
    args = argparser().parse_args()
    for filename in args.files:
        f = Path(filename)
        if f.exists() and f.is_file():
            rc = main(f)
            print(f"Response Code: {rc}")
            if rc == 200:
                continue
            else:
                sys.exit(rc)
        else:
            print(f"file {f.name} not found")
            sys.exit(-1)
    sys.exit(0)
