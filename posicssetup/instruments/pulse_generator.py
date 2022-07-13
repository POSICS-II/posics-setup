import time
import pyvisa as visa
import json
import logging
import atexit

logger = logging.getLogger(__name__)

rm = visa.ResourceManager('@py')
TIME_SLEEP = 2.5


class PulseGeneratorTG5011:

    def __init__(self, config_file):

        with open(config_file, 'r') as f:
            self.config = json.load(f)['led']

        self.serial = self.config['serial']
        self._resource = rm.open_resource(self.serial, send_end=True)
        self.set_synch_out(False)
        self.set_main_out(False)
        self._setup_pulse()
        self.beep()

        atexit.register(self.close)

    def __str__(self):

        return self.query('*IDN?')

    def beep(self):

        self.write('BEEP')

    def close(self):

        self.set_synch_out(False)
        self.set_main_out(False)
        self.beep()
        self.write('LOCAL')
        self._resource.close()
        logger.info('Closing PulseGenerator ({})'.format(self.serial))

    def write(self, message: str):

        time.sleep(TIME_SLEEP)
        self._resource.write(message, )

    def query(self, message: str):

        time.sleep(TIME_SLEEP)
        response = self._resource.query(message)

        return response

    def _setup_pulse(self):

        self.write('WAVE {}'.format(self.config['mode']))
        self.write('PULSFREQ {}'.format(self.config['frequency']))
        self.write('PULSWID {}'.format(self.config['width']))
        self.write('PULSEDGE {}'.format(self.config['edge']))
        self.write('AMPUNIT VPP')
        self.write('AMPL {}'.format(self.config['amplitude']))
        self.write('DCOFFS {}'.format(self.config['offset']))

    def set_synch_out(self, enable: bool):

        message = 'ON' if enable else 'OFF'

        self.write('SYNCOUT {}'.format(message))
        logger.info('Setting trigger output of pulse generator ({}) to {}'.format(self.serial, message))

    def set_main_out(self, enable: bool):

        message = 'ON' if enable else 'OFF'

        self.write('OUTPUT {}'.format(message))
        logger.info('Setting main output of pulse generator ({}) to {}'.format(self.serial, message))
