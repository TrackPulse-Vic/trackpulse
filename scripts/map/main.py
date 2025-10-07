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
    return vlineData.json(), metroData.json()

print(getVehiclePositions('train'))
