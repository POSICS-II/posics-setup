import matplotlib.pyplot as plt
import numpy as np

from instruments.osciloscopes import PicoScope6000
from instruments.pulse_generator import PulseGeneratorTG5011

config_file = 'config.json'

pulse_generator = PulseGeneratorTG5011(config_file=config_file)


ps_1 = PicoScope6000(config_file=config_file, serial='FW878/020')
ps_2 = PicoScope6000(config_file=config_file, serial='FW881/048')
ps_1.check_status()
ps_2.check_status()

data_1 = ps_1.read_data()
data_2 = ps_2.read_data()

data = np.hstack([data_1, data_2])

for i in range(10):

    plt.figure()
    plt.step(ps_1.times * 1E9, data[i, :].T)
    plt.xlabel('Time [ns]')
    plt.ylabel('ADC []')
    plt.legend(loc='best')
    plt.savefig('tmp/test_{}.png'.format(i))

pulse_generator.close()