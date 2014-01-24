# Installation

```
git clone git@github.com:paulfurley/python-uk-trains.git
cd python-uk-trains
virtualenv venv
pip install -r requirements.txt
```

# Usage

```
from uktrains import search_trains 

for journey in search_trains('london euston', 'lime street'):
    print(journey)

for journey in search_trains('kettering', 'wellingborough',
                             datetime.datetime(2013, 4, 1, 8, 30)):
    print(journey)
```

```
import uktrains

from_station = uktrains.get_station('liverpool')
to_station = uktrains.get_station('euston')

uktrains.get_trains(from_station, to_station)
```
