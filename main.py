#!/usr/bin/env python
"""
Foursquare Archiver

Usage: ./main.py

TODO: follow pagination option
TODO: token from command line
TODO: better output when script is run
"""

import argparse
import collections
import datetime
import logging
import json
import os
import sys
from glob import glob

import requests

TOKEN = os.getenv("FOURSQUARE_OAUTH_TOKEN")
CLIENT_ID = os.getenv("FOURSQUARE_CLIENT_ID")
CALLBACK_URL = "http://localhost:8000"

logger = logging.getLogger(__name__)


def print_auth_instructions():
    if CLIENT_ID:
        auth_url = (
            f"https://foursquare.com/oauth2/authenticate"
            f"?client_id={CLIENT_ID}&response_type=token&redirect_uri={CALLBACK_URL}"
        )
        print(f"\nGet a new token by visiting:\n  {auth_url}")
        print("\nAfter approving, copy the access_token from the redirect URL and run:")
    else:
        print("\nSet FOURSQUARE_CLIENT_ID to get an auth URL, then run:")
    print("  export FOURSQUARE_OAUTH_TOKEN=<token>\n")


parser = argparse.ArgumentParser(description="Archive your Foursquare checkins")
parser.add_argument(
    "--data",
    dest="data_directory",
    default="data",
    help="Path to directory to store JSON (default: data)",
)
parser.add_argument(
    "--no-resume",
    action="store_true",
    help="Ignore existing data and download all checkins from the beginning",
)


def get_most_recent(directory):
    """Get the createdAt timestamp of the most recent entry in the latest JSONL file."""
    jsonl_files = glob(os.path.join(directory, "*.jsonl"))
    if not jsonl_files:
        return None
    latest_file = sorted(jsonl_files)[-1]
    last_line = None
    with open(latest_file) as fp:
        for line in fp:
            line = line.strip()
            if line:
                last_line = line
    if last_line is None:
        return None
    return json.loads(last_line)["createdAt"]


def _write_jsonl_items(directory, items, mode):
    """Group items by year and write to JSONL files."""
    by_year = collections.defaultdict(list)
    for item in items:
        year = datetime.datetime.fromtimestamp(item["createdAt"], datetime.UTC).year
        by_year[year].append(item)

    os.makedirs(directory, exist_ok=True)
    for year, year_items in by_year.items():
        year_items.sort(key=lambda x: x["createdAt"])
        filepath = os.path.join(directory, f"{year}.jsonl")
        with open(filepath, mode) as fp:
            for item in year_items:
                fp.write(json.dumps(item) + "\n")


def download_self_checkins(data_directory="data", resume=True):
    url = "https://api.foursquare.com/v2/users/self/checkins"
    params = {
        "limit": 250,
        "v": "20160612",
    }
    headers = {
        "user-agent": "foursquare-archiver/0",
        "Authorization": f"Bearer {TOKEN}",
    }
    dest = os.path.join(data_directory, "self")
    latestTimestamp = get_most_recent(dest)
    if resume and latestTimestamp:
        params["afterTimestamp"] = latestTimestamp
    offset = 0
    all_items = []

    while True:
        params["offset"] = offset
        response = requests.get(url, params=params, headers=headers)
        if not response.ok:
            logging.error(response.json())
            if response.status_code in (401, 403):
                print_auth_instructions()
            return
        items = response.json()["response"]["checkins"]["items"]
        if not items:
            logger.info("End of the rainbow reached. %s", offset)
            break
        all_items.extend(items)
        offset += 250

    if all_items:
        mode = "a" if resume else "w"
        _write_jsonl_items(dest, all_items, mode)

    if sys.stdout.isatty():
        print(
            "Self: Downloaded: {} using timestamp: {}".format(
                len(all_items), latestTimestamp
            )
        )


def download_friend_checkins(data_directory="data"):
    url = "https://api.foursquare.com/v2/checkins/recent"
    params = {
        "limit": 100,
        "v": "20161101",
    }
    headers = {
        "user-agent": "foursquare-archiver/0",
        "Authorization": f"Bearer {TOKEN}",
    }
    dest = os.path.join(data_directory, "friends")
    latestTimestamp = get_most_recent(dest)
    if latestTimestamp:
        params["afterTimestamp"] = latestTimestamp
    response = requests.get(url, params=params, headers=headers)
    if not response.ok:
        logging.error(response.json())
        return

    items = response.json()["response"]["recent"]
    if items:
        _write_jsonl_items(dest, items, "a")

    if sys.stdout.isatty():
        print(
            "Friends: Downloaded: {} using timestamp: {}".format(
                len(items), latestTimestamp
            )
        )


if __name__ == "__main__":
    args = parser.parse_args()

    download_self_checkins(data_directory=args.data_directory, resume=not args.no_resume)
    download_friend_checkins(data_directory=args.data_directory)
