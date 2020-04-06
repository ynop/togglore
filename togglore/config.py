import configparser
import datetime


class Config(object):
    def __init__(self, api_key=None, work_hours_per_day=8.4, excluded_days=[], user_id=1, workspace=1, project=1, boss_name="Boss", hourly_wage=10.0, eur_to_brl={'value': '5.0', 'date': '30/01/2020'}):
        self.api_key = api_key
        self.work_hours_per_day = work_hours_per_day
        self.excluded_days = excluded_days
        self.user_id = user_id
        self.workspace = workspace
        self.project = project
        self.boss_name = boss_name
        self.hourly_wage = hourly_wage
        self.eur_to_brl = eur_to_brl

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
        excluded_days_string = cfg['Work Hours']['excluded_days']
        user_id = cfg['User Info']['id']
        workspace = cfg['User Info']['workspace']
        project = cfg['User Info']['project']
        boss_name = cfg['Personal Details']['boss_name']
        hourly_wage = float(cfg['Personal Details']['hourly_wage'])
        eur_to_brl = cfg['EUR to BRL']
        

        day_strings = excluded_days_string.split(',')
        days = []

        for day_string in day_strings:
            days.append(datetime.datetime.strptime(day_string, "%Y.%m.%d").date())

        return cls(api_key=api_key, work_hours_per_day=float(work_hours), excluded_days=days, user_id=user_id,
                   workspace=workspace, project=project, boss_name=boss_name, hourly_wage=hourly_wage, eur_to_brl=eur_to_brl)
