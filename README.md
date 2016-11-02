Foursquare Archiver
===================

Archive your Foursquare checkin data locally.

This is a Python script for saving the json data from Foursuare's `checkins`
resource https://developer.foursquare.com/docs/users/checkins .


Getting started
---------------

In a virtualenv, install requirements:

    make install

Get yourself a Foursquare Oauth token. See https://developer.foursquare.com/docs/explore

Set the `FOURSQUARE_OAUTH_TOKEN` environment variable

    export FOURSQUARE_OAUTH_TOKEN=AAAABBBBBCCCCDDDD


Usage
-----

Run `main.py`. A `data` directory will be created if it does not already exist.

    ./main.py

### With Docker

You can also run this via Docker with something like:

    docker run --rm -e FOURSQUARE_OAUTH_TOKEN=AAAABBBBBCCCCDDDD -v /tmp/data:/app/data:rw crccheck/foursquare-archiver --data=/app/data
