import base64
import datetime
import itertools
import json
import logging
import os
import pickle
import urllib.request
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

# mapping of start, end
vacations = [
    # marathon
    (datetime.date(2017, 11, 9), datetime.date(2017, 11, 14)),
    # skiing
    (datetime.date(2018, 3, 12), datetime.date(2018, 3, 16)),
    # cycling bologna
    (datetime.date(2018, 4, 3), datetime.date(2018, 4, 13)),
    # schwappla
    (datetime.date(2018, 7, 26), datetime.date(2018, 7, 27)),
    # cycling tuscany
    (datetime.date(2018, 9, 24), datetime.date(2018, 10, 5)),
    # skiing
    (datetime.date(2019, 2, 18), datetime.date(2019, 2, 22)),
    # skiing
    (datetime.date(2019, 3, 11), datetime.date(2019, 3, 12)),
    # cycling greece
    (datetime.date(2019, 5, 20), datetime.date(2019, 6, 7)),
    # ccc
    (datetime.date(2019, 12, 25), datetime.date(2020, 1, 3)),
    # skiing
    (datetime.date(2020, 3, 9), datetime.date(2020, 3, 12)),
    # cycling coronapfad
    (datetime.date(2020, 6, 15), datetime.date(2020, 6, 26)),
    # schwappla
    (datetime.date(2020, 8, 17), datetime.date(2020, 8, 21)),
    # mtb
    (datetime.date(2020, 9, 4), datetime.date(2020, 9, 4)),
    # mega tour france/spain (not yet taken)
    (datetime.date(2021, 5, 3), datetime.date(2021, 5, 31)),
]

# not counting to vacation days (sick leave, bildungskarenz, moving, ...)
special_vacations = [
    # bildungskarenz mitarbeitermotivation
    (datetime.date(2019, 11, 1), datetime.date(2019, 11, 1)),
    (datetime.date(2019, 11, 8), datetime.date(2019, 11, 8)),
    (datetime.date(2019, 11, 15), datetime.date(2019, 11, 15)),
    (datetime.date(2019, 11, 22), datetime.date(2019, 11, 22)),
    (datetime.date(2019, 11, 29), datetime.date(2019, 11, 29)),

    # bildungskarenz mitarbeiterfuehrung
    (datetime.date(2019, 12, 6), datetime.date(2019, 12, 6)),
    (datetime.date(2019, 12, 13), datetime.date(2019, 12, 13)),
    (datetime.date(2019, 12, 20), datetime.date(2019, 12, 20)),
    (datetime.date(2019, 12, 27), datetime.date(2019, 12, 27)),

    # bildungskarenz zeitmanagement
    (datetime.date(2020, 1, 3), datetime.date(2019, 1, 3)),
    (datetime.date(2020, 1, 10), datetime.date(2019, 1, 10)),
    (datetime.date(2020, 1, 17), datetime.date(2019, 1, 17)),
    (datetime.date(2020, 1, 24), datetime.date(2019, 1, 24)),
    (datetime.date(2020, 1, 31), datetime.date(2020, 1, 31)),
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
    map = None

    def __init__(
            self, calendar, client, vacations, special_vacations,
            employment_started, weekly_working_days, refresh=False):

        self.map = {}
        self.client = client
        self.cal = calendar
        self.vacations = vacations
        self.special_vacations = special_vacations
        self.weekly_working_days = weekly_working_days
        self.today = datetime.date.today()
        self.employment_started = employment_started
        self._deflate_vacations()
        self._deflate_special_vacations()
        self._fetch_time_entries(refresh)
        self._generate_calendar()
        self._structure_time_entries()


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

    def _add_day_to_map(self, label, working_day, note=None):
        self.map[label] = {
            'working_day': bool(working_day),
            'hours_actually_worked': 0,
            'hours_should_worked': 8 if working_day else 0,
            'note': note or '',
        }

    def _add_worktime_to_map(self, label, hours):
        self.map[label]['hours_actually_worked'] += hours

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

    def _deflate_special_vacations(self):
        vacation_days = []
        for sdate, edate in self.special_vacations:
            delta = edate - sdate
            for i in range(delta.days + 1):
                vd = sdate + timedelta(days=i)
                vacation_days.append(vd)
                print(f'special vacation day: {vd}')
        print(f'special vacation days entered: {len(vacation_days)}')
        self.special_vacation_days_total = vacation_days

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

    def _structure_time_entries(self):
        for te in self.time_entries:
            self._add_worktime_to_map(
                te['start'].split('T')[0], te['dur'] / 3600 / 1000
            )

    def _generate_calendar(self):
        self.cal_working_days = []
        self.cal_non_working_days = []
        self.cal_vacation_days_countable = []

        ref = self.employment_started - relativedelta(days=1)
        while ref < self.today:
            ref = ref + relativedelta(days=1)
            label = ref.isoformat()
            if not cal.is_working_day(ref):
                reason = cal.get_holiday_label(ref) or 'weekend'
                print(f'-- {ref} is {reason}')
                self.cal_non_working_days.append(ref)
                self._add_day_to_map(label, False, reason)
                continue

            if ref.isoweekday() not in self.weekly_working_days:
                print(f'-- {ref} is not in your working days.')
                self.cal_non_working_days.append(ref)
                self._add_day_to_map(label, False, 'free-day')
                continue

            # special vacation
            if ref in self.special_vacation_days_total:
                print(f'-- {ref} on special vacation.')
                self._add_day_to_map(label, False, 'special vacation')
                continue

            if ref in self.vacation_days_total:
                print(f'-- {ref} on vacation.')
                self.cal_vacation_days_countable.append(ref)
                self._add_day_to_map(label, False, 'vacation')
                continue

            print(f'++ {ref} is a working day.')
            self.cal_working_days.append(ref)
            self._add_day_to_map(label, True, 'working day')

    def print_calendar(self):
        head = \
            f"{'date':<15}" \
            f"{'workday':<5}" \
            f"{'should':<5}" \
            f"{'worked':<5}" \
            f"{'note':<30}" \
            f"{'difference':<5}"

        print(head)
        special_days = []

        for date, entry in self.map.items():
            diff = entry['hours_actually_worked'] - entry['hours_should_worked']
            diff_str = format(diff, '+.2f')

            sumary = \
                f"{date:<15}" \
                f"{entry['working_day']:<5}" \
                f"{entry['hours_should_worked']:<5}" \
                f"{format(entry['hours_actually_worked'], '.2f'):<10}" \
                f"{entry['note']:<30}" \
                f"{diff_str:<5}"

            if diff < -4 or diff > 4:
                special_days.append(sumary)

            print(sumary)

        if special_days and False:
            print('found some extreme days, did you forget to map?')
            print(head)
            for sd in special_days:
                print(sd)


balance = LifeWorkBalance(
    calendar=cal, client=tc,
    vacations=vacations,
    special_vacations=special_vacations,
    employment_started=datetime.date(2017, 9, 15),
    weekly_working_days=[MON, TUE, THU, FRI],
    # refresh=True
)

balance.print_calendar()
print(f'{balance.overtime}h overtime.')
print(
    f'{balance.used_vacation} vacation days of '
    f'{balance.vacation_days_claim} used.'
)
