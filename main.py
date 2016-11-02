#!/usr/bin/env python
"""
Foursquare Archiver

Usage: ./main.py

TODO: follow pagination option
TODO: token from command line
TODO: better output when script is run
"""
import argparse
import datetime
import logging
import json
import os
import sys
from glob import glob

import requests

TOKEN = os.getenv('FOURSQUARE_OAUTH_TOKEN')

logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser(description='Archive your Foursquare checkins')
parser.add_argument('--data', dest='data_directory', default='data',
                    help='Path to directory to store JSON (default: data)')


def get_most_recent(directory):
    """Get the createdAt timestamp of the most recent data file."""
    # This isn't the most efficient way, but it is terse
    try:
        all_json = glob(os.path.join(directory, '**/*.json'), recursive=True)
        most_recent = sorted(all_json)[-1]
        return os.path.basename(most_recent).split('-')[0]
    except IndexError:
        return None


def download_self_checkins(data_directory='data', paginate=False):
    url = 'https://api.foursquare.com/v2/users/self/checkins'
    params = {
        'limit': 250,
        'oauth_token': TOKEN,
        'v': '20160612',
    }
    latestTimestamp = get_most_recent(os.path.join(data_directory, 'self'))
    if latestTimestamp:
        params['afterTimestamp'] = latestTimestamp
    offset = 0

    while True:
        params['offset'] = offset
        response = requests.get(
            url,
            params=params,
            headers={'user-agent': 'foursquare-archiver/0'},
        )
        items = response.json()['response']['checkins']['items']
        if not items:
            logger.info('End of the rainbow reached. %s', offset)
            break

        for item in items:
            timestamp = datetime.datetime.utcfromtimestamp(item['createdAt'])
            filepath = '{}/self/{}/{:02}/{}-{}.json'.format(
                data_directory, timestamp.year, timestamp.month, item['createdAt'], item['id'])

            if not os.path.isdir(os.path.dirname(filepath)):
                os.makedirs(os.path.dirname(filepath))

            with open(filepath, 'w') as fp:
                json.dump(item, fp, indent=2)
            os.utime(filepath, times=(item['createdAt'], item['createdAt']))
        offset += 250

        if not paginate:
            break

    if sys.stdout.isatty():
        print('Self: Downloaded: {} using timestamp: {}'
              .format(len(items), latestTimestamp))


def download_friend_checkins(data_directory='data', paginate=False):
    url = 'https://api.foursquare.com/v2/checkins/recent'
    params = {
        'limit': 100,
        'oauth_token': TOKEN,
        'v': '20161101',
    }
    latestTimestamp = get_most_recent(os.path.join(data_directory, 'friends'))
    if latestTimestamp:
        params['afterTimestamp'] = latestTimestamp
    response = requests.get(
        url,
        params=params,
        headers={'user-agent': 'foursquare-archiver/0'},
    )
    if not response.ok:
        logging.error(response.json())
        return

    items = response.json()['response']['recent']
    for item in items:
        timestamp = datetime.datetime.utcfromtimestamp(item['createdAt'])
        filepath = '{}/friends/{}/{:02}/{}-{}.json'.format(
            data_directory, timestamp.year, timestamp.month, item['createdAt'], item['id'])

        if not os.path.isdir(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))

        with open(filepath, 'w') as fp:
            json.dump(item, fp, indent=2)
        os.utime(filepath, times=(item['createdAt'], item['createdAt']))

    if sys.stdout.isatty():
        print('Friends: Downloaded: {} using timestamp: {}'
              .format(len(items), latestTimestamp))


if __name__ == '__main__':
    args = parser.parse_args()

    download_self_checkins(data_directory=args.data_directory)
    download_friend_checkins(data_directory=args.data_directory)
