from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tzlocal import get_localzone
import calendar
import locale
import time
import uuid
import os

from .config import signature, location

def getFileName(format: str):
    options = {
        "ltime": datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
        "stime": datetime.now().strftime('%Y-%m-%d'),
        "title": signature["title"],
        "producer": signature["producer"],
        "uuid": uuid.uuid4()
    }

    filename = format.format(**options)

    return os.path.realpath(f"./out/{filename}.pdf")

class _Dates():
    def __init__(self):
        locale.setlocale(locale.LC_TIME, location)

    def today(self):
        return datetime.now().strftime("%A, %d de %B de %Y, %H:%M:%S")

    def now(self, days: int = 0):
        return (datetime.now() - timedelta(days=days)).strftime("%d/%m/%Y, 00:00:00")
    
    @property
    def days_month(self):
        now = datetime.now()
        return calendar.monthrange(now.year, now.month)[1]

    def getTimeZone(self):
        time_zone = get_localzone()
        displacement = time_zone.utcoffset(datetime.now())
        hours = displacement.total_seconds() // 3600
        minutes = (displacement.total_seconds() // 60) % 60

        return f"{str(time_zone)}, GMT{int(hours)}:{int(minutes)}"

    def getISODate(self, days: int = 0):
        date = datetime.now() - timedelta(days=days)
        return date.strftime("%Y-%m-%dT%H:%M:%SZ")

    def get(self, years: int = 0, months: int = 0, days: int = 0, hours: int = 0, minutes: int = 0, reset: bool = False) -> datetime: 
        current_date = datetime.now()
        new_date = current_date + relativedelta(years=years, months=months, days=days, hours=hours, minutes=minutes)
        if reset:
            new_date = new_date.replace(day=1)
        return new_date

    def getLastDay(self, date):
        next_month = date + relativedelta(months=1)
        last_day = next_month - relativedelta(days=1)
        return last_day

    def toMilliseconds(self, dt: datetime):
        milliseconds = int(time.mktime(dt.timetuple()) * 1000)
        return milliseconds
    
    from datetime import datetime, timedelta


    def get_last_month_range(self):
        today = datetime.now()
        first_day_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate the first day of the last month
        if first_day_current_month.month == 1:
            first_day_last_month = first_day_current_month.replace(year=first_day_current_month.year - 1, month=12)
        else:
            first_day_last_month = first_day_current_month.replace(month=first_day_current_month.month - 1)

        last_day_last_month = first_day_current_month - timedelta(days=1)
        
        gte = int(first_day_last_month.timestamp()) * 1000
        lte = int(last_day_last_month.timestamp()) * 1000 + 86399000  # Add 23 hours, 59 minutes, and 59 seconds
        
        return {"gte": gte, "lte": lte}


    def get_current_month_range(self):
        today = datetime.now()
        first_day_current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day_current_month = first_day_current_month.replace(day=28) + timedelta(days=4)  # Ensure the last day of the month is obtained
        
        gte = int(first_day_current_month.timestamp()) * 1000
        lte = int(last_day_current_month.timestamp()) * 1000
        
        return {"gte": gte, "lte": lte}

dates = _Dates()
