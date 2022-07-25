#! /usr/bin/env python3

import argparse
import csv
import datetime
import json
import os
import sys

#
#  TODO:
#  - Windows compatibility
#  - Linux compatibility
#  - 
#

#
#  Roastime control codes.
#
codes_by_control = {
    'power': 0,
    'fan': 1,
    'drum': 2,
}


#
#  Functions for computing event fields.
#
def make_get_sample(index_field):
    '''
    Get a sampled field at an index.
    '''

    def get_sample(roast_json, source_field):
        try:
            index = min(roast_json[index_field], len(roast_json[source_field]) - 1)
            return roast_json[source_field][index]
        except:
            raise
            sys.stderr.write(f'failed to get sample {source_field} using index field {index_field}\n')
            return None

    return get_sample


def make_get_control(control):
    '''
    Get a control value at an index.
    '''

    control_code = codes_by_control[control]
    def get_control(roast_json, source_field):
        current_value = None
        index_value = roast_json[source_field]

        try:
            action_times = roast_json['actions']['actionTimeList']
            for action in action_times:
                if action['ctrlType'] != control_code:
                    continue

                if action['index'] > index_value:
                    return current_value

                current_value = action['value']

            if current_value is not None:
                return current_value

            sys.stderr.write(f'index value {index_value} not within control range\n')
            return None
        except:
            sys.stderr.write(f'failed to get control {control} using index field {source_field}\n')
            raise
            return None

    return get_control


def make_conversion(conversion_type):
    '''
    Coerce a roast field to a specific type.
    '''

    def conversion(roast_json, source_field):
        return conversion_type(roast_json[source_field])

    return conversion


def seconds_from_index(roast_json, source_field):
    '''
    Convert an index field to a time value in seconds.
    '''

    try:
        return roast_json[source_field] / roast_json['sampleRate']
    except:
        sys.stderr.write(f'failed to get convert {source_field} to time value\n')
        return None


#
#  Set up basic fields.
#
roast_fields = [
    {'fields': ['dateTime'], 'mapped_field': ('date', lambda roast_json, source_field: datetime.datetime.fromtimestamp(roast_json[source_field] / 1000).strftime('%Y-%m-%d')) },
    {'fields': ['dateTime'], 'mapped_field': ('time', lambda roast_json, source_field: datetime.datetime.fromtimestamp(roast_json[source_field] / 1000).strftime('%H:%M:%S')) },

    'dateTime',
    'uid',
    'roastNumber',
    'roastName',
    'beanId',
    'rating',

    'serialNumber',
    'firmware',
    'hardware',

    {'fields': ['ambient', 'ambientTemp'], 'mapped_field': ('ambient', make_conversion(float))},
    {'fields': ['humidity', 'roomHumidity'], 'mapped_field': ('humidity', make_conversion(float))},
    {'fields': ['weightGreen'], 'mapped_field': ('weightGreen', make_conversion(float))},
    {'fields': ['weightRoasted'], 'mapped_field': ('weightRoasted', make_conversion(float))},

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

#
#  Work around event naming inconsistencies.
#
events = [
    ('roastStart', True),
    ('roastEnd', True),
    ('YellowingStart', False),
    ('FirstCrackStart', False),
    ('FirstCrackEnd', False),
    ('SecondCrackStart', False),
    ('SecondCrackEnd', False),
]


def get_event_field(event_name, prepend, field):
    return f'{event_name}{field.capitalize()}' if prepend else f'{field}{event_name}'


#
#  Add computed event fields.
#
roast_sample_fields = [
    'beanDerivative',
    'beanTemperature',
    'drumTemperature',
]

for event_name, prepend in events:
    #
    #  Fields for event times.
    #
    source_field = get_event_field(event_name, prepend, 'index')
    destination_field = get_event_field(event_name, prepend, 'seconds')
    roast_fields.append({'fields': [source_field], 'mapped_field': (destination_field, seconds_from_index) })

    #
    #  Fields for event control values.
    #
    for control in codes_by_control.keys():
        source_field = get_event_field(event_name, prepend, 'index')
        destination_field = get_event_field(event_name, prepend, control)
        roast_fields.append({'fields': [source_field], 'mapped_field': (destination_field, make_get_control(control)) })

    #
    #  Fields for event sample values.
    #
    for roast_sample_field in roast_sample_fields:
        source_field = get_event_field(event_name, prepend, 'index')
        destination_field = get_event_field(event_name, prepend, roast_sample_field)
        roast_fields.append({'fields': [roast_sample_field], 'mapped_field': (destination_field, make_get_sample(source_field)) })


def set_roast_column(roast_json, roast_columns, roast_field):
    if 'mapped_field' in roast_field:
        mapped_field, mapping_fn = roast_field['mapped_field']
        if 'fields' in roast_field:
            #
            #  Map a source field (optionally involving arbitrary
            #  data as specified in the mapping function).
            #
            for field in roast_field['fields']:
                if field in roast_json:
                    roast_columns[mapped_field] = mapping_fn(roast_json, field)
                    return
        else:
            #
            #  Compute a value from arbitrary roast fields.
            #
            roast_columns[mapped_field] = mapping_fn(roast_json, None)

        sys.stderr.write(f'failed to retrieve data for {mapped_field}\n')
        roast_columns[mapped_field] = None
        return
    
    roast_columns[roast_field] = roast_json.get(roast_field, None)


def create_roast(roast_json):
    roast = {}
    for roast_field in roast_fields:
        set_roast_column(roast_json, roast, roast_field)

    return roast


def load_roasts(roast_dirname):
    roasts = []
    for roast_filename in os.listdir(roast_dirname):
        roast_pathname = os.path.join(roast_dirname, roast_filename)
        sys.stderr.write(f'loading {roast_pathname}\n')
        with open(roast_pathname, 'r', encoding='utf-8') as roast_file:
            roast_json = json.load(roast_file)
            roast = create_roast(roast_json)
            roasts.append(roast)
    
    return roasts


def get_fields():
    return [f if 'mapped_field' not in f else f['mapped_field'][0] for f in roast_fields]


def write_roasts(csv_file, roasts, fields):
        writer = csv.writer(csv_file)
        writer.writerow(fields)
        for roast in roasts:
            writer.writerow([roast[field] for field in fields])


def main():
    default_fields = ['date', 'time', 'beanId', 'weightGreen']
    valid_fields = ', '.join(get_fields())
    epilog = f'Valid field names are: {valid_fields}'

    parser = argparse.ArgumentParser(description='Convert RoasTime roast data to CSV.', epilog=epilog)
    parser.add_argument('-f', '--fields', help=f'comma-separated list of fields (default is {",".join(default_fields)})')
    parser.add_argument('output_file', metavar='PATH', help='CSV file name (default is stdout)', nargs='?')

    roast_path = os.path.join(os.path.expanduser("~"), "Library/Application Support/roast-time/roasts")
    args = parser.parse_args()
    roasts = load_roasts(roast_path)
    fields = default_fields if args.fields is None else args.fields.split(",")
    file_id = sys.stdout.fileno() if args.output_file is None else args.output_file
    with open(file_id, 'w', newline='') as csv_file:
        write_roasts(csv_file, roasts, fields)


if __name__ == "__main__":
    rv = main()
    sys.exit(rv)
