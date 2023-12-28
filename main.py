import os
import requests
from pprint import pprint


from dotenv import load_dotenv
load_dotenv(override=True)
NATURE_REMO_TOKEN = os.getenv('NATURE_REMO_TOKEN')

NATURE_API_ENDPOINT = 'https://api.nature.global'

def get_nature_sensor():
    url = NATURE_API_ENDPOINT+'/1/devices'
    header = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer {}'.format(NATURE_REMO_TOKEN),
        }

    sensorInformation = requests.get(url, headers=header)

    if sensorInformation.status_code == 200:
        pprint(sensorInformation.json())
    else:
        pass


if __name__ == "__main__":
    get_nature_sensor()