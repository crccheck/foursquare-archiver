#!/usr/bin/env python
"""
One-time migration: convert per-checkin JSON files to per-year JSONL files.

Usage:
    python migrate.py [--data DATA_DIR]

Old layout: data/self/YEAR/MONTH/TIMESTAMP-ID.json
New layout: data/self/YEAR.jsonl

Prints a summary of files written. Does NOT delete old JSON files.
"""

import argparse
import collections
import datetime
import json
import os
from glob import glob

parser = argparse.ArgumentParser(description="Migrate JSON checkins to JSONL format")
parser.add_argument(
    "--data",
    dest="data_directory",
    default="data",
    help="Path to data directory (default: data)",
)


def migrate_directory(directory: str) -> None:
    json_files = glob(os.path.join(directory, "**/*.json"), recursive=True)
    if not json_files:
        print(f"  No JSON files found in {directory}")
        return

    by_year: dict[int, list[dict]] = collections.defaultdict(list)
    for path in json_files:
        with open(path) as fp:
            data = json.load(fp)
        year = datetime.datetime.fromtimestamp(data["createdAt"], datetime.UTC).year
        by_year[year].append(data)

    total = 0
    for year, items in sorted(by_year.items()):
        items.sort(key=lambda x: x["createdAt"])
        out_path = os.path.join(directory, f"{year}.jsonl")
        with open(out_path, "w") as fp:
            for item in items:
                fp.write(json.dumps(item) + "\n")
        print(f"  Wrote {len(items):>5} entries → {out_path}")
        total += len(items)

    print(f"  Total: {total} entries from {len(json_files)} JSON files")


if __name__ == "__main__":
    args = parser.parse_args()

    for subdir in ("self", "friends"):
        path = os.path.join(args.data_directory, subdir)
        print(f"\n{subdir}:")
        if os.path.isdir(path):
            migrate_directory(path)
        else:
            print(f"  Directory not found: {path}")

    print("\nDone. Old JSON files have NOT been deleted.")
    print("Verify the JSONL files, then remove the old files manually if desired.")
