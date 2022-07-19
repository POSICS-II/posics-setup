import json
import time

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import matplotlib

from posicssetup.instruments.oscilloscopes import PicoScope6000
from posicssetup.instruments.pulse_generator import PulseGeneratorTG5011
from posicssetup.instruments.linear_stage import LinearStageTDC001
from posicssetup.instruments.power_supply import Keithley2400
from posicssetup.io.writer import HDF5FileWriter
from posicssetup.io.utils import get_basename
from posicssetup.io.logger import Logger


matplotlib.use('TkAgg')


#logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s:%(message)s')
#logger = logging.getLogger(__name__)

config_file = 'config.json'

basename = get_basename(config_file)
logger = Logger(config_file=config_file, basename=basename)

writer = HDF5FileWriter(config_file=config_file, basename=basename)
picoamp = Keithley2400(config_file=config_file)
picoamp.set_output(True)

stage_vertical = LinearStageTDC001(config_file=config_file, name='vertical')
stage_horizontal = LinearStageTDC001(config_file=config_file, name='horizontal')

pulse_generator = PulseGeneratorTG5011(config_file=config_file)
pulse_generator.set_main_out(True)
pulse_generator.set_synch_out(False)

ps_1 = PicoScope6000(config_file=config_file, serial='FW878/020')
# ps_2 = PicoScope6000(config_file=config_file, serial='FW881/048')

ps_1.check_status()
# ps_2.check_status()

start_horizontal = stage_horizontal.center + stage_horizontal.length / 2
start_vertical = stage_vertical.center + stage_vertical.length / 2

stage_horizontal.move_to(start_horizontal)
stage_vertical.move_to(start_vertical)

x_previous = start_horizontal
y_previous = start_vertical

fig = plt.figure()
axes = fig.add_subplot()

for i in tqdm(range(stage_horizontal.n_steps), desc='Horizontal', leave=False):

    x = start_horizontal - stage_horizontal.step * i
    stage_horizontal.move_to(position=x, previous_position=x_previous)

    x_previous = x
    iterator_y = range(stage_vertical.n_steps) if (i % 2 == 0) else reversed(range(stage_vertical.n_steps))

    for j in tqdm(iterator_y, desc='Vertical', leave=False):

        y = start_vertical - stage_vertical.step * j
        stage_vertical.move_to(position=y, previous_position=y_previous)

        y_previous = y

        ps_1._setup_trigger()
        # ps_2._setup_trigger()
        ps_1._setup_data()
        # ps_2._setup_data()

        time.sleep(2)
        pulse_generator.set_synch_out(True)
        time.sleep(2)

        data_1 = ps_1.read_data()
        # data_2 = ps_2.read_data()
        # times_1 = ps_1.read_trigger_times()
        # times_2 = ps_2.read_trigger_times()

        ps_1.check_status()
        # ps_2.check_status()

        # data = np.hstack([data_1, data_2])
        # times = np.hstack([times_1, times_2])
        data = data_1
        # times = times_1

        pulse_generator.set_synch_out(False)

        writer.write_data(name="step_{}_{}".format(i, j), data=data)
        # writer.write_data(name="step_{}_{}".format(i, j), data=times, group='trigger')

        axes.clear()
        axes.plot(ps_1.times * 1E9, np.mean(data, axis=0).T)
        axes.set_xlabel('Time [ns]')
        axes.set_ylabel('ADC []')
        legend = ['Channel {}'.format(i) for i in range(data.shape[1])]
        axes.legend(legend, loc='best')
        fig.savefig(basename + '_waveforms_step_{}_{}.png'.format(i, j))

        # plt.figure()
        # plt.plot(times)
        # plt.show()

writer.close()
