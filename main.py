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

    if not os.path.isdir(data_directory):
        logging.debug('Creating data directory %s', data_directory)
        os.mkdir(data_directory)

    while True:
        response = requests.get(url_format(TOKEN, offset))
        items = response.json()['response']['checkins']['items']
        if not items:
            logger.info('End of the rainbow reached. %s', offset)
            break

        for item in items:
            timestamp = datetime.datetime.utcfromtimestamp(item['createdAt'])
            filepath = '{}/{}/{}-{}.json'.format(
                data_directory, timestamp.year, item['createdAt'], item['id'])

            if not os.path.isdir(os.path.join(data_directory, str(timestamp.year))):
                os.mkdir(os.path.join(data_directory, str(timestamp.year)))

            with open(filepath, 'w') as fp:
                json.dump(item, fp, indent=2)
            os.utime(filepath, times=(item['createdAt'], item['createdAt']))
        offset += 250

        if not paginate:
            break


if __name__ == '__main__':
    args = parser.parse_args()
    download_self_checkins(data_directory=args.data_directory)
