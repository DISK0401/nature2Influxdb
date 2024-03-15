import binascii
from bluepy.btle import Scanner, DefaultDelegate
from influxdb_client import InfluxDBClient
from datetime import datetime
from config import IS_DEBUG,SCANNING_TIME_SECAND,SWITCH_BOT_MACDDR_LIST,INFLUXDB_URL,INFLUXDB_ORG,INFLUXDB_TOKEN,INFLUXDB_BUCKET

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)

def get_old_meter_device(device):
    battery = -1
    temperature = -1
    humidity = -0.000
    isEncrypted = -1
    isDualStateMode = -1
    isStatusOff = -1
    isTemperatureHighAlert = -1
    isTemperatureLowAlert = -1
    isHumidityHighAlert = -1
    isHumidityLowAlert = -1
    isTemperatureUnitF = -1

    for (adtype, desc, value) in device.getScanData():
        if (adtype != 22): continue
        servicedata = binascii.unhexlify(value[4:])

        # バッテリー残量
        battery = servicedata[2] & 0b01111111
        # 気温
        temperature = (servicedata[3] & 0b00001111) / 10 + (servicedata[4] & 0b01111111)
        isTemperatureAboveFreezing = servicedata[4] & 0b10000000
        if not isTemperatureAboveFreezing:
            ## isTemperatureAboveFreezingがFalseのばあいは、氷点下であるがデータ上は+で来るので、マイナス変換する
            temperature = -temperature
        # 湿度
        humidity = (servicedata[5] & 0b01111111)*0.01
        # その他
        isEncrypted            = ( servicedata[0] & 0b10000000 ) >> 7
        isDualStateMode        = ( servicedata[1] & 0b10000000 ) >> 7
        isStatusOff            = ( servicedata[1] & 0b01000000 ) >> 6
        isTemperatureHighAlert = ( servicedata[3] & 0b10000000 ) >> 7
        isTemperatureLowAlert  = ( servicedata[3] & 0b01000000 ) >> 6
        isHumidityHighAlert    = ( servicedata[3] & 0b00100000 ) >> 5
        isHumidityLowAlert     = ( servicedata[3] & 0b00010000 ) >> 4
        isTemperatureUnitF     = ( servicedata[5] & 0b10000000 ) >> 7

    return battery,temperature,humidity


def get_new_meter_device(device):
    battery = -1
    temperature = -1
    humidity = -0.00
    isEncrypted = -1
    isDualStateMode = -1
    isStatusOff = -1
    isTemperatureHighAlert = -1
    isTemperatureLowAlert = -1
    isHumidityHighAlert = -1
    isHumidityLowAlert = -1
    isTemperatureUnitF = -1

    for (adtype, desc, value) in device.getScanData():
        if(adtype == 22):
            servicedata = binascii.unhexlify(value[4:])
            battery = servicedata[2] & 0b01111111
            return battery,temperature,humidity
        elif(adtype == 255):
            madata = binascii.unhexlify(value[16:])
            humidity = (madata[4] & 0b01111111)*0.01
            temperature = (madata[2] & 0b00001111) / 10 + (madata[3] & 0b01111111)
            isTemperatureAboveFreezing = madata[3] & 0b10000000
            print("isTemperatureAboveFreezing:",isTemperatureAboveFreezing)
            if not isTemperatureAboveFreezing:
                ## isTemperatureAboveFreezingがFalseのばあいは、氷点下であるがデータ上は+で来るので、マイナス変換する
                temperature = -temperature
            continue
        else : continue

    return battery,temperature,humidity


def get_plugmini_device(device):
    is_state_on = False
    wifi_rssi = 0
    is_overload = False
    wat = 0

    for (adtype, desc, value) in device.getScanData():
        if (adtype != 255): continue

        manufacturer = binascii.unhexlify(value)
        is_state_on = ( manufacturer[9] & 0b10000000 ) >> 7
        wifi_rssi = manufacturer[11]
        is_overload = ( manufacturer[12] & 0b10000000 ) >> 7
        wat = (((manufacturer[12] << 8 ) + manufacturer[13]) & 0x7fff) / 10
    return is_state_on,wifi_rssi,is_overload,wat


if __name__ == '__main__':
    scanner = Scanner()
    while True:
        influx_body = []
        if IS_DEBUG: print("scan start :",datetime.now())
        devices = scanner.scan(SCANNING_TIME_SECAND)
        if IS_DEBUG: print("scan end   :",datetime.now())
        for device in devices:
            if (device.addr).upper() not in SWITCH_BOT_MACDDR_LIST: continue
            if IS_DEBUG: print(SWITCH_BOT_MACDDR_LIST[(device.addr).upper()]['name'])

            if SWITCH_BOT_MACDDR_LIST[(device.addr).upper()]['type'] in ['meter_new','meter_old']:
                battery = -1
                temperature = -1
                humidity = -1

                if SWITCH_BOT_MACDDR_LIST[(device.addr).upper()]['type'] == 'meter_old':
                    battery,temperature,humidity = get_old_meter_device(device)
                elif SWITCH_BOT_MACDDR_LIST[(device.addr).upper()]['type'] == 'meter_new':
                    battery,temperature,humidity = get_new_meter_device(device)

                body = {
                    "measurement":"switchbot_smartmeter",
                    "time":datetime.utcnow(),
                    "tags": {
                        "mac_address": (device.addr).upper(),
                        "device_name": SWITCH_BOT_MACDDR_LIST[(device.addr).upper()]['name'],
                    },
                    "fields": {
                        "temperature": temperature,
                        "humidity": humidity,
                        "battery": battery,
                    }
                }
                influx_body.append(body)

            elif SWITCH_BOT_MACDDR_LIST[(device.addr).upper()]['type'] == 'plugmini':
                is_state_on = False
                wifi_rssi = 0
                is_overload = False
                wat = -1

                is_state_on,wifi_rssi,is_overload,power = get_plugmini_device(device)
                wat = power * 100

                body = {
                    "measurement":"switchbot_plugmini",
                    "time":datetime.utcnow(),
                    "tags": {
                        "mac_address": (device.addr).upper(),
                        "device_name": SWITCH_BOT_MACDDR_LIST[(device.addr).upper()]['name'],
                    },
                    "fields": {
                        "is_state_on": is_state_on,
                        "wifi_rssi": wifi_rssi,
                        "is_overload": is_overload,
                        "wat": wat,
                    }
                }
                influx_body.append(body)
            else :
                print("想定外のデバイス")

        if IS_DEBUG: print("actscan end:",datetime.now())
        if influx_body:
            if IS_DEBUG:print(influx_body)
            write_api = client.write_api()
            write_api.write(bucket=INFLUXDB_BUCKET,org=INFLUXDB_ORG,record=influx_body)
        if IS_DEBUG: print("write end  :",datetime.now())
