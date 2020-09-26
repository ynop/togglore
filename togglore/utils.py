import datetime
import calendar
import math
from datetime import timedelta


def calculate_vacation_demand(entered_on, days_per_year):
    diff = datetime.datetime.today().date() - entered_on
    return math.ceil(diff.days / 365) * days_per_year


def sum_time_of_entries(entries):
    ms = 0

    for entry in entries:
        ms += entry['dur']

    return ms / 3600000.0


class WorkTimeCalculator(object):
    def __init__(self, work_hours_per_day=8.4, public_holidays=None,
                 vacation_days=None, working_days=None):
        self.work_hours_per_day = work_hours_per_day
        self.vacation_days = vacation_days or []
        self.public_holidays = public_holidays or []
        self.working_days = working_days or []

    def count_workdays_in_range(self, date_range):
        current = date_range.start
        workdays = 0
        working_days = self.working_days
        excluded_days = self.vacation_days + self.public_holidays
        while current <= date_range.end:
            if current.isoweekday() in working_days and current not in excluded_days:
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
    def this_month(cls):
        today = datetime.date.today()
        __, end_day = calendar.monthrange(today.year, today.month)
        start = datetime.date(today.year, today.month, 1)
        end = datetime.date(today.year, today.month, end_day)

        return cls(start, end)

    @classmethod
    def this_year(cls):
        today = datetime.date.today()
        start = datetime.date(today.year, 1, 1)
        end = datetime.date(today.year, 12, 31)

        return cls(start, end)

    @classmethod
    def month(cls, month):
        today = datetime.date.today()
        __, end_day = calendar.monthrange(today.year, month)
        start = datetime.date(today.year, month, 1)
        end = datetime.date(today.year, month, end_day)

        return cls(start, end)


def get_weekends(since=None):
    """
    get all weekend days since a given date up until today
    :param since: datetime.date
    :return: list of datetime.date of weekend days.
    """
    if not since:
        since = datetime.date(2014,1,1)

    to = datetime.date.today()
    delta = to - since

    weekend_days = []

    for i in range(delta.days + 1):
        day = since + timedelta(days=i)
        if day.weekday() >= 5:
            weekend_days.append(day)

    return weekend_days


def annotate_weekday_name(dates):
    annotated = {}

    for day in dates:
        annotated[day.strftime('%Y-%m-%d')] = day.strftime("%A")

    return annotated


def reduce(*event_lists):
    """
    intersect all events of multiple sources to one dict of date: summary
    """
    result = {}
    for cal_items in event_lists:
        for item in cal_items:
            try:
                ref = item['start'].get('date', None) or item['start'].get('dateTime')
            except:
                import ipdb; ipdb.set_trace()
                print()
            result[ref] = item['summary']

    return result


def append_annotate(*event_lists):
    """
    intersect all events of multiple sources to one dict of
    date: summary + summary + summary
    """
    result = {}
    baselist_keys = event_lists[0].keys()
    for cal_items in event_lists:
        for key, value in cal_items.items():
            if not key in baselist_keys:
                continue
            if key in result:
                result[key] = result[key] + ' | ' + value
            else:
                result[key] = value
    return result


def deflate(event):
    from_date = event['start']['date']
    to_date = event['end']['date']
    summary = event['summary']


    from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
    to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()

    days = [from_date]

    delta = to_date - from_date
    for i in range(delta.days + 1):
        cand = from_date + timedelta(days=i)
        if cand > to_date:
            break
        days.append(cand)

    result = {}
    for day in days:
        result[day.strftime('%Y-%m-%d')] = event

    return result
