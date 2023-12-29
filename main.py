import os
import requests
from pprint import pprint
from typing import Optional


## 環境変数ロード
from dotenv import load_dotenv
load_dotenv(override=True)
NATURE_REMO_TOKEN = os.getenv('NATURE_REMO_TOKEN')

## 固定値
NATURE_API_ENDPOINT = 'https://api.nature.global'


def get_nature_sensor() -> Optional[dict]:
    """
    Nature Remo APIを用いての温度、湿度、照度計データを取得する
    """
    url = NATURE_API_ENDPOINT+'/1/devices'
    header = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer {}'.format(NATURE_REMO_TOKEN),
        }

    result = requests.get(url, headers=header)

    if result.status_code == 200:
        data = result.json()
        # pprint(data)
        nature_data = {
            "temperature":data[1]["newest_events"]["te"]["val"],  ## 温度
            "humidity":data[1]["newest_events"]["hu"]["val"],     ## 湿度
            "illuminance":data[1]["newest_events"]["il"]["val"],  ## 照度
        }
        print(nature_data)
        return nature_data
    else:
        return None



def get_nature_home_power() -> Optional[list[dict]]:
    """
    Nature Remo APIを用いての家電の電力を取得する
    """
    url = NATURE_API_ENDPOINT+'/1/appliances'
    header = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer {}'.format(NATURE_REMO_TOKEN),
        }

    result = requests.get(url, headers=header)

    if result.status_code == 200:
        data = result.json()
        # pprint(data)
        nature_data = []
        for i in data:
            tmp_result = {}
            tmp_result.update(
                name=i["device"]["name"],
                date=i["smart_meter"]["echonetlite_properties"][0]["updated_at"],
            )
            for j in i["smart_meter"]["echonetlite_properties"]:
                tmp_result.update({j["name"]: j["val"]})
            nature_data.append(tmp_result)
        pprint(nature_data)
        return nature_data
    else:
        return None


if __name__ == "__main__":
    remo_sensor_data = get_nature_sensor()

    # 積算電力量計測値(正方向)]：normal_direction_cumulative_electric_energy
    # 瞬時電力計測値(W)：measured_instantaneous
    remot_energy_data = get_nature_home_power()
