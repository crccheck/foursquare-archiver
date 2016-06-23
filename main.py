#!/usr/bin/env python
"""
Foursquare Archiver

Usage: ./main.py

TODO: specify data directory
TODO: follow pagination option
TODO: token from command line
TODO: better output when script is run
"""
import datetime
import logging
import json
import os

import requests


URL_FORMAT = ('https://api.foursquare.com/v2/users/self/checkins?'
              'limit=250&oauth_token={}&v=20160612&offset={}'.format)

TOKEN = os.getenv('FOURSQUARE_OAUTH_TOKEN')


logger = logging.getLogger(__name__)


def main(paginate=False):
    offset = 0

    if not os.path.isdir('data'):
        os.mkdir('data')

    while True:
        response = requests.get(URL_FORMAT(TOKEN, offset))
        items = response.json()['response']['checkins']['items']
        if not items:
            logger.info('End of the rainbow reached. %s', offset)
            break

        for item in items:
            timestamp = datetime.datetime.utcfromtimestamp(item['createdAt'])
            filepath = 'data/{}/{}-{}.json'.format(
                timestamp.year, item['createdAt'], item['id'])

            if not os.path.isdir(os.path.join('data', str(timestamp.year))):
                os.mkdir(os.path.join('data', str(timestamp.year)))

            with open(filepath, 'w') as fp:
                json.dump(item, fp, indent=2)
            os.utime(filepath, times=(item['createdAt'], item['createdAt']))
        offset += 250

        if not paginate:
            break


if __name__ == '__main__':
    main()
