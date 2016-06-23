Foursquare Archiver
===================

Archive your Foursquare checkin data locally.

This is a Python script for saving the json data from Foursuare's `checkins`
resource https://developer.foursquare.com/docs/users/checkins .


Getting started
---------------

Install requirements:

    make install

Get yourself a Foursquare Oauth token. See https://developer.foursquare.com/docs/explore

Set the `FOURSQUARE_OAUTH_TOKEN` environment variable


Usage
=====

Run `main.py`. A `data` directory will be created

    /path/to/main.py

### With Docker

You can also run this via Docker with something like:

    docker run -e FOURSQUARE_OAUTH_TOKEN=AAAABBBBBCCCCDDDD -v /tmp/data:/app/data crccheck/foursquare-archiver
