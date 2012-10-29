import datetime
import dateutil


def min_datetime(datetime_string):
    return dateutil.parser.parse(datetime_string, default=datetime.datetime(2000, 1, 1, 0, 0, 0, 0, None))


def max_datetime(datetime_string):
    for day in range(31, 27, -1):
        try:
            return dateutil.parser.parse(datetime_string, default=datetime.datetime(2000, 12, day, 23, 59, 59, 999999, None))
        except ValueError:
            pass


def to_naive_utc(datetime):
    if datetime.utcoffset() is not None:
        return datetime.replace(tzinfo=None) - datetime.utcoffset()
        
    return datetime

