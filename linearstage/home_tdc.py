from thorlabs_apt_device.devices.tdc001 import TDC001
import time
import logging
import json
from utils import position_to_motor, MAX_RANGE, velocity_to_motor, compute_time_of_movement


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


velocity_home = config['velocity_home']
velocity_home = velocity_to_motor(velocity_home)

offset_home = config['offset_home']

tdc_horizontal.set_home_params(velocity_to_motor(velocity_home), offset_distance=position_to_motor(offset_home))
tdc_vertical.set_home_params(velocity_to_motor(velocity_home), offset_distance=position_to_motor(offset_home))
time.sleep(WAIT_TIME)

homing_time = compute_time_of_movement(MAX_RANGE, velocity_home, 0.1, x0=0)
homing_time += compute_time_of_movement(offset_home, velocity_home, 0.1, x0=0)

tdc_horizontal.home()
tdc_vertical.home()

time.sleep(WAIT_TIME + homing_time)

# exit()
print(tdc_vertical.status)
print(tdc_horizontal.status)
tdc_horizontal.close()
tdc_vertical.close()

