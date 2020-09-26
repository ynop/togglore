# togglore
Tool for the timetracker [toggle](http://toggl.com/) to calculate the difference between tracked time and the time you should have worked in a given range.

## Setup

# dev environment
create a python 3.8 venv
`virtualenv -p python3.8 venv` from the root of the repository 
and activate it `. venv/bin/activate`
then install the requirements `pip install -r requirements.txt`


Create a config file and save it at ~/.togglore.
```sh
[Authentication]
API_KEY = 5b9f5e3fd7745a022781daf205f62c72

[Work Hours]
hours_per_day = 8.4
excluded_days = 2016.01.01

[User Info]
id = 1
workspace = 1
```

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
The output is something like:
```
Hours to do: 176.00h (22.00 days)
Hours worked: 186.65h (23.33 days)
Difference: 10.65h (1.33 days)
```
