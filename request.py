#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from pathlib import Path

import requests


def argparser():
    ap = argparse.ArgumentParser(prog="REST Request to Time Log Flask Service")
    ap.argument("filename", type=str, help="Time Log to convert to JSON")
    return ap


def main():
    pass


if __name__ == "__main__":
