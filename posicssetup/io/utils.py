import os
import json
import datetime


def get_basename(config_file: str):

    with open(config_file, 'r') as f:
        config = json.load(f)['writer']

    format_data = "%Y%m%d-%H:%M:%S"
    basename = config['basename'].format(date=datetime.datetime.strftime(datetime.datetime.now(), format_data))
    format_data = "%Y%m%d"
    directory = config['directory'].format(date=datetime.datetime.strftime(datetime.datetime.now(), format_data))

    if not os.path.exists(directory):

        os.mkdir(directory)

    basename = os.path.join(directory, basename)

    return basename
