import base64
import datetime
import itertools
import json
import json
import logging
import os
import pickle
import urllib
import urllib.request
from datetime import date, timedelta
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from urllib.parse import urlparse
from workalendar.europe import Austria

from togglore.toggl import TogglClient
from togglore.utils import DateRange

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

API_KEY = 'fa85b49a932f6fea291be8ae8a9f7204'
# user_id = 3577081
workspace = 2302677

tc = TogglClient(API_KEY)
cal = Austria()

# assign the order of work days, starting a week with monday (0-7)
MON, TUE, WED, THU, FRI, SAT, SUN = range(1, 8)

# calculate vacation days

# todo import from config file
vacations = [
    # mapping of start, end
    (datetime.date(2017, 11, 9), datetime.date(2017, 11, 14)),
    (datetime.date(2017, 3, 12), datetime.date(2017, 3, 16)),
    (datetime.date(2018, 4, 4), datetime.date(2018, 4, 12)),
    (datetime.date(2018, 7, 26), datetime.date(2018, 7, 27)),
    (datetime.date(2018, 9, 25), datetime.date(2018, 10, 4)),
    (datetime.date(2019, 2, 19), datetime.date(2019, 2, 22)),
    (datetime.date(2019, 3, 11), datetime.date(2019, 3, 12)),
    (datetime.date(2019, 5, 20), datetime.date(2019, 6, 7)),
    (datetime.date(2020, 3, 9), datetime.date(2020, 3, 12)),
    (datetime.date(2020, 6, 15), datetime.date(2020, 6, 26)),
    (datetime.date(2020, 8, 18), datetime.date(2020, 8, 21)),
    (datetime.date(2020, 9, 4), datetime.date(2020, 9, 4)),
]


def save_obj(obj, name):
    with open(f'.cache_{name}.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(f'.cache_{name}.pkl', 'rb') as f:
        return pickle.load(f)


class LifeWorkBalance(object):
    vacations = None
    vacation_days_total = None

    cal_vacation_days_countable = None
    cal_non_working_days = None
    cal_working_days = None
    time_entries = None

    def __init__(
            self, calendar, client, vacations, employment_started,
            weekly_working_days, refresh=False):

        self.client = client
        self.cal = calendar
        self.vacations = vacations
        self.weekly_working_days = weekly_working_days
        self.today = datetime.date.today()
        self.employment_started = employment_started


        self._deflate_vacations()
        self._fetch_time_entries(refresh)
        self._generate_calendar()

    @property
    def employment_duration(self):
        return datetime.date.today() - self.employment_started

    @property
    def total_seconds_worked(self):
        dur = 0
        for te in self.time_entries:
            dur += te['dur']
        return dur

    @property
    def total_hours_worked(self):
        return self.total_seconds_worked / 3600 / 1000

    @property
    def hours_should_worked(self):
        return len(self.cal_working_days) * 8

    @property
    def overtime(self):
        return int(self.total_hours_worked - self.hours_should_worked)

    @property
    def used_vacation(self):
        return len(self.cal_vacation_days_countable)

    @property
    def vacation_days_claim(self):
        return (int(self.employment_duration.days / 365) + 1) \
               * 25 / 5 * len(self.weekly_working_days)

    def _deflate_vacations(self):
        vacation_days = []
        for sdate, edate in self.vacations:
            delta = edate - sdate
            for i in range(delta.days + 1):
                vd = sdate + timedelta(days=i)
                vacation_days.append(vd)
                print(f'vacation day: {vd}')
        print(f'vacation days entered: {len(vacation_days)}')
        self.vacation_days_total = vacation_days

    def _fetch_time_entries(self, refresh=False):
        cache_name = 'toggle_entries'
        if not refresh:
            try:
                self.time_entries = load_obj(cache_name)
                print('using cache instead of querying toggl.')
                return
            except Exception as ex:
                print(f'cannot load cache {ex}')

        time_entries = []
        for ws in self.client.workspaces:
            from_date = self.employment_started
            to_date = self.employment_started + relativedelta(years=1)
            while True:
                print(f'query workspace {ws} from {from_date} to {to_date}')
                te = tc.time_entries(
                    ws, DateRange(from_date, to_date)
                )
                time_entries.extend(te)

                # if the last to_date was including today, we are done here.
                if to_date > self.today:
                    break

                from_date = to_date + relativedelta(days=1)
                to_date = from_date + relativedelta(years=1)

        user_entries = []
        for entry in time_entries:
            if entry['uid'] != self.client.user_id:
                logger.debug(f'ignoring timestamp from {entry["user"]}')
                print(f'ignoring timestamp from {entry["user"]}')
                continue
            user_entries.append(entry)
        self.time_entries = user_entries
        save_obj(user_entries, cache_name)

    def _generate_calendar(self):
        self.cal_working_days = []
        self.cal_non_working_days = []
        self.cal_vacation_days_countable = []
        ref = self.employment_started - relativedelta(days=1)
        while ref < self.today:
            ref = ref + relativedelta(days=1)
            if not cal.is_working_day(ref):
                reason = cal.get_holiday_label(ref) or 'weekend.'
                print(f'-- {ref} is {reason}')
                self.cal_non_working_days.append(ref)
                continue
            if ref.isoweekday() not in self.weekly_working_days:
                print(f'-- {ref} is not in your working days.')
                self.cal_non_working_days.append(ref)
                continue
            if ref in self.vacation_days_total:
                print(f'-- {ref} on vacation.')
                self.cal_vacation_days_countable.append(ref)
                continue

            print(f'++ {ref} is a working day.')
            self.cal_working_days.append(ref)


balance = LifeWorkBalance(
    calendar=cal, client=tc,
    vacations=vacations,
    employment_started=datetime.date(2017, 9, 15),
    weekly_working_days=[MON, TUE, THU, FRI],
    # refresh=True
)

print(f'{balance.overtime}h overtime.')
print(
    f'{balance.used_vacation} vacation days of '
    f'{balance.vacation_days_claim} used.'
)

print(balance.calendar)

