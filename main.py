import json
import time

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import logging
import matplotlib
import h5py

from posicssetup.instruments.oscilloscopes import PicoScope6000
from posicssetup.instruments.pulse_generator import PulseGeneratorTG5011
from posicssetup.instruments.linear_stage import LinearStageTDC001
from posicssetup.instruments.power_supply import Keithley2400

matplotlib.use('TkAgg')


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

config_file = 'config.json'

output_file = h5py.File(json.load(open(config_file, 'r'))['writer']['output_file'], 'x')

picoamp = Keithley2400('config.json')
picoamp.set_output(True)

stage_vertical = LinearStageTDC001(config_file=config_file, name='vertical')
stage_horizontal = LinearStageTDC001(config_file=config_file, name='horizontal')

pulse_generator = PulseGeneratorTG5011(config_file=config_file)
pulse_generator.set_main_out(True)

ps_1 = PicoScope6000(config_file=config_file, serial='FW878/020')
ps_2 = PicoScope6000(config_file=config_file, serial='FW881/048')

ps_1.check_status()
ps_2.check_status()

start_horizontal = stage_horizontal.center + stage_horizontal.length / 2
start_vertical = stage_vertical.center + stage_vertical.length / 2

stage_horizontal.move_to(start_horizontal)
stage_vertical.move_to(start_vertical)

x_previous = start_horizontal
y_previous = start_vertical

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
        ps_2._setup_trigger()
        ps_1._setup_data()
        ps_2._setup_data()

        time.sleep(2)
        pulse_generator.set_synch_out(True)

        data_1 = ps_1.read_data()
        data_2 = ps_2.read_data()

        ps_1.check_status()
        ps_2.check_status()

        data = np.hstack([data_1, data_2])

        pulse_generator.set_synch_out(False)

        output_file.create_dataset("Step_{}_{}".format(i, j), data=data, compression="gzip", compression_opts=9)

output_file.close()
