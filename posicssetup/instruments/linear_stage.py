from thorlabs_apt_device.devices.tdc001 import TDC001
from posicssetup.utils.utils import position_to_motor, velocity_to_motor, acceleration_to_motor, compute_time_of_movement
import time
import logging
import json
import atexit

logger = logging.getLogger(__name__)

TIME_SLEEP = 1


class LinearStageTDC001:

    def __init__(self, config_file: str, name: str):

        self.MAX_POSITION = 50  # mm
        self.name = name

        with open(config_file, 'r') as f:
            self.config = json.load(f)['stage'][self.name]

        self.serial = self.config['serial']
        self.center = self.config['center']
        self.step = self.config['step']
        self.length = self.config['length']
        self.n_steps = self.length // self.step + 1
        assert self.length % self.step == 0
        self.velocity = self.config['velocity']
        self.acceleration = self.config['acceleration']
        self.velocity_home = self.config['velocity_home']
        self.offset_home = float(self.config['offset_home'])
        self._resource = TDC001(serial_port=self.serial, home=False)
        time.sleep(TIME_SLEEP)
        self.set_velocity()
        atexit.register(self.close)

    def __str__(self):

        return str(self._resource.status)

    def close(self):

        self._resource.close()

    def set_velocity(self, acceleration: float = None, velocity: float = None):

        self.acceleration = self.acceleration if acceleration is None else acceleration
        self.velocity = self.velocity if velocity is None else velocity

        logger.info("Setting translation stage {} ({}) velocity {:.2f} mm/s and acceleration {:.2f} mm/s^2".format(
            self.name, self.serial, self.velocity, self.acceleration
        ))
        self._resource.set_velocity_params(acceleration_to_motor(self.acceleration), velocity_to_motor(self.velocity))
        time.sleep(TIME_SLEEP)

    def move_to(self, position: float, previous_position: float = None):

        if previous_position is None:
            distance = max(abs(self.MAX_POSITION - position), abs(position))
            duration = compute_time_of_movement(distance, self.velocity, self.acceleration, x0=0)

        else:
            duration = compute_time_of_movement(position, self.velocity, self.acceleration, x0=previous_position)

        logger.info("Moving translation stage {} ({}) to position {:.4f} mm\t Please wait {:.2f} seconds".format(
            self.name, self.serial, position, duration))
        self._resource.move_absolute(position=position_to_motor(position), now=True, bay=0, channel=0)
        time.sleep(duration + TIME_SLEEP)

    def home(self):

        self._resource.set_home_params(velocity_to_motor(self.velocity_home),
                                       offset_distance=position_to_motor(self.offset_home))
        time.sleep(TIME_SLEEP)
        duration = compute_time_of_movement(self.MAX_POSITION, self.velocity_home, 0.1, 0)
        duration += compute_time_of_movement(self.offset_home, self.velocity_home, 0.1, 0)
        logger.info("Moving translation stage {} ({}) to home with offset {:.4f} mm".format(self.name,
                                                                                           self.serial,
                                                                                           self.offset_home))
        self._resource.home()
        time.sleep(duration + TIME_SLEEP)
