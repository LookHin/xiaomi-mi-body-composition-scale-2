# xiaomi-mi-body-composition-scale-2

![Image](https://www.onlyme.dev/github/xiaomi-mi-body-composition-scale-2/1.png?v=3)

### 0. Install library

```
# apt-get update
# apt-get install -y bluez* pkg-config libbluetooth-dev libglib2.0-dev
# apt-get install -y libboost-thread-dev libboost-python-dev python3-capstone

# pip3 install requests
# pip3 install bleak
# pip3 install asyncio
```

### 1. discover.py

```
# nano discover.py
```

```python
import sys
import asyncio
import time

from typing import Sequence
from bleak import BleakScanner

async def findBluetoothDevice():
    devices: Sequence[BLEDevice] = await BleakScanner.discover(timeout=1)

    print("** Date Time: ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "**\n")

    for device in devices:
        print(device)

    print("--------------------------------------------------\n")

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
```

### 2. Find device address

```
# python3 discover.py
```

![Image](https://www.onlyme.dev/github/xiaomi-mi-body-composition-scale-2/2.png)


### 3. xiaomi-mi-body-composition-scale-2.py

```
# nano xiaomi-mi-body-composition-scale-2.py
```

```python
import sys
import asyncio
import struct
import requests
import time
import platform

from typing import Sequence
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
    devices: Sequence[BLEDevice] = await BleakScanner.discover(timeout=1)

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
```

### 4. Run

```
# python3 xiaomi-mi-body-composition-scale-2.py
```

![Image](https://www.onlyme.dev/github/xiaomi-mi-body-composition-scale-2/3.png)


## About Us
Name : Khwanchai Kaewyos (LookHin)

Email : khwanchai@gmail.com

## Website
[https://www.onlyme.dev](https://www.onlyme.dev)

[https://www.facebook.com/LookHin](https://www.facebook.com/LookHin)


## License

MIT License

Copyright (c) 2023 Khwanchai Kaewyos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
