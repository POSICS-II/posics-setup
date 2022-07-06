from thorlabs_apt_device.devices.tdc001 import TDC001
from utils import position_to_motor, velocity_to_motor, acceleration_to_motor, compute_time_of_movement, MAX_ACCELERATION, MAX_VELOCITY
import time
import logging
from tqdm import tqdm
import json


with open('../config.json', 'r') as f:

    data = json.load(f)
    config = data['stage']

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

WAIT_TIME = config['wait_time']
tdc_vertical = TDC001(serial_port=config['port_x'], home=False)
tdc_horizontal = TDC001(serial_port=config['port_y'], home=False)
time.sleep(WAIT_TIME)
print(tdc_horizontal.status)
print(tdc_vertical.status)
print(tdc_vertical.homeparams_)

start_position_x = config['start_position_x']
start_position_y = config['start_position_y']

step_x = config['step_x']  # mm
step_y = config['step_y']  # mm
length_x = config['length_x'] # mm
length_y = config['length_y'] # mm
n_steps_x = length_x // step_x
n_steps_y = length_y // step_y

assert (length_x % step_x == 0) and (length_y % step_y == 0)

velocity_x = config['velocity_x']
velocity_y = config['velocity_y']
acceleration_x = config['acceleration_x']
acceleration_y = config['acceleration_y']

tdc_horizontal.set_velocity_params(acceleration_to_motor(acceleration_x), velocity_to_motor(velocity_x), )
tdc_vertical.set_velocity_params(acceleration_to_motor(acceleration_y), velocity_to_motor(velocity_y), )
time.sleep(WAIT_TIME)

print(tdc_vertical.status)
print(tdc_horizontal.status)

x_prev = 0
y_prev = 0
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

time.sleep(WAIT_TIME)

x = start_position_x
y = start_position_y
tdc_horizontal.move_absolute(position=position_to_motor(x), now=True, bay=0, channel=0)
tdc_vertical.move_absolute(position=position_to_motor(y), now=True, bay=0, channel=0)
time_of_flight_x = compute_time_of_movement(x, velocity_x, acceleration_x, x0=x_prev)
time_of_flight_y = compute_time_of_movement(y, velocity_y, acceleration_y, x0=y_prev)
time_of_flight = max(time_of_flight_x, time_of_flight_y)
time.sleep(time_of_flight + WAIT_TIME)

tdc_horizontal.close()
tdc_vertical.close()

