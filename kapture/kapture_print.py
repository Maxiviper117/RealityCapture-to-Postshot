
"""
Script to print statistics about kapture data.
"""

import argparse
import logging
import sys
import contextlib
import os.path as path
from typing import Optional, Tuple
from datetime import datetime
import time

import path_to_kapture  # noqa: F401
import kapture
import kapture.utils.logging
import kapture.io.csv

logger = logging.getLogger('kapture_print')

# Consider as valid timestamps only if between these two dates
LOWER_RECORD_DATE_TIMESTAMP = time.mktime(datetime(year=1980, month=1, day=1, hour=0, minute=0, second=0).timetuple())
UPPER_RECORD_DATE_TIMESTAMP = time.mktime(datetime(year=2100, month=1, day=1, hour=0, minute=0, second=0).timetuple())


@contextlib.contextmanager
def open_or_stdout(filename=None):
    """
    Get the output to print into
    """
    # from https://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
    if filename and filename != '-':
        fh = open(filename, 'w')
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


def print_key_value(key, value, file, show_none=False) -> None:
    """
    Prints a key and its value
    """
    if value is not None or show_none:
        print(f'{key:25}: {value}', file=file)


def print_title(title, file) -> None:
    """
    Prints the title
    """
    print(f'=== {title:^25} ===', file=file)


def print_sensors(kapture_data, output_stream, show_detail, show_all) -> None:
    """
    Prints the sensors (only) to the output stream
    """
    if not show_detail:
        print_key_value('nb sensors', len(kapture_data.sensors), file=output_stream, show_none=show_all)
    else:
        print_title('sensors', file=output_stream)
        cam_ids = [s_id for s_id, sensor in kapture_data.sensors.items()
                   if sensor.sensor_type in kapture.ALL_CAMERA_SENSOR_TYPES]
        print_key_value(' ├─ nb cameras', len(cam_ids), file=output_stream, show_none=show_all)
        lidar_ids = [s_id for s_id, sensor in kapture_data.sensors.items()
                     if sensor.sensor_type == kapture.SensorType.lidar.name]
        print_key_value(' ├─ nb lidar', len(lidar_ids), file=output_stream, show_none=show_all)
        wifi_ids = [s_id for s_id, sensor in kapture_data.sensors.items()
                    if sensor.sensor_type == kapture.SensorType.wifi.name]
        print_key_value(' ├─ nb wifi', len(wifi_ids), file=output_stream, show_none=show_all)
        bluetooth_ids = [s_id for s_id, sensor in kapture_data.sensors.items()
                         if sensor.sensor_type == kapture.SensorType.bluetooth.name]
        print_key_value(' ├─ nb bluetooth', len(bluetooth_ids), file=output_stream, show_none=show_all)
        gnss_ids = [s_id for s_id, sensor in kapture_data.sensors.items()
                    if sensor.sensor_type == kapture.SensorType.gnss.name]
        print_key_value(' ├─ nb gnss', len(gnss_ids), file=output_stream, show_none=show_all)
        accelerometer_ids = [s_id for s_id, sensor in kapture_data.sensors.items()
                             if sensor.sensor_type == kapture.SensorType.accelerometer.name]
        print_key_value(' ├─ nb accelerometer', len(accelerometer_ids), file=output_stream, show_none=show_all)
        gyroscope_ids = [s_id for s_id, sensor in kapture_data.sensors.items()
                         if sensor.sensor_type == kapture.SensorType.gyroscope.name]
        print_key_value(' ├─ nb gyroscope', len(gyroscope_ids), file=output_stream, show_none=show_all)
        magnetic_ids = [s_id for s_id, sensor in kapture_data.sensors.items()
                        if sensor.sensor_type == kapture.SensorType.magnetic.name]
        print_key_value(' ├─ nb magnetic', len(magnetic_ids), file=output_stream, show_none=show_all)
        print_key_value(' └─ nb sensors total', len(kapture_data.sensors), file=output_stream, show_none=show_all)


