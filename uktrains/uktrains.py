#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

import datetime
import json
import logging
import sys

from collections import namedtuple
from cStringIO import StringIO

import requests
import requests_cache

import lxml.html

__all__ = ['search_trains', 'get_trains', 'get_station', 'search_stations']


_SEARCH_URL = 'http://ojp.nationalrail.co.uk/find/stationsDLRLU/{search}'
_TRAINS_URL = ('http://ojp.nationalrail.co.uk/service/timesandfares/'
               '{from_}/{to}/{DDMMYY}/{HHMM}/dep?excludeslowertrains')


class Station(namedtuple('Station', 'name,code')):
    def get_code_for_search(self):
        if self.code == 'All Stations':
            return self.name.lower()  # ie 'Liverpool'
        else:
            return self.code.upper()  # ie 'LIV'


class Journey(namedtuple('Journey',
                         ('depart_station,arrive_station,'
                          'depart_time,arrive_time,changes,status'))):
    pass


def main(phrase):
    logging.basicConfig(level=logging.INFO)
    requests_cache.install_cache()
    parts = phrase.split(' to ', 1)
    if len(parts) != 2:
        print("Try eg 'liverpool to london euston'")
        sys.exit(2)

    depart, arrive = parts

    for journey in search_trains(depart, arrive,
                                 datetime.datetime(2014, 1, 25, 9, 0)):
        print(journey)


def get_station(station_name):
    """
    Return the single most likely station for this name.
    """
    return next(search_stations(station_name))  # TODO: don't just get the 1st


def search_stations(text):
    """
    Yields Station objects for the given station name provided.
    """

    stations_json = _http_get(_SEARCH_URL.format(search=text)).read()

    stations = []
    for result in json.loads(stations_json):
        code, name, _, _ = result
        stations.append(Station(name=name, code=code))
    return stations


def _http_get(url):
    response = requests.get(url)
    response.raise_for_status()
    return StringIO(response.content)


def search_trains(from_name, to_name, *args):
    """
    Get trains between the given station names.
    """
    return get_trains(
        get_station(from_name),
        get_station(to_name),
        *args)


def get_trains(from_station, to_station, when=None):
    if when is None:
        when = datetime.datetime.now()

    html = _http_get(
        requests.get(_TRAINS_URL.format(
            from_=from_station.get_code_for_search(),
            to=to_station.get_code_for_search(),
            DDMMYY=when.strftime('%d%m%y'),
            HHMM=when.strftime('%H%M')))
    ).read()

    root = lxml.html.fromstring(html)
    journeys = []
    for tr in root.cssselect('table#oft > tbody > tr.mtx'):
        journeys.append(_parse_station_from_tr(tr))
    return journeys


def _parse_station_from_tr(tr):

    try:
        depart_time = tr.cssselect('td.dep')[0].text_content().strip()
        arrive_time = tr.cssselect('td.arr')[0].text_content().strip()
        from_code = tr.cssselect('td.from abbr')[0].text_content().strip()
        to_code = tr.cssselect('td.to abbr')[0].text_content().strip()
        changes = tr.cssselect('td.chg')[0].text_content().strip()
        status = tr.cssselect('td.status')[0].text_content().strip()
    except IndexError:
        print(lxml.html.tostring(tr))
        raise

    return Journey(
        depart_station=from_code,
        arrive_station=to_code,
        depart_time=depart_time,
        arrive_time=arrive_time,
        changes=changes,
        status=status)


if __name__ == '__main__':
    main(' '.join(sys.argv[1:]))
