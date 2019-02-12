import configparser
import datetime


def parse_dates_from_config(dates_str):
    return [datetime.datetime.strptime(day_string, "%Y.%m.%d").date()
            for day_string in dates_str.split(',')]


class Config(object):
    def __init__(self, api_key=None, work_hours_per_day=8.4, public_holidays=None,
                 vacation_days=None, working_days=None, user_id=1, workspace=1,
                 vacation_days_per_year=25, started_on=None):
        self.api_key = api_key
        self.work_hours_per_day = work_hours_per_day
        self.vacation_days = vacation_days or []
        self.public_holidays = public_holidays or []
        self.working_days = working_days or []
        self.user_id = user_id
        self.workspace = workspace
        self.vacation_days_per_year = vacation_days_per_year
        self.started_on = started_on

    def write_to_file(self, path):
        cfg = configparser.ConfigParser()

        cfg['Authentication'] = {}
        cfg['Authentication']['API_KEY'] = self.api_key

        with open(path, 'w') as configfile:
            cfg.write(configfile)

    @classmethod
    def read_from_file(cls, path):
        cfg = configparser.ConfigParser()
        cfg.read(path)

        api_key = cfg['Authentication']['API_KEY']
        work_hours = cfg['Work Hours']['hours_per_day']

        working_days_string = cfg['Work Hours']['working_days']
        user_id = cfg['User Info']['id']
        try:
            started_on = parse_dates_from_config(cfg['User Info']['started_on'])[0]
        except Exception:
            started_on = datetime.datetime.today()
        workspace = cfg['User Info']['workspace']
        vacation_days_per_year = cfg['Work Hours']['vacation_days_per_year']
        working_days = [int(day) for day in working_days_string.split(',')]

        holidays = parse_dates_from_config(cfg['Work Hours']['public_holidays'])
        vacation_days = parse_dates_from_config(cfg['Work Hours']['vacation_days'])

        return cls(
            api_key=api_key, work_hours_per_day=float(work_hours),
            public_holidays=holidays,
            vacation_days=vacation_days,
            working_days=working_days,
            user_id=user_id, workspace=workspace,
            vacation_days_per_year=vacation_days_per_year,
            started_on=started_on
        )