def print_rigs(kapture_data, output_stream, show_detail, show_all) -> None:
    """
    Prints the rigs to the output stream
    """
    nb_rigs = len(kapture_data.rigs) if kapture_data.rigs is not None else None
    if not show_detail:
        print_key_value('nb rigs', nb_rigs, file=output_stream, show_none=show_all)
    else:
        print_title('rigs', file=output_stream)
        if kapture_data.rigs is not None:
            for rig_id, rig in kapture_data.rigs.items():
                s_ids = [s_id for s_id in kapture_data.rigs[rig_id]]
                print_key_value(' ├─ rig', rig_id, file=output_stream, show_none=show_all)
                for sensor_id in s_ids:
                    sensor_type = 'unknown'
                    if sensor_id in kapture_data.sensors:
                        sensor_type = kapture_data.sensors[sensor_id].sensor_type
                    if sensor_id in kapture_data.rigs:
                        sensor_type = 'rig'
                    print_key_value(f' │   ├─ {sensor_type}', sensor_id, file=output_stream, show_none=show_all)
                print_key_value(' │   └─ nb sensors total', len(s_ids), file=output_stream, show_none=show_all)
        print_key_value(' └─ nb rigs total', nb_rigs, file=output_stream, show_none=show_all)


FACTOR_TO_SECONDS = {
    'second': 1.0,
    'millisecond': 1.e-3,
    'microsecond': 1.e-6,
    'nanoseconds': 1.e-9
}


def guess_timestamp_posix_unit(timestamp: int) -> Optional[str]:
    """
    Guess the unit of a timestamp based on its value.

    :param timestamp: the timestamp value
    :return: 'posix' or 'posix-ms' or 'index'
    """
    assert isinstance(timestamp, int)

    for unit, factor in FACTOR_TO_SECONDS.items():
        if LOWER_RECORD_DATE_TIMESTAMP < factor * float(timestamp) < UPPER_RECORD_DATE_TIMESTAMP:
            return unit

    # none worked, its not posix
    return None


def format_timestamp_range(
        timestamp_range: Tuple[int, int],
        timestamp_unit: Optional[str],
        timestamp_format: Optional[str]
) -> str:
    """
    Format a time range with unit.

    :param timestamp_range: range of timestamps
    :param timestamp_unit: timestamp unit, can be: formatted_timestamp or auto
    :param timestamp_format: the timestamp format string
    :return string:
    """
    if timestamp_unit is None:
        timestamp_unit = 'index'
    elif timestamp_unit == 'auto':
        guessed_units = tuple(guess_timestamp_posix_unit(ts) for ts in timestamp_range)
        timestamp_unit = guessed_units[0] if guessed_units[0] == guessed_units[1] else 'index'

    if timestamp_unit in FACTOR_TO_SECONDS:
        try:
            factor = FACTOR_TO_SECONDS[timestamp_unit]
            dts = [datetime.utcfromtimestamp(ts * factor)
                   for ts in timestamp_range]
            # print the first timestamp completely
            if timestamp_format:
                return ' : '.join(dt.strftime(timestamp_format) for dt in dts)
            # if format not given, use ISO for 1st, and just print what change for second.
            timestamp_format_d = {
                'date': '%Y/%m/%d',
                'time': '%H:%M:%S.%f'
            }
            timestamp_parts = [
                {
                    pname: dt.strftime(pformat)
                    for pname, pformat in timestamp_format_d.items()
                }
                for dt in dts
            ]
            timestamp_str = timestamp_parts[0]['date']
            timestamp_str += ' '
            timestamp_str += timestamp_parts[0]['time']
            timestamp_str += '  :  '
            if timestamp_parts[0]['date'] != timestamp_parts[1]['date']:
                timestamp_str = timestamp_parts[0]['date']
                timestamp_str += ' '
            timestamp_str += timestamp_parts[1]['time']
            return timestamp_str
        except ValueError as _:  # noqa: F841
            return ' : '.join(str(ts) for ts in timestamp_range) + f' ** FAIL to parse as posix {timestamp_unit}'
    else:  # not posix
        return ' : '.join(str(ts) for ts in timestamp_range)


