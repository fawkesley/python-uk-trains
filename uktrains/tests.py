import mock
from contextlib import contextmanager
from os.path import dirname, join as pjoin
from nose.tools import assert_equal

from cStringIO import StringIO

from uktrains import get_trains, Station, search_stations

_DATA = pjoin(dirname(__file__), 'sample_data')


@contextmanager
def sample_data(filename):
    try:
        with open(pjoin(_DATA, filename), 'r') as f:
            yield f
    finally:
        pass


@mock.patch('uktrains.uktrains._http_get')
def test_decode_search_results(mock_http_get):
    with sample_data('01_station_search_results.json') as f:
        mock_http_get.return_value =f
        stations = search_stations('LIV')
        assert_equal(9, len(stations))


@mock.patch('uktrains.uktrains._http_get')
def test_split_table(mock_http_get):
    with sample_data('03_split_tables.html') as f:
        mock_http_get.return_value = f
        journeys = get_trains(Station('Bar', 'BAR'), Station('Foo', 'FOO'))
        assert_equal(None, journeys)


@mock.patch('uktrains.uktrains._http_get')
def test_search_stations_returns_just_rail_stationsn(mock_http_get):
    mock_http_get.return_value = StringIO("[]")
    search_stations('LIV')
    expected_url = ('http://ojp.nationalrail.co.uk/find/stations/LIV')
    assert_equal(
        mock.call(expected_url),
        mock_http_get.call_args_list[0])
