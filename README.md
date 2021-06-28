# Aillio RoasTime Data Tools

## Dump Local RoasTime Data to CSV

Download the script `dump-roasts.py` to your system, and make it
executable:

    chmod +x dump-roasts.py

Dump default roast fields to a CSV file:

    ./dump-roasts.py roasts.csv

Dump user-specified roast fields:

    ./dump-roasts.py -f date,time,ambient,humidity roasts.csv
