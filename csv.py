"""
Utility to get coordinates from Foursquare checkin history JSON.

Usage:
    python csv.py <topleft> <bottomright>
    python csv.py <bboxstring>

Example:
    python csv.py 36.5,-106.65 25.837,-93.5 | pbcopy
    python csv.py -74.0237331390381,40.69580229372344,-73.96682739257814,40.75258879956551
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
    if len(sys.argv) == 3:
        lat1, lng1 = map(float, sys.argv[1].split(','))
        lat2, lng2 = map(float, sys.argv[2].split(','))
        top = max(lat1, lat2)
        right = max(lng1, lng2)
        bottom = min(lat1, lat2)
        left = min(lng1, lng2)
    elif len(sys.argv) == 2:
        left, bottom, right, top = map(float, sys.argv[1].split(','))
    else:
        print(__doc__)
        exit(1)

    counts = Counter(get_all_points(top, right, bottom, left))
    print('lat,lng,count')
    for (lat, lng), count in counts.items():
        print('{},{},{}'.format(lat, lng, count))
