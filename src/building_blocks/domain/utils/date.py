import datetime as dt


def get_current_timestamp() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


DEFAULT_DATE_FORMAT = "%d-%m-%Y, %H:%M:%S"
