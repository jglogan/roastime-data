#! /usr/bin/env python3

import argparse
import csv
import datetime
import json
import os
import sys

roast_fields = [
    'dateTime',
    'uid',
    'roastNumber',
    'roastName',
    'beanId',
    'rating',

    'serialNumber',
    'firmware',
    'hardware',

    {'fields': ['ambient', 'ambientTemp'], 'mapped_field': 'ambient', 'type': float},
    {'fields': ['humidity', 'roomHumidity'], 'mapped_field': 'humidity', 'type': float},
    {'fields': ['weightGreen'], 'mapped_field': 'weightGreen', 'type': float},
    {'fields': ['weightRoasted'], 'mapped_field': 'weightRoasted', 'type': float},

    'preheatTemperature',
    'beanChargeTemperature',
    'beanDropTemperature',
    'drumChargeTemperature',
    'drumDropTemperature',
    
    'totalRoastTime',
    'sampleRate',
    'roastStartIndex',
    'indexYellowingStart',
    'indexFirstCrackStart',
    'indexFirstCrackEnd',
    'indexSecondCrackStart',
    'indexSecondCrackEnd',
    'roastEndIndex',
]

def set_roast_column(roast_json, roast_columns, roast_field):
    if 'fields' in roast_field:
        for field in roast_field['fields']:
            if field in roast_json:
                roast_columns[roast_field['mapped_field']] = roast_field['type'](roast_json[field])
                return

        roast_columns[roast_field['mapped_field']] = ''
        return
    
    roast_columns[roast_field] = roast_json.get(roast_field, None)

def load_roast(roast_pathname):
    sys.stderr.write(f'loading {roast_pathname}\n')
    with open(roast_pathname, 'r', encoding='utf-8') as roast_file:
        roast_json = json.load(roast_file)
        roast = {}
        for roast_field in roast_fields:
            set_roast_column(roast_json, roast, roast_field)

        roast['date'] = datetime.datetime.fromtimestamp(roast['dateTime'] / 1000).strftime('%Y-%m-%d')
        roast['time'] = datetime.datetime.fromtimestamp(roast['dateTime'] / 1000).strftime('%H:%M:%S')
        return roast

def load_roasts(roast_dirname):
    roasts = []
    for roast_filename in os.listdir(roast_dirname):
        roast = load_roast(os.path.join(roast_dirname, roast_filename))
        roasts.append(roast)
    
    return roasts

def get_fields():
    return [f if 'mapped_field' not in f else f['mapped_field'] for f in roast_fields]

def main():
    default_fields = ['date', 'time', 'beanId', 'weightGreen']
    valid_fields = ', '.join(get_fields())
    epilog = f'Valid field names are: {valid_fields}'
    parser = argparse.ArgumentParser(description='Convert RoasTime roast data to CSV.', epilog=epilog)
    parser.add_argument('-f', '--fields', help=f'comma-separated list of fields (default is {",".join(default_fields)})')
    parser.add_argument('output_file', metavar='PATH', help='CSV file name')
    roast_path = os.path.join(os.path.expanduser("~"), "Library/Application Support/roast-time/roasts")
    args = parser.parse_args()
    roasts = load_roasts(roast_path)
    fields = default_fields if args.fields is None else args.fields.split(",")
    with open(args.output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(fields)
        for roast in roasts:
            writer.writerow([roast[field] for field in fields])

if __name__ == "__main__":
    rv = main()
    sys.exit(rv)
