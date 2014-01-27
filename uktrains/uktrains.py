#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals

import datetime
import json
import logging
import re
import sys

from collections import namedtuple
from cStringIO import StringIO

import requests
import requests_cache

import lxml.html

__all__ = ['search_trains', 'get_trains', 'get_station', 'search_stations',
           'Journey', 'Station']


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
                          'depart_time,arrive_time,platform,changes,status'))):
    pass


def main(phrase):
    logging.basicConfig(level=logging.DEBUG)
    requests_cache.install_cache()
    parts = phrase.split(' to ', 1)
    if len(parts) != 2:
        print("Try eg 'liverpool to london euston'")
        sys.exit(2)

    depart, arrive = parts

    for journey in search_trains(depart, arrive):
        print(journey)


def get_station(station_name):
    """
    Return the single most likely station for this name.
    """
    station = search_stations(station_name)[0]  # TODO: don't just get 1st
    logging.debug("'{}' => '{}'".format(station_name, station))
    return station


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
    logging.debug(url)
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
        _TRAINS_URL.format(
            from_=from_station.get_code_for_search(),
            to=to_station.get_code_for_search(),
            DDMMYY=when.strftime('%d%m%y'),
            HHMM=when.strftime('%H%M'))
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
        from_name, from_code = _parse_name_code(
            tr.cssselect('td.from')[0].text_content())
        to_name, to_code = _parse_name_code(
            tr.cssselect('td.to')[0].text_content())

        changes = tr.cssselect('td.chg')[0].text_content().strip()
        status = tr.cssselect('td.status')[0].text_content().strip()
        try:
            platform_span = tr.cssselect('td.from > span.ctf-plat')[0]
            from_platform = _parse_platform(platform_span.text_content())
        except IndexError:
            from_platform = None

    except IndexError:
        print(lxml.html.tostring(tr))
        raise

    return Journey(
        depart_station=Station(from_name, from_code),
        arrive_station=Station(to_name, to_code),
        depart_time=depart_time,
        arrive_time=arrive_time,
        platform=from_platform,
        changes=changes,
        status=status)


def _parse_name_code(station):
    """
    >>> _parse_name_code(' \n West Kirby  [WKI]\n \t \n')
    ('West Kirby', 'WKI')
    """
    match = re.match('[ \t\n]*(?P<name>.+) +\[(?P<code>[A-Z]{3})\][ \t\n]*',
                     station)
    if match:
        return match.group('name').strip(), match.group('code').strip()
    logging.warn("Failed to parse: '{}'".format(station))
    return None


def _parse_platform(span_content):
    """
    >>> _parse_platform('  Platform\\n\\t\\t\\t\\t8  ')
    8
    """
    match = re.search(r'(\d+)', span_content)
    if match:
        return int(match.group(0))
    logging.warn("Failed to parse: '{}'".format(span_content))
    return None

if __name__ == '__main__':
    main(' '.join(sys.argv[1:]))
