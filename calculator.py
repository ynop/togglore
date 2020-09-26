import base64
import datetime
import itertools
import json
import logging
import os
import urllib
import urllib.request
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from urllib.parse import urlparse
from workalendar.europe import Austria
from datetime import date, timedelta
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
working_days = [MON, TUE, THU, FRI]

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

vacation_days = []
for sdate, edate in vacations:
    delta = edate - sdate
    for i in range(delta.days + 1):
        vd = sdate + timedelta(days=i)
        vacation_days.append(vd)
        print(f'vacation day: {vd}')
print(f'vacation days entered: {len(vacation_days)}')

today = datetime.date.today()
employment_started = datetime.date(2017, 9, 15)
employment_duration = datetime.date.today() - employment_started

workdays = []
non_working_days = []
countable_vacation_days=[]

ref = employment_started - relativedelta(days=1)
while ref < today:
    ref = ref + relativedelta(days=1)
    if not cal.is_working_day(ref):
        reason = cal.get_holiday_label(ref) or 'weekend.'
        print(f'-- {ref} is {reason}')
        non_working_days.append(ref)
        continue
    if ref.isoweekday() not in working_days:
        print(f'-- {ref} is not in your working days.')
        non_working_days.append(ref)
        continue
    if ref in vacation_days:
        print(f'-- {ref} on vacation.')
        countable_vacation_days.append(ref)
        continue

    print(f'++ {ref} is a working day.')
    workdays.append(ref)

should_worked_h = len(workdays) * 8


time_entries = []
for ws in tc.workspaces:
    from_date = employment_started
    to_date = employment_started + relativedelta(years=1)
    while True:
        logger.info(f'query workspace {ws} from {from_date} to {to_date}')
        print(f'query workspace {ws} from {from_date} to {to_date}')
        te = tc.time_entries(
            ws, DateRange(from_date, to_date)
        )
        time_entries.extend(te)

        # if the last to_date was including today, we are done here.
        if to_date > today:
            break

        from_date = to_date + relativedelta(days=1)
        to_date = from_date + relativedelta(years=1)

user_entries = []
for entry in time_entries:
    if entry['uid'] != tc.user_id:
        logger.debug(f'ignoring timestamp from {entry["user"]}')
        print(f'ignoring timestamp from {entry["user"]}')
        continue
    user_entries.append(entry)
dur = 0

for te in user_entries:
    dur += te['dur']

worked_h = dur / 3600 / 1000

print(f'{int(worked_h - should_worked_h)}h overtime.')
print(f'{len(countable_vacation_days)} countable vacation days.')

class LifeWorkBalance(object):
    def __init__(self):
        pass