def print_records(
        kapture_data, output_stream, show_detail, show_all,
        timestamp_unit=None,
        timestamp_formatting=None
) -> None:
    """
    Prints the records and trajectories to the output stream
    """
    # records (+trajectories)
    for record_name in ['trajectories', 'records_camera', 'records_lidar', 'records_wifi', 'records_bluetooth',
                        'records_gnss', 'records_accelerometer', 'records_gyroscope', 'records_magnetic']:
        records_field = getattr(kapture_data, record_name)
        records = list(kapture.flatten(records_field))
        nb_record = None if records_field is None else len(records)
        if not show_detail:
            print_key_value(f'nb {record_name}', nb_record, output_stream, show_none=show_all)
        elif records_field is not None or show_all:
            print_title(f'{record_name}', output_stream)
            if records_field is not None and nb_record > 0:
                timestamp_range = (min(records_field), max(records_field))
                timestamp_range_str = format_timestamp_range(timestamp_range, timestamp_unit, timestamp_formatting)
                sensors_ids = records_field.sensors_ids
                print_key_value(' ├─ timestamp range', timestamp_range_str, output_stream, show_none=show_all)
                print_key_value(' ├─ sensors', f'{len(sensors_ids)}: {sensors_ids}', output_stream, show_none=show_all)
            print_key_value(' └─ nb total', nb_record, output_stream, show_none=show_all)


def print_features(kapture_data, output_stream, show_detail, show_all) -> None:
    """
    Prints the features to the output stream
    """
    # image features
    for feature_name in ['keypoints', 'descriptors', 'global_features']:
        feature_collection = getattr(kapture_data, feature_name)
        nb_feature_types = None if feature_collection is None else len(list(feature_collection.keys()))
        if not show_detail:
            print_key_value(f'nb types {feature_name}', nb_feature_types, file=output_stream, show_none=show_all)
            if feature_collection is not None:
                for feature_type, features in feature_collection.items():
                    print_key_value(f' └─ nb images {feature_type} ', len(features), file=output_stream,
                                    show_none=show_all)
        elif feature_collection is not None or show_all:
            print_title(feature_name, file=output_stream)
            if feature_collection is not None:
                for feature_type, features in feature_collection.items():
                    print_key_value(' ├─ feature_type ', feature_type, file=output_stream, show_none=show_all)
                    print_key_value(' | ├─ kind ', features.type_name, file=output_stream, show_none=show_all)
                    print_key_value(' | ├─ data type', features.dtype.__name__, file=output_stream, show_none=show_all)
                    print_key_value(' | ├─ data size', features.dsize, file=output_stream, show_none=show_all)
                    if feature_name == 'descriptors':
                        print_key_value(' | ├─ keypoints_type', features.keypoints_type,
                                        file=output_stream, show_none=show_all)
                    if feature_name != 'keypoints':
                        print_key_value(' | ├─ metric_type', features.metric_type,
                                        file=output_stream, show_none=show_all)
                    print_key_value(' | └─ nb images ', len(list(features)), file=output_stream, show_none=show_all)
            print_key_value(f' └─ nb types {feature_name}', nb_feature_types, file=output_stream, show_none=show_all)


def print_matches(kapture_data, output_stream, show_detail, show_all) -> None:
    """
    Prints the matches to the output stream
    """
    # matches
    nb_kpts_types = None if kapture_data.matches is None else len(list(kapture_data.matches.keys()))
    if not show_detail:
        print_key_value('nb types ', nb_kpts_types, output_stream, show_all)
        if kapture_data.matches is not None:
            for kpt_type, matches in kapture_data.matches.items():
                print_key_value(f' └─ nb matching pairs {kpt_type} ', len(list(matches)),
                                output_stream, show_all)
    elif kapture_data.matches is not None or show_all:
        print_title('matches', output_stream)
        if kapture_data.matches is not None:
            for kpt_type, matches in kapture_data.matches.items():
                print_key_value(' ├─ keypoints_type ', kpt_type, output_stream, show_all)
                print_key_value(' | └─ nb pairs ', len(list(matches)), output_stream, show_all)
        print_key_value(' └─ nb types ', nb_kpts_types, output_stream, show_all)


