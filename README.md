# togglore
Tool for the timetracker [toggle](http://toggl.com/) to calculate the difference between tracked time and the time you should have worked in a given range.

## Setup

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

# HowTo for Win10, WSLv2, AlpineWSL, Python3.9.5
```
apk update
apk upgrade
apk add python3 git
cat .togglore > ~/.togglore
cd
git clone https://github.com/ynop/togglore.git
cd togglore/
python3 run.py
time python3 run.py since 2021.11.01
```
E-mail notification
```
apk add msmtp mailx
cat /mnt/d/WSL/Alpine/msmtprc > /etc/msmtprc
ln -sf /usr/bin/msmtp /usr/sbin/sendmail
cd ~/togglore/
python3 run.py since 2021.10.1 | mail -s "Toggl" e-mail_user@Your_domain.tld
```

## or Thanks to christiandt we can use Python2
```
apk update
apk upgrade
apk add python2 git
python -m ensurepip --upgrade
mkdir ~/Dropbox
cat .togglore > ~/Dropbox/toggl.txt
cd
git clone https://github.com/christiandt/togglore.git
cd togglore/
pip install -r requirements.txt
time python run.py since 2021.11.01
```
