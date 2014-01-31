import mock
from contextlib import contextmanager
from os.path import dirname, join as pjoin
from nose.tools import assert_equal

from cStringIO import StringIO

from uktrains import get_trains, Journey, Station, search_stations

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
def _test_split_table(mock_http_get):
    with sample_data('03_split_tables.html') as f:
        mock_http_get.return_value = f
        journeys = get_trains(Station('Bar', 'BAR'), Station('Foo', 'FOO'))
        assert_equal(None, journeys)


@mock.patch('uktrains.uktrains._http_get')
def test_parse_journeys(mock_http_get):
    with sample_data('02_search_results.html') as f:
        mock_http_get.return_value = f
        journeys = get_trains(Station('Bar', 'BAR'), Station('Foo', 'FOO'))
        assert_equal(5, len(journeys))
        assert_equal(
            Journey(
                depart_station=Station(name='Liverpool Lime Street',
                                       code='LIV'),
                arrive_station=Station(name='London Euston',
                                       code='EUS'),
                depart_time='19:48',
                arrive_time='22:09',
                platform=None,
                changes=0,
                status='on time'),
            journeys[0])

        assert_equal(
            Journey(
                depart_station=Station(name='Liverpool Lime Street',
                                       code='LIV'),
                arrive_station=Station(name='London Euston',
                                       code='EUS'),
                depart_time='23:43',
                arrive_time='07:38',
                platform=None,
                changes=2,
                status=''),
            journeys[4])


@mock.patch('uktrains.uktrains._http_get')
def test_newlines_removed_from_status(mock_http_get):
    with sample_data('05_journey_split_status.html') as f:
        mock_http_get.return_value = f
        journeys = get_trains(Station('Bar', 'BAR'), Station('Foo', 'FOO'))
        assert_equal('disrupted', journeys[0].status)


@mock.patch('uktrains.uktrains._http_get')
def test_search_stations_returns_just_rail_stationsn(mock_http_get):
    mock_http_get.return_value = StringIO("[]")
    search_stations('LIV')
    expected_url = ('http://ojp.nationalrail.co.uk/find/stations/LIV')
    assert_equal(
        mock.call(expected_url),
        mock_http_get.call_args_list[0])
