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
from collections import Counter
from glob import iglob


def get_all_points(top, right, bottom, left):
    all_jsonl = iglob("data/**/*.jsonl", recursive=True)
    for path in all_jsonl:
        with open(path) as fp:
            for line in fp:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)

                if "venue" not in data:
                    continue

                # restrict to a bounding box
                if (
                    bottom < data["venue"]["location"]["lat"] < top
                    and left < data["venue"]["location"]["lng"] < right
                ):
                    yield (data["venue"]["location"]["lat"], data["venue"]["location"]["lng"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("bbox", nargs="+", help="Bounding box: two 'lat,lng' corners or one 'lng,lat,lng,lat' string (optionally prefixed with #)")
    parser.add_argument("--margin", type=float, default=0.20, help="Fractional margin to expand the bounding box (default: 0.20)")
    args = parser.parse_args()

    if len(args.bbox) == 2:
        lat1, lng1 = map(float, args.bbox[0].split(","))
        lat2, lng2 = map(float, args.bbox[1].split(","))
        top = max(lat1, lat2)
        right = max(lng1, lng2)
        bottom = min(lat1, lat2)
        left = min(lng1, lng2)
    elif len(args.bbox) == 1:
        left, bottom, right, top = map(float, args.bbox[0].split(","))
    else:
        parser.print_help()
        exit(1)

    lat_margin = (top - bottom) * args.margin
    lng_margin = (right - left) * args.margin
    top += lat_margin
    bottom -= lat_margin
    right += lng_margin
    left -= lng_margin

    counts = Counter(get_all_points(top, right, bottom, left))
    print("lat,lng,count")
    for (lat, lng), count in counts.items():
        print("{},{},{}".format(lat, lng, count))
