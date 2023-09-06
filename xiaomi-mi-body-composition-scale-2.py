# pip3 install requests
# pip3 install bleak
# pip3 install asyncio

import sys
import asyncio
import struct
import requests
import time
import platform

from bleak import BleakScanner
from datetime import datetime

CURRENT_SYSTEM: str = platform.system()
XIAOMI_SCALE_ADDRESS = "88:22:XX:XX:0E:7F" # Change to your device address

oldTimestamp = 0

def getValueFromServiceData(unpackData):
    global oldTimestamp

    # hexData = [hex(dt) for dt in unpackData]
    # print("hexData : ", hexData)

    # Get Data
    isStabilized = unpackData[1] & (1<<5)
    weight = (((unpackData[12] & 0xFF) << 8) | (unpackData[11] & 0xFF)) / 200.0
    deviceDateTime = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(int(((unpackData[3] & 0xFF) << 8) | unpackData[2]), int(unpackData[4]), int(unpackData[5]), int(unpackData[6]), int(unpackData[7]), int(unpackData[8]))

    # Convert to Local Time Zone
    currentTimestamp = time.time()
    localTimeZoneOffset = datetime.fromtimestamp(currentTimestamp) - datetime.utcfromtimestamp(currentTimestamp)
    currentDateTime = datetime.strptime(deviceDateTime, "%Y-%m-%d %H:%M:%S") + localTimeZoneOffset
    currentTimestamp = datetime.timestamp(currentDateTime)

    # Check isStabilized and currentTimestamp > 10 seconds
    if isStabilized and currentTimestamp - oldTimestamp > 10:
        oldTimestamp = currentTimestamp

        print("Date Time: "+str(currentDateTime.strftime("%Y-%m-%d %H:%M:%S"))+"\t\tWeight : "+str(weight))

async def findBluetoothDevice():
    devices = await BleakScanner.discover()

    for device in devices:
        if device.address == XIAOMI_SCALE_ADDRESS:
            if CURRENT_SYSTEM == "Windows":
                for detail in device.details:
                    if detail is not None:
                        for data in detail.advertisement.data_sections:
                            unpackData = [dt[0] for dt in struct.iter_unpack("<B", data.data)]
                            unpackData = unpackData[2:]

                            if data.data_type == 22 and len(unpackData) == 13:
                                getValueFromServiceData(unpackData)

            elif CURRENT_SYSTEM == "Linux":
                uuid = device.details.get("props").get("UUIDs")[0]
                data = device.details.get("props").get("ServiceData")[uuid]

                unpackData = [dt[0] for dt in struct.iter_unpack("<B", data)]

                if len(unpackData) == 13:
                    getValueFromServiceData(unpackData)

print("If you want to exit, you can press Ctrl + C.\n")

while True:
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(findBluetoothDevice())
    except KeyboardInterrupt:
        print("\nExit\n")
        sys.exit(0)
    except Exception as e:
        print("Exception Message:", str(e))
        time.sleep(1)