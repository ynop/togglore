# togglore
Tool for the timetracker [toggle](http://toggl.com/) to calculate the difference between tracked time and the time you should have worked in a given range.

## Setup

Create a config file and save it at ~/.togglore.
```sh
[Authentication]
API_KEY = 5b9f5e3fd7745a022781daf205f62c72

[Work Hours]
hours_per_day = 8.4
excluded_days = 2016-08-01,2016-12-24
```

## Run
```sh
# show diff for today
python3 run.py today

# show diff for the current week
python3 run.py thisweek

# show diff for the current month
python3 run.py thismonth

# show diff for the current year
python3 run.py thisyear

# show diff for the given month
python3 run.py month 08

# show diff from 2016.08.01 until today
python3 run.py since 2016.08.01
```
