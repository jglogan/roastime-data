# Aillio RoasTime Data Tools

## Dump Local RoasTime Data to CSV

Download the script `dump_roasts.py` to your system, and make it
executable:

    chmod +x dump_roasts.py

Dump default roast fields to a CSV file:

    ./dump_roasts.py roasts.csv

Dump user-specified roast fields:

    ./dump_roasts.py -f date,time,ambient,humidity roasts.csv

Get help:

    ./dump_roasts.py -h

## Jupyter Notebook

    ./install-env coffee-env
    . coffee-env/bin/activate
    jupyter lab &
