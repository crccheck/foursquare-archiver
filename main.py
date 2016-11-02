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

import requests

TOKEN = os.getenv('FOURSQUARE_OAUTH_TOKEN')

logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser(description='Archive your Foursquare checkins')
parser.add_argument('--data', dest='data_directory', default='data',
                    help='Path to directory to store JSON (default: data)')


def download_self_checkins(data_directory='data', paginate=False):
    url_format = ('https://api.foursquare.com/v2/users/self/checkins?'
                  'limit=250&oauth_token={}&v=20160612&offset={}'.format)
    offset = 0

    while True:
        response = requests.get(
            url_format(TOKEN, offset),
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


def download_friend_checkins(data_directory='data', paginate=False):
    url_format = ('https://api.foursquare.com/v2/checkins/recent?'
                  'limit=100&oauth_token={}&v=20161101'.format)

    response = requests.get(
        url_format(TOKEN),
        headers={'user-agent': 'foursquare-archiver/0'},
    )
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


if __name__ == '__main__':
    args = parser.parse_args()

    if not os.path.isdir(args.data_directory):
        logging.debug('Creating data directory %s', args.data_directory)
        os.mkdir(args.data_directory)

    download_self_checkins(data_directory=args.data_directory)
    download_friend_checkins(data_directory=args.data_directory)
