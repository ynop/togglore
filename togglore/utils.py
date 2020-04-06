import datetime
import calendar


def sum_time_of_entries(entries):
    ms = 0

    for entry in entries:
        ms += entry['dur']

    return ms / 3600000.0

def get_time_of_running_entry(entry):
    if not entry:
        return 0.0
    current_time = int(datetime.datetime.now().strftime("%s"))
    duration = int(entry['duration'])
    return (current_time + duration) / 3600.0


class WorkTimeCalculator(object):
    def __init__(self, work_hours_per_day=8.4, excluded_days=[]):
        self.work_hours_per_day = work_hours_per_day
        self.excluded_days = excluded_days

    def count_workdays_in_range(self, date_range):
        current = date_range.start
        workdays = 0

        while current <= date_range.end:
            if current.isoweekday() not in [6, 7] and current not in self.excluded_days:
                workdays += 1

            current += datetime.timedelta(1)

        return workdays

    def time_to_work_in_range(self, date_range):
        weekdays = self.count_workdays_in_range(date_range)

        return weekdays * self.work_hours_per_day


class DateRange(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    @classmethod
    def since(cls, start):
        start = datetime.datetime.strptime(start, "%Y.%m.%d").date()
        end = datetime.date.today()
        return cls(start, end)

    @classmethod
    def parse_from_iso_strings(cls, start, end):
        start = datetime.datetime.strptime(start, "%Y.%m.%d").date()
        end = datetime.datetime.strptime(end, "%Y.%m.%d").date()
        return cls(start, end)

    @classmethod
    def today(cls):
        return cls(datetime.date.today(), datetime.date.today())

    @classmethod
    def this_week(cls):
        today = datetime.date.today()
        start = today - datetime.timedelta(today.weekday())
        end = start + datetime.timedelta(6)

        return cls(start, end)

    @classmethod
    def this_week_until_today(cls):
        today = datetime.date.today()
        start = today - datetime.timedelta(today.weekday())
        end = today

        return cls(start, end)

    @classmethod
    def this_month(cls):
        today = datetime.date.today()
        __, end_day = calendar.monthrange(today.year, today.month)
        start = datetime.date(today.year, today.month, 1)
        end = datetime.date(today.year, today.month, end_day)

        return cls(start, end)

    @classmethod
    def this_month_until_today(cls):
        today = datetime.date.today()
        __, end_day = calendar.monthrange(today.year, today.month)
        start = datetime.date(today.year, today.month, 1)
        end = today

        return cls(start, end)

    @classmethod
    def this_year(cls):
        today = datetime.date.today()
        start = datetime.date(today.year, 1, 1)
        end = datetime.date(today.year, 12, 31)

        return cls(start, end)

    @classmethod
    def this_year_until_today(cls):
        today = datetime.date.today()
        start = datetime.date(today.year, 1, 1)
        end = today

        return cls(start, end)

    @classmethod
    def month(cls, month):
        today = datetime.date.today()
        __, end_day = calendar.monthrange(today.year, month)
        start = datetime.date(today.year, month, 1)
        end = datetime.date(today.year, month, end_day)

        return cls(start, end)
