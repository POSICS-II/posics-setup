import matplotlib.pyplot as plt
import numpy as np

from posicssetup.instruments.osciloscopes import PicoScope6000
from posicssetup.instruments.pulse_generator import PulseGeneratorTG5011
from posicssetup.instruments.linear_stage import LinearStageTDC001

config_file = 'config.json'

stage_vertical = LinearStageTDC001(config_file=config_file, name='vertical')
stage_horizontal = LinearStageTDC001(config_file=config_file, name='horizontal')

pulse_generator = PulseGeneratorTG5011(config_file=config_file)

ps_1 = PicoScope6000(config_file=config_file, serial='FW878/020')
ps_2 = PicoScope6000(config_file=config_file, serial='FW881/048')

stage_vertical.move_to_start()
stage_horizontal.move_to_start()

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

x_prev = 0
# for i, x in tqdm(enumerate(position_x_mm), desc='Horizontal'):
for i in tqdm(range(n_steps_x), desc='Horizontal', leave=False):

    x = start_position_x - step_x * i
    tdc_horizontal.move_absolute(position=position_to_motor(x), now=True, bay=0, channel=0)
    time_of_flight_x = compute_time_of_movement(x, velocity_x, acceleration_x, x0=x_prev)
    # for j, y in tqdm(iterator_y, desc='Vertical'):
    x_prev = x
    iterator_y = range(n_steps_y) if (i % 2 == 0) else reversed(range(n_steps_y))

    for j in tqdm(iterator_y, desc='Vertical', leave=False):

        y = start_position_y - step_y * j
        tdc_vertical.move_absolute(position=position_to_motor(y), now=True, bay=0, channel=0)
        time_of_flight_y = compute_time_of_movement(y, velocity_y, acceleration_y, x0=y_prev)

        time_of_flight = max(time_of_flight_x, time_of_flight_y)
        time.sleep(time_of_flight + WAIT_TIME)
        y_prev = y