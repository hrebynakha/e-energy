from zoneinfo import ZoneInfo
from datetime import datetime


def convert_minutes_to_hours(minutes):
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours}:{minutes:02d}"


def get_current_minutes():
    timezone = ZoneInfo("Europe/Kiev")
    now = datetime.now(tz=timezone)
    return now.hour * 60 + now.minute
