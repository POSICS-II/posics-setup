import logging
import json
import sys


class Logger:

    def __init__(self, config_file: str, basename : str):

        with open(config_file, 'r') as f:
            self.config = json.load(f)['logger']

        self.output_file = basename + '.log'

        self.logger = logging.getLogger()
        self.log_level = self.config['level']
        self._file_handler = logging.FileHandler(self.output_file)
        formatter = logging.Formatter("%(asctime)s [%(name)s] [%(levelname)-5.5s]  %(message)s")
        self.logger.setLevel(self.log_level)
        self._file_handler.setFormatter(formatter)
        self.logger.addHandler(self._file_handler)

        self._console_handler = logging.StreamHandler()
        self._console_handler.setFormatter(formatter)
        self.logger.addHandler(self._console_handler)
