# Aillio RoasTime Data Tools

## Dump Local RoasTime Data to CSV

Download the script `dump-roasts.py` to your system, and make it
executable:

    chmod +x dump-roasts.py

Dump default roast fields to a CSV file:

    ./dump-roasts.py roasts.csv

Dump user-specified roast fields:

    ./dump-roasts.py -f date,time,ambient,humidity roasts.csv

Get help:

```
./dump-roasts.py -h
usage: dump-roasts.py [-h] [-f FIELDS] PATH

Convert RoasTime roast data to CSV.

positional arguments:
  PATH                  CSV file name

optional arguments:
  -h, --help            show this help message and exit
  -f FIELDS, --fields FIELDS
                        comma-separated list of fields (default is
                        date,time,beanId,weightGreen)

Valid field names are: dateTime, uid, roastNumber, roastName, beanId, rating,
serialNumber, firmware, hardware, ambient, humidity, weightGreen,
weightRoasted, preheatTemperature, beanChargeTemperature, beanDropTemperature,
drumChargeTemperature, drumDropTemperature, totalRoastTime, sampleRate,
roastStartIndex, indexYellowingStart, indexFirstCrackStart,
indexFirstCrackEnd, indexSecondCrackStart, indexSecondCrackEnd, roastEndIndex
```