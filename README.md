# togglore
Tool for the timetracker [toggle](http://toggl.com/) to calculate the difference between tracked time and the time you should have worked in a given range.

## Setup

# dev environment
create a python 3.8 venv
`virtualenv -p python3.8 venv` from the root of the repository 
and activate it `. venv/bin/activate`
then install the requirements `pip install -r requirements.txt`

create an env file `runtime.env` in the root dir of the project and add following values:
```
export API_KEY=xxxx
export WORKSPACE=xxxx
export RECRUITMENT_DATE=2017.9.15
# 1, 2, 3, 4, 5, 6, 7 = MON, TUE, WED, THU, FRI, SAT, SUN
export WORKING_DAYS=1,2,4,5
export HOURS_PER_DAY=8

```
source it with `source runtime.env`

### where to get this info
#### workspace id
go to https://toggl.com/app/workspaces/ and edit the workspace, get the id from the URL
#### api key
https://toggl.com/app/profile on the bottom
#### user id [id]
make a get request to your workspace

```sh
curl -v -u {API_TOKEN}:api_token \
-X GET https://www.toggl.com/api/v8/workspaces/{worksapce_id}/users
```

## Configure
read through calculator.py and make your vacation days, special vacation days and working days/hours fixed.
this is currently not easily configurable except changing it in the python file but will be, soon.

## Run
```sh
python calculator.py
```

currently every execution gets cached, to recalculate values you need to run 
`rm .cache_toggle_entries.pkl`. this is because we are in testing mode to make it easier.

The output is something like:
```
2021-02-18     1    8    8.16      working day                   +0.16
2021-02-19     1    8    3.00      working day                   -5.00
2021-02-20     0    0    0.00      weekend                       +0.00
2021-02-21     0    0    0.00      weekend                       +0.00
2021-02-22     1    8    5.41      working day                   -2.59
2021-02-23     1    8    7.06      working day                   -0.94
2021-02-24     0    0    7.59      free-day                      +7.59
2021-02-25     1    8    5.22      working day                   -2.78
2021-02-26     1    8    0.00      working day                   -8.00
2021-02-27     0    0    0.00      weekend                       +0.00
2021-02-28     0    0    0.00      weekend                       +0.00
2021-03-01     1    8    5.05      working day                   -2.95
2021-03-02     1    8    7.16      working day                   -0.84
2021-03-03     0    0    0.62      free-day                      +0.62
2021-03-04     1    8    8.54      working day                   +0.54
2021-03-05     1    8    3.22      working day                   -4.78
2021-03-06     0    0    0.00      weekend                       +0.00
2021-03-07     0    0    0.00      weekend                       +0.00
2021-03-08     1    8    6.33      working day                   -1.67
2021-03-09     1    8    7.14      working day                   -0.86
2021-03-10     0    0    8.01      free-day                      +8.01
2021-03-11     1    8    8.06      working day                   +0.06
2021-03-12     1    8    0.00      working day                   -8.00
2021-03-13     0    0    0.00      weekend                       +0.00
2021-03-14     0    0    0.00      weekend                       +0.00
2021-03-15     1    8    8.49      working day                   +0.49
2021-03-16     1    8    3.85      working day                   -4.15
2021-03-17     0    0    4.94      free-day                      +4.94
2021-03-18     1    8    5.90      working day                   -2.10
2021-03-19     1    8    8.96      working day                   +0.96
2021-03-20     0    0    1.82      weekend                       +1.82
2021-03-21     0    0    7.87      weekend                       +7.87
2021-03-22     1    8    3.30      working day                   -4.70
2021-03-23     1    8    6.05      working day                   -1.95
2021-03-24     0    0    0.00      free-day                      +0.00
2021-03-25     1    8    10.64     working day                   +2.64
2021-03-26     1    8    3.63      working day                   -4.37
2021-03-27     0    0    2.02      weekend                       +2.02
2021-03-28     0    0    0.00      weekend                       +0.00
2021-03-29     1    8    5.19      working day                   -2.81
2021-03-30     1    8    8.20      working day                   +0.20
2021-03-31     0    0    5.39      free-day                      +5.39
2021-04-01     1    8    3.53      working day                   -4.47
2021-04-02     1    8    0.00      working day                   -8.00
2021-04-03     0    0    0.00      weekend                       +0.00
2021-04-04     0    0    0.00      weekend                       +0.00
2021-04-05     0    0    0.00      Easter Monday                 +0.00
2021-04-06     1    8    0.00      working day                   -8.00
2021-04-07     0    0    6.10      free-day                      +6.10
2021-04-08     1    8    5.44      working day                   -2.56
2021-04-09     1    8    2.47      working day                   -5.53
2021-04-10     0    0    0.00      weekend                       +0.00
2021-04-11     0    0    0.00      weekend                       +0.00
2021-04-12     1    8    9.28      working day                   +1.28
2021-04-13     1    8    7.42      working day                   -0.58
2021-04-14     0    0    4.91      free-day                      +4.91
2021-04-15     1    8    8.52      working day                   +0.52
2021-04-16     1    8    5.43      working day                   -2.57
2021-04-17     0    0    0.00      weekend                       +0.00
2021-04-18     0    0    0.00      weekend                       +0.00
2021-04-19     1    8    6.69      working day                   -1.31
2021-04-20     1    8    9.87      working day                   +1.87
2021-04-21     0    0    0.00      free-day                      +0.00
2021-04-22     1    8    6.50      working day                   -1.50
-1h overtime.
62 vacation days of 80.0 used.
```
