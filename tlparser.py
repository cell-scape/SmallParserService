#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path
import sys


def valid_date(d: str) -> bool:
    """
    valid_date(d: str) -> bool

    input:
        - d: a string representing a date in the form MM/DD/YY

    output:
        - boolean
    """
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
    """
    valid_time(t: str) -> bool

    input:
        - t: a string representing a time stamp of the form HH:MM[am|pm]

    output:
        - boolean
    """
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


def to_days(d: str) -> int:
    """
    to_days(d: str) -> int:

    input:
        - d: a string representing a validated date
    output: 
        - int: days into the current century

    Days = (total days of n-1 months) + days + (total days of n-1 years) + leap years
    """
    mm, dd, yy = map(lambda n: int(n), d.split('/'))
    months = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    days = dd + yy*365 + (yy // 4)
    if mm > 1:
        days += sum(months[:(mm-1)])
    return days


def to_minutes(t: str) -> int:
    """
    to_minutes(t: str) -> int

    input:
        - t: A string representing a validated timestamp

    output:
        - int: minutes into the current day
    """
    hour, rest = t.split(":")
    minute, meridiem = int(rest[:2]), rest[2:].lower()
    hour = int(hour)
    if meridiem == "am":
        if hour == 12:
            hour = 0
    if meridiem == "pm":
        if hour < 12:
            hour += 12
    return hour*60 + minute


def date_delta(d1: str, d2: str) -> int:
    """
    date_delta(d1: str, d2: str) -> int:

    input:
        - d1: a valid date of the form MM/DD/YY
        - d2: a valid date monotonically larger than d1
    output:
        - int: the difference d2-d1 of elapsed days
    """
    d1 = to_days(d1)
    d2 = to_days(d2)
    return (d2 - d1) % (100 * 365 + 100 // 4)  # days in a century + leap days


def time_delta(t1: str, t2: str) -> int:
    """
    time_delta(t1: str, t2: str) -> int

    input:
        - t1: a string representing a timestamp of the form HH:MM[am|pm]
        - t2: a string representing a timestamp of the form HH:MM[am|pm], strictly greater than t1
    output:
        - int: the strictly positive difference between t2 - t1, modulo 1440
    """
    t1 = to_minutes(t1)
    t2 = to_minutes(t2)
    return (t2 - t1) % 1440


def parse_line(line: str) -> dict:
    """
    parse_line(line: str) -> dict

    input:
        - line: a line as a string from the time log file under scrutiny
    output:
        - data: a dictionary containing the different types of tokens in the line

    Tokenizes each line into a date, an even number of timestamps, and a comment string
    """
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


def parse_log(filename: str) -> tuple:
    """
    parse_log(filename: str) -> tuple

    input:
        - filename: a path to a time log file
    output:
        - (time_records, total_time): a tuple of time_records, and the total accumulated time

    time_record -> (date, time spent, accumulated comments)

    Parses the time log file by checking the number of valid tokens in each line.
    Accumulates total time, and saves individual times for each date/task.
    Multiline comments are accumulated together, blank dates are assumed to be the same.
    """
    with open(filename) as f:
        lines = f.readlines()
    if lines[0].lower().strip() != "time log:":
        return -1
    time_record = []
    cur_comment = []
    cur_date = ""
    cur_total = 0
    total_time = 0
    for i, line in enumerate(lines[1:]):
        try:
            parsed = parse_line(line)
            nkeys = len(parsed.keys())
            ts = tuple(filter(lambda k: k.startswith('t'), sorted(parsed.keys())))
            if nkeys == 1:
                comment = parsed['comment'].strip()
                if comment:
                    cur_comment.append(comment)
            if nkeys == 2:
                td = time_delta(parsed[ts[0]], parsed[ts[1]])
                cur_total += td
                total_time += td
                cur_comment = []
            if nkeys == 3:
                td = time_delta(parsed[ts[0]], parsed[ts[1]])
                cur_total += td
                total_time += td
                comment = parsed['comment'].strip()
                if comment:
                    cur_comment.append(comment)
            if nkeys == 4:
                if i == 0:
                    cur_date = parsed['date']
                    comment = parsed['comment'].strip()
                    if comment:
                        cur_comment.append(f"{comment}")
                    td = time_delta(parsed[ts[0]], parsed[ts[1]])
                    cur_total += td
                    total_time += td
                else:
                    if cur_date != parsed['date']:
                        time_record.append((cur_date, cur_total, f"\n{' '*(len(cur_date)+2)}".join(cur_comment)))
                        cur_date = parsed['date']
                        cur_total = 0
                        cur_comment = []
                    td = time_delta(parsed[ts[0]], parsed[ts[1]])
                    cur_total += td
                    total_time += td
                    comment = parsed['comment'].strip()
                    if comment:
                        cur_comment.append(comment)
        except Exception:
            print(f"error on line {i}")
            continue
    return time_record, total_time


def longest_task(records: list) -> tuple:
    """
    longest_task(records: list[tuple]) -> tuple[int, str]

    input:
        - records: a list of time_record tuples (date, duration, task)
    output:
        - (): the maximum duration and the corresponding task or comments
    """
    maxtime = 0
    maxrecord = None
    for r in records:
        if r[1] > maxtime:
            maxtime = r[1]
            maxrecord = r
    return maxrecord


def working_days(records: list) -> tuple:
    """
    working_days(records: list[tuple]) -> tuple[int, int]

    input:
        - records: a list of tuples (date, duration, task)
    output:
        - (int, int): Total number of days worked, total number of days elapsed
    """
    worked = {r[0] for r in records}
    elapsed = date_delta(records[0][0], records[-1][0])
    return worked, elapsed


def record_stats(records: list, total: int, filename: str) -> dict:
    """
    record_stats(filename: str) -> dict:

    input:
        - filename: path to log file
    output:
        - dict: Organized dictionary of statistics and data
    """
    stats = {'filename': filename, 'total': total}
    stats['dates'], stats['elapsed'] = working_days(records)
    stats['durations'] = map(lambda r: r[1], records)
    stats['mean'] = stats['total'] / len(stats['dates'])
    ts = sorted(stats['durations'])
    if len(ts) % 2 == 0:
        stats['median'] = (ts[len(ts) // 2] + ts[len(ts) // 2 + 1]) / 2
    else:
        stats['median'] = ts[len(ts) // 2 + 1]
    stats['longest'] = longest_task(records)
    return stats


def format_output(stats: dict) -> list:
    """
    format_output(stats: dict) -> str:

    input:
        - stats: dictionary of statistics collected from time log
    output:
        - list: formatted output for terminal or template rendering
    """
    output = [f"Statistics for {stats['filename']}:"]
    output.append(f"{'-'*(len(stats['filename'])+16)}")

    h, m = divmod(stats['total'], 60)
    output.append(f"Total time spent: {h} hours, {m} minutes")
    output.append(f"Total days worked: {len(stats['dates'])}")
    output.append(f"Total days elapsed: {stats['elapsed']}\n")

    h, m = divmod(stats['mean'], 60)
    output.append(f"Mean time spent per working day: {h:.2f} hours, {m:.2f} minutes")
    h, m = divmod(stats['median'], 60)
    output.append(f"Median time spent: {h:.2f} hours, {m:.2f} minutes\n")

    date, maxtime, task = stats['longest']
    h, m = divmod(maxtime, 60)
    output.append("Longest working session:")
    output.append(f"{date}: {task}")
    output.append(f"Time spent: {h} hours, {m} minutes\n")

    return output


def argparser():
    """Set up argument parser."""
    ap = argparse.ArgumentParser(prog="Time Log Parser")
    ap.add_argument("files",
                    type=str,
                    metavar="FILE",
                    nargs='+',
                    help="Log files to parse")
    return ap


def main(f: Path) -> str:
    """Run all parser functions."""
    records, total = parse_log(f.absolute())
    stats = record_stats(records, total, f.name)
    results = format_output(stats)
    return "\n".join(results)


if __name__ == "__main__":
    args = argparser().parse_args()
    for filename in args.files:
        f = Path(filename)
        if f.exists() and f.is_file():
            results = main(f)
            print(results)
        else:
            print(f"file {f.name} not found")
            sys.exit(-1)
    sys.exit(0)
