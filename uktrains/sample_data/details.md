# Search for a station

## Plain old train stations

``http://ojp.nationalrail.co.uk/find/stations/<search_term>``

Response looks like 01_station_search_results.json

 
 Response Array Keys for ojpServiceURL

  - 0 = CRS Code [XYZ]
  - 1 = Station Name 
  - 2 = Classification
    * 0 = Normal station
    * 1 = Group Station  (ie Manchester All Stations)
    * 2 = London station
    * 3 = Non OJP Station

## Include Tube and DLR stations
  
``http://ojp.nationalrail.co.uk/find/stationsDLRLU/<search_term>``

  Response Array Keys for dlrServiceURL
  - 0 = CRS
  - 1 = Name
  - 2 = Classification
    - 0 = Normal station including London
    - 1 = Group staition 
    - 2 = London Station
    - 3 = Non OJP station
    - 4 = Station is exclusive to DLR
    - 5 = Station is exclusive London Undergroud
    - 6 = Station is both DLR and LU and not NR
  - 3 = Enabled (boolean) (OJP can plan this route)


#  Query a train

http://ojp.nationalrail.co.uk/service/timesandfares/LIV/EUS/today/1900/dep?excludeslowertrains
