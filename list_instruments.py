import pyvisa as visa
import logging

logger = logging.getLogger(__name__)

rm = visa.ResourceManager('@py')

for serial in rm.list_resources():

    print(serial)
    instrument = rm.open_resource(serial)

    try:
        print(instrument.query('*IDN?'))
    except visa.errors.VisaIOError:
        pass