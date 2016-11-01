import configparser


class Config(object):
    def __init__(self, api_key=None):
        self.api_key = api_key

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

        return cls(api_key=api_key)
