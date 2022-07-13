import time
import pyvisa as visa
import json
import logging
import atexit

logger = logging.getLogger(__name__)

rm = visa.ResourceManager('@py')
TIME_SLEEP = 2.5


class Keithley2400:

    def __init__(self, config_file: str,  baud_rate=9600, data_bits=8, read_termination='\r', write_termination='\r',
                 **kwargs):

        with open(config_file, 'r') as f:
            self.config = json.load(f)['sipm']

        self.serial = self.config['serial']
        self.voltage = self.config['voltage']
        self._resource = rm.open_resource(self.serial, baud_rate=baud_rate, data_bits=data_bits,
                                          read_termination=read_termination,
                                          write_termination=write_termination, **kwargs)
        self.set_output(enable=False)
        self.write('SOUR:VOLT:RANG MAX')
        self.set_voltage(self.voltage)
        atexit.register(self.close)

    def close(self):

        self.set_output(enable=False)
        self._resource.close()

    def write(self, message: str):

        time.sleep(TIME_SLEEP)
        self._resource.write(message)

    def query(self, message: str):

        time.sleep(TIME_SLEEP)
        self._resource.query(message)

    def set_voltage(self, voltage: float):

        self.write('SOUR:VOLT:LEV:IMM:AMPL {:.3f}'.format(voltage))

    def set_output(self, enable: bool):

        enable = 'ON' if enable else 'OFF'
        self.write('OUTP {}'.format(enable))