#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os


def valid_date(d: str) -> bool:
    if not d[0].isdigit():
        return False
    if d.startswith("0"):
        return False
    if "/" not in d:
        return False
    if not d.endswith(":"):
        return False
    dt = tuple(map(lambda x: int(x), d[:-1].split("/")))
    if dt[0] < 1 or dt[0] > 12:
        return False
    if dt[1] < 1 or dt[1] > 31:
        return False
    if dt[2] < 1 or dt[2] > 99:
        return False
    return True


def valid_time(t: str) -> bool:
    if not t[0].isdigit():
        return False
    if t.startswith("0"):
        return False
    if ":" not in t:
        return False
    if not t.endswith("am") and not t.endswith("pm"):
        return False
    if len(t) > 7:
        return False
    hour, rest = t.split(":")
    minute, _ = int(rest[:2]), rest[2:]
    hour = int(hour)
    if hour < 1 or hour > 12:
        return False
    if minute < 0 or minute > 59:
        return False
    return True


def to_24hr_time(t: str) -> tuple:
    hour, rest = t.split(":")
    minute, meridiem = int(rest[:2]), rest[2:]
    hour = int(hour)
    if meridiem == "am":
        if hour == 12:
            hour = 0
    if meridiem == "pm":
        if hour != 12:
            hour += 12
    return (hour, minute)


def time_delta(t1: str, t2: str) -> int:
    t1 = to_24hr_time(t1)
    t2 = to_24hr_time(t2)
    hours = t2[0] - t1[0]
    minutes = t2[1] - t1[1]
    if hours < 0:
        hours += 24
    if minutes < 0:
        minutes += 60
    return hours*60 + minutes


def parse_line(line: str):
    tokens = line.split()
    data = {"comment": ""}
    for i, tok in enumerate(tokens):
        if valid_date(tok):
            data["date"] = tok[:-1]
            continue
        if valid_time(tok):
            data[f"t{i}"] = tok
            continue
        if tok == "-":
            continue
        else:
            data["comment"] += f" {tok}"
    return data


def parse_log(filename: str):
    lines = open(filename).readlines()
    if lines[0].lower().strip() != "time log:":
        return -1
    time_record = []
    cur_comment = ""
    cur_date = ""
    cur_total = 0
    total_time = 0
    for i, line in enumerate(lines[1:]):
        try:
            parsed = parse_line(line)
            nkeys = len(parsed.keys())
            ts = tuple(filter(lambda k: k.startswith('t'), sorted(parsed.keys())))
            if nkeys == 1:
                cur_comment += f" | {parsed['comment']}"
            if nkeys == 2:
                td = time_delta(parsed[ts[0]], parsed[ts[1]])
                cur_total += td
                total_time += td
                cur_comment = ""
            if nkeys == 3:
                td = time_delta(parsed[ts[0]], parsed[ts[1]])
                cur_total += td
                total_time += td
                cur_comment += f" | {parsed['comment']}"
            if nkeys == 4:
                if i == 0:
                    cur_date = parsed['date']
                    cur_comment = parsed['comment']
                    td = time_delta(parsed[ts[0]], parsed[ts[1]])
                    cur_total += td
                    total_time += td
                else:
                    if cur_date != parsed['date']:
                        time_record.append((cur_date, cur_total, cur_comment))
                        cur_date = parsed['date']
                        cur_total = 0
                        cur_comment = ""
                    td = time_delta(parsed[ts[0]], parsed[ts[1]])
                    cur_total += td
                    total_time += td
                    cur_comment = parsed['comment']
        except Exception:
            print(f"error on line {i}")
            continue
    return time_record, total_time


def longest_task(records):
    maxtime = 0
    task = ""
    for r in records:
        if r[1] > maxtime:
            maxtime = r[1]
            task = r[2]
    return maxtime, task


def argparser():
    ap = argparse.ArgumentParser()
    ap.add_argument("filename", type=str, help="Log file to parse")
    return ap


def main():
    ap = argparser().parse_args()
    if os.path.exists(os.path.abspath(ap.filename)):
        records, total_time = parse_log(ap.filename)
        h, m = divmod(total_time, 60)
        print(f"Total time spent: {h} hours and {m} minutes")
        h, m = divmod(total_time // len(records), 60)
        print(f"Average time spent per day: {h} hours and {m} minutes")
        maxtime, task = longest_task(records)
        h, m = divmod(maxtime, 60)
        print(f"Most time consuming task(s): {h} hours, {m} minutes")
        print(f"{task}")


if __name__ == "__main__":
    main()
