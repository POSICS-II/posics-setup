from thorlabs_apt_device.devices.tdc001 import TDC001
from utils import position_to_motor, motor_to_position, velocity_to_motor, acceleration_to_motor, compute_time_of_movement, MAX_ACCELERATION, MAX_VELOCITY, MAX_RANGE
import time
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

WAIT_TIME = 1.5  # s

serial_port_1 = '/dev/ttyUSB0'
serial_port_2 = '/dev/ttyUSB1'
serial_port_3 = '/dev/ttyUSB2'
serial_port_4 = '/dev/ttyUSB3'

tdc_vertical = TDC001(serial_port=serial_port_3, home=False)
tdc_horizontal = TDC001(serial_port=serial_port_4, home=False)
time.sleep(WAIT_TIME)
print(tdc_horizontal.status)
print(tdc_vertical.status)
print(tdc_vertical.homeparams_)

position_x = 667669
position_y = 590443
#position_x_mm = [x + offset_x_mm for x in position_x_mm]
#position_y_mm = [y + offset_y_mm for y in position_y_mm]
velocity_y_mm = velocity_x_mm = MAX_VELOCITY / 4  # mm / s
acceleration_y_mm = acceleration_x_mm = MAX_ACCELERATION / 4  # mm / s / s

velocity_x = velocity_to_motor(velocity_x_mm)
velocity_y = velocity_to_motor(velocity_y_mm)

acceleration_x = acceleration_to_motor(acceleration_x_mm)
acceleration_y = acceleration_to_motor(acceleration_y_mm)

tdc_vertical.set_velocity_params(acceleration_y, velocity_y, )
tdc_horizontal.set_velocity_params(acceleration_x, velocity_x, )
time.sleep(WAIT_TIME)

print(tdc_vertical.status)
print(tdc_horizontal.status)
prev_position_x = 0
prev_position_y = 0

x = motor_to_position(position_x)
y = motor_to_position(position_y)
print(x, y)
time_of_flight_x = compute_time_of_movement(MAX_RANGE, velocity_x_mm, acceleration_x_mm, x0=0)
time_of_flight_y = compute_time_of_movement(MAX_RANGE, velocity_y_mm, acceleration_y_mm, x0=0)
time_of_flight = max(time_of_flight_x, time_of_flight_y)

tdc_horizontal.move_absolute(position=position_x, now=True, bay=0, channel=0)
tdc_vertical.move_absolute(position=position_y, now=True, bay=0, channel=0)
time.sleep(time_of_flight + WAIT_TIME)

print(tdc_vertical.status)
print(tdc_horizontal.status)

time.sleep(WAIT_TIME)
tdc_horizontal.close()
tdc_vertical.close()

