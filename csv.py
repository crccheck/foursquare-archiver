"""
Utility to get coordinates from Foursquare checkin history JSON.

Usage: python csv.py topleft bottomright

Example: python csv.py 36.5,-106.65 25.837,-93.5 | pbcopy

"""
import json
import sys
from collections import Counter
from glob import iglob


def get_all_points(top, right, bottom, left):
    all_json = iglob('data/**/*.json', recursive=True)
    for path in all_json:
        with open(path) as fp:
            data = json.load(fp)

        if 'venue' not in data:
            continue

        # restrict to a bounding box
        if (bottom < data['venue']['location']['lat'] < top and
                left < data['venue']['location']['lng'] < right):
            yield (data['venue']['location']['lat'], data['venue']['location']['lng'])


if __name__ == '__main__':
    print('lat,lng,count')
    lat1, lng1 = map(float, sys.argv[1].split(','))
    lat2, lng2 = map(float, sys.argv[2].split(','))
    counts = Counter(get_all_points(
        max(lat1, lat2),
        max(lng1, lng2),
        min(lat1, lat2),
        min(lng1, lng2),
    ))
    for (lat, lng), count in counts.items():
        print('{},{},{}'.format(lat, lng, count))
