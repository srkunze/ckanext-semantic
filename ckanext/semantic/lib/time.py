import datetime
import dateutil


def min_datetime(datetime_string):
    return dateutil.parser.parse(datetime_string, default=datetime.datetime.min)


def max_datetime(datetime_string):
    for day in range(31, 27, -1):
        try:
            return dateutil.parser.parse(datetime_string, default=datetime.datetime.max.replace(day=day))
        except ValueError:
            pass


def to_naive_utc(datetime):
    if datetime.utcoffset() is not None:
        return datetime.replace(tzinfo=None) - datetime.utcoffset()
        
    return datetime

