import mock
from contextlib import contextmanager
from os.path import dirname, join as pjoin
from nose.tools import assert_equal

from uktrains import get_trains, Station

_DATA = pjoin(dirname(__file__), 'sample_data')


@contextmanager
def sample_data(filename):
    try:
        with open(pjoin(_DATA, filename), 'r') as f:
            yield f
    finally:
        pass


@mock.patch('uktrains.uktrains._http_get')
def test_split_table(mock_http_get):
    with sample_data('03_split_tables.html') as f:
        mock_http_get.return_value = f
        journeys = get_trains(Station('Bar', 'BAR'), Station('Foo', 'FOO'))
        assert_equal(None, journeys)
