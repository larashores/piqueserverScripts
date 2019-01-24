from datetime import datetime, timezone
import time


def current_timestamp():
    return datetime.utcnow().timestamp()


def time_string(timestamp):
    if timestamp is None:
        return 'now'
    dtime = datetime.fromtimestamp(int(timestamp[0])).replace(tzinfo=timezone.utc).astimezone()
    return dtime.strftime('%H:%M')


def parse_time_string(time_string):
    """
    Returns the seconds past epoch when given a time string in local time
    Should be in any of the following formats:
        HH::MM, HH:MM::dd, HH::MM::dd::mm, HH::MM::dd::mm::yyyy
    """
    current_time = time.localtime()
    values = time_string.split(':')
    if not 2 <= len(values) <= 5:
        raise ValueError('Incorrect time_string format')
    elif len(values) == 2:
        hours, minutes = values
        day = current_time.tm_mday
        month = current_time.tm_mon
        year = current_time.tm_year
    elif len(values) == 3:
        hours, minutes, day = values
        month = current_time.tm_mon
        year = current_time.tm_year
    elif len(values) == 4:
        hours, minutes, day, month = values
        year = current_time.tm_year
    elif len(values) == 5:
        hours, minutes, day, month, year = values

    d_time = datetime(int(year), int(month), int(day), int(hours), int(minutes))
    return time.mktime(time.gmtime(d_time.timestamp()))
