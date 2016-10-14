#!/usr/bin/env python
import os
import pytz
import time
import json
import requests
from hashlib import sha1
from calendar import timegm
from datetime import datetime

from requests.compat import quote

API_KEY = ""
API_SECRET = ""
API_BASE_URL = "https://us.pycon.org/2016/"
SCHEDULE_JSON_URL = "https://us.pycon.org/2016/schedule/conference.json"


class API(object):
    def __init__(self):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.base_url = API_BASE_URL

    def get(self, endpoint, **kwargs):
        return self.request('GET', endpoint, **kwargs)

    def post(self, endpoint, body):
        return self.request('POST', endpoint, json.dumps(body))

    def request(self, method, endpoint, body='', **kwargs):
        """Make a request to the PyCon website, and return the result."""
        # The PyCon website runs using HTTPS, but localhost doesn't.
        # Determine the right thing.

        url = self.base_url + endpoint

        # If keyword arguments are provided, append them to
        # the URI.
        if kwargs:
            url += '?' + '&'.join(
                ['%s=%s' % (k, quote(str(v))) for k, v in kwargs.items()],
            )

        # Generate the appropriate request signature to certify
        # that this is a valid request.
        uri = "/" + url.partition("://")[2].partition("/")[2]
        signature = self._sign_request(uri, method, body)

        # Add the appropriate content-type header.
        if method == 'POST':
            signature['Content-Type'] = 'application/json'

        # Make the actual request to the PyCon website.
        r = requests.request(
            method, url, data=body, headers=signature, verify=False)
        r.raise_for_status()

        # OK, all is well; return the response.
        return r.json()

    def _sign_request(self, uri, method, body=''):
        """Return a dictionary with the appropriate headers with which
        to sign this request.
        """
        # What time is it right now? We use the current timestamp
        # as part of the request signature.
        timestamp = timegm(datetime.now(tz=pytz.UTC).timetuple())

        # Create the "base string", and then SHA1 hash it.
        base_string = unicode(''.join((
            self.api_secret,
            unicode(timestamp),
            method.upper(),
            uri,
            body,
        )))

        # Return a signature dictionary.
        return {
            'X-API-Key': self.api_key,
            'X-API-Signature': sha1(base_string.encode('utf-8')).hexdigest(),
            'X-API-Timestamp': timestamp,
        }


def cached_get(outf_name, func):
    data_file = os.path.join(os.path.dirname(__file__), outf_name)
    if not os.path.exists(data_file):
        res = func()
    elif time.time() - os.path.getmtime(data_file) > 600:
        res = func()
    else:
        with open(data_file) as f:
            return json.load(f)

    with open(data_file, "w") as f:
        json.dump(res, f)

    return res


def _download_schedule():
    resp = requests.get(SCHEDULE_JSON_URL, verify=False)
    resp.raise_for_status()
    return resp.json()


def get_schedule():
    schedule = cached_get(".schedule.json", _download_schedule)
    return [
        {
            "abstract": "",
            "authors": [
                "Lorena Barba",
            ],
            "conf_key": 100000,
            "contact": [],
            "description": "Keynote",
            "duration": 40,
            "start": "2016-05-30T09:30:00",
            "end": "2016-05-30T010:10:00",
            "kind": "keynote",
            "license": "CC",
            "name": "Keynote",
            "released": True,
            "room": "Keynote",
            "tags": ""
        },
        {
            "abstract": "",
            "authors": [
                "Guido van Rossum",
            ],
            "conf_key": 100000,
            "contact": [],
            "description": "Python Language",
            "duration": 40,
            "start": "2016-05-31T09:00:00",
            "end": "2016-05-31T009:40:00",
            "kind": "keynote",
            "license": "CC",
            "name": "Python Language",
            "released": True,
            "room": "Keynote",
            "tags": ""
        },
        {
            "abstract": "",
            "authors": [
                "Parisa Tabriz",
            ],
            "conf_key": 100000,
            "contact": [],
            "description": "Keynote",
            "duration": 40,
            "start": "2016-05-31T09:40:00",
            "end": "2016-05-31T010:20:00",
            "kind": "keynote",
            "license": "CC",
            "name": "Keynote",
            "released": True,
            "room": "Keynote",
            "tags": ""
        },
        {
            "abstract": "",
            "authors": [
                "Van Lindberg",
            ],
            "conf_key": 100000,
            "contact": [],
            "description": "Python Software Foundation",
            "duration": 20,
            "start": "2016-06-01T09:00:00",
            "end": "2016-06-01T009:20:00",
            "kind": "keynote",
            "license": "CC",
            "name": "Python Software Foundation",
            "released": True,
            "room": "Keynote",
            "tags": ""
        },
        {
            "abstract": "",
            "authors": [
                "Cris Ewing",
            ],
            "conf_key": 100000,
            "contact": [],
            "description": "Keynote",
            "duration": 40,
            "start": "2016-06-01T09:20:00",
            "end": "2016-06-01T010:00:00",
            "kind": "keynote",
            "license": "CC",
            "name": "Keynote",
            "released": True,
            "room": "Keynote",
            "tags": ""
        },
        {
            "abstract": "",
            "authors": [
                "K Lars Lohn",
            ],
            "conf_key": 100000,
            "contact": [],
            "description": "Keynote",
            "duration": 40,
            "start": "2016-06-01T15:10:00",
            "end": "2016-06-01T015:50:00",
            "kind": "keynote",
            "license": "CC",
            "name": "Keynote",
            "released": True,
            "room": "Keynote",
            "tags": ""
        },
    ] + schedule


def get_session_staff():
    staff = cached_get(
        ".session-staff.json",
        lambda: API().get("schedule/session-staff.json"))
    res = {}
    for session_staff in staff["data"]:
        ck = session_staff["conf_key"]
        assert ck not in res
        res[ck] = session_staff
    return res
