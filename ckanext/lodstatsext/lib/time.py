import datetime


def seconds(timedelta):
    return float(timedelta.days * 24 * 3600 + timedelta.seconds)