def print_points(kapture_data, output_stream, show_detail, show_all) -> None:
    """
    Prints the 3D points (and observations) to the output stream
    """
    # points 3D
    nb_points3d = None if kapture_data.points3d is None else len(list(kapture_data.points3d))
    if not show_detail:
        print_key_value('nb points 3-D', nb_points3d, file=output_stream, show_none=show_all)
    elif kapture_data.points3d is not None or show_all:
        print_title('points 3-D', file=output_stream)
        print_key_value(' └─ nb points 3-D', nb_points3d, file=output_stream, show_none=show_all)
    # observations
    nb_observations_3d = kapture_data.observations.observations_number()\
        if kapture_data.observations is not None\
        else None
    nb_observations_2d = len([feat
                              for observations in kapture_data.observations.values()
                              for feats in observations.values()
                              for feat in feats]) if kapture_data.observations is not None else None
    if not show_detail:
        print_key_value('nb observed 3-D points', nb_observations_3d, file=output_stream, show_none=show_all)
        print_key_value('nb observation 2-D points', nb_observations_2d, file=output_stream, show_none=show_all)
    elif kapture_data.observations is not None or show_all:
        print_title('Observations', file=output_stream)
        if kapture_data.observations is not None:
            print_key_value(' ├─ nb observed 3-D', nb_observations_3d, file=output_stream, show_none=show_all)
        print_key_value(' └─ nb observations 2-D', nb_observations_2d, file=output_stream, show_none=show_all)


def print_command_line() -> None:
    """
    Do the print using the parameters given on the command line.
    """

    parser = argparse.ArgumentParser(description='Print on stdout (or given file) statistics about kapture dataset.')
    parser_verbosity = parser.add_mutually_exclusive_group()
    parser_verbosity.add_argument(
        '-v', '--verbose', nargs='?', default=logging.WARNING, const=logging.INFO,
        action=kapture.utils.logging.VerbosityParser,
        help='verbosity level (debug, info, warning, critical, ... or int value) [warning]')
    parser_verbosity.add_argument(
        '-q', '--silent', '--quiet', action='store_const', dest='verbose', const=logging.CRITICAL)
    parser.add_argument('-i', '--input', '-k', '--kapture', required=True,
                        help='path to kapture data root directory.')
    parser.add_argument('-o', '--output', required=False, default='-',
                        help='output file [stdout]')
    parser.add_argument('-a', '--all', action='store_true', default=False,
                        help='display all, even None')
    parser.add_argument('-d', '--detail', action='store_true', default=False,
                        help='display detailed')
    parser.add_argument('-t', '--timestamp_unit', choices=['auto', 'index', 'second', 'millisecond', 'microsecond'],
                        default='auto',
                        help='Force what timestamp really are (eg. millisecond) to display them nicely.'
                             'Auto means the program tries to guess. [auto]')
    parser.add_argument('-f', '--timestamp_formatting',
                        help='Tells what timestamp are, helps human display.')
    args = parser.parse_args()

    logger.setLevel(args.verbose)
    if args.verbose <= logging.DEBUG:
        # also let kapture express its logs
        kapture.utils.logging.getLogger().setLevel(args.verbose)

    args.input = path.abspath(args.input)
    # load
    with kapture.io.csv.get_all_tar_handlers(args.input) as tar_handlers:
        kapture_data = kapture.io.csv.kapture_from_dir(args.input, tar_handlers=tar_handlers)
        do_print(kapture_data, args.input, args.output, args.detail, args.all,
                 args.timestamp_unit, args.timestamp_formatting)


def do_print(
        kapture_data: kapture,
        kapture_path: str,
        output_filepath: str,
        show_detail: bool,
        show_all: bool,
        timestamp_unit: str,
        timestamp_formatting: str,
) -> None:
    """
    Print out kapture data:

    :param kapture_data: input kapture data to print.
    :param kapture_path: full path to kapture directory.
    :param output_filepath: file path where to print. '-' means stdout.
    :param show_detail: If true, show details about data (in depth)
    :param show_all: If true, prints even if None
    :param timestamp_unit: tells the unit of timestamp (eg. posix)
    :param timestamp_formatting: how to format the timestamp on display
    """

    # print
    with open_or_stdout(output_filepath) as output_stream:
        if show_detail:
            print_title('general', file=output_stream)
            print_key_value('path', kapture_path, file=output_stream, show_none=show_all)
            print_key_value('version', kapture_data.format_version, file=output_stream, show_none=show_all)

        print_sensors(kapture_data, output_stream, show_detail, show_all)
        print_rigs(kapture_data, output_stream, show_detail, show_all)
        print_records(kapture_data, output_stream, show_detail, show_all, timestamp_unit, timestamp_formatting)
        print_features(kapture_data, output_stream, show_detail, show_all)
        print_matches(kapture_data, output_stream, show_detail, show_all)
        print_points(kapture_data, output_stream, show_detail, show_all)


if __name__ == '__main__':
    print_command_line()
