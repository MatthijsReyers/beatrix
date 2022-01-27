from os.path import expanduser
import json


class ConfigFile():
    def __init__(self, logger):
        self.logger = logger
        self.local_server = False
        self.raspberry_ip = '192.168.23.211'

        home = expanduser("~")
        self.url = home + '/.beatrix-config.json'

        try:
            with open(self.url, 'r') as file:
                try:
                    config = json.load(file)
                    self.local_server = config['local_server']
                    self.raspberry_ip = config['raspberry_ip']
                except json.decoder.JSONDecodeError:
                    logger.log('Config file was corrupted, using default values instead.')
        except FileNotFoundError as e:
            logger.log('Using default config values.')

    def save(self):
        with open(self.url, 'w') as file:
            file.write(json.dumps({
                'local_server': self.local_server,
                'raspberry_ip': self.raspberry_ip
            }))
        self.logger.log('Saving config file.')
