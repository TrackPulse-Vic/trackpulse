import os

from dotenv import load_dotenv
import requests

load_dotenv()

def getVehiclePositions(mode):
    headers = {"KeyID": os.getenv('TRANSPORT_VIC_API_KEY')}
    if mode == 'train':
        vline = "https://api.opendata.transport.vic.gov.au/opendata/public-transport/gtfs/realtime/v1/vline/vehicle-positions?format=json"
        metro = 'https://api.opendata.transport.vic.gov.au/opendata/public-transport/gtfs/realtime/v1/metro/vehicle-positions?format=json'
        vlineData = requests.get(vline, headers=headers)
        metroData = requests.get(metro, headers=headers)
        if vlineData.status_code != 200:
            print(f"HTTP {vlineData.status_code} when fetching GTFS data")
        if metroData.status_code != 200:
            print(f"HTTP {metroData.status_code} when fetching GTFS data")
        return({'vline': vlineData.json(), 'metro': metroData.json()})
    
    elif mode == 'tram':
        tram = 'https://api.opendata.transport.vic.gov.au/opendata/public-transport/gtfs/realtime/v1/tram/vehicle-positions?format=json'
        tramData = requests.get(tram, headers=headers)
        if tramData.status_code != 200:
            print(f"HTTP {tramData.status_code} when fetching GTFS data")
        return({'tram': tramData.json()})
    elif mode == 'bus':
        bus = 'https://api.opendata.transport.vic.gov.au/opendata/public-transport/gtfs/realtime/v1/bus/vehicle-positions?format=json'
        busData = requests.get(bus, headers=headers)
        if busData.status_code != 200:
            print(f"HTTP {busData.status_code} when fetching GTFS data")
        return({'bus': busData.json()})

        