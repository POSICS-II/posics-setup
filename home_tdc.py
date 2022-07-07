from thorlabs_apt_device.devices.tdc001 import TDC001
import time
import logging
import json
from posicssetup.utils.utils import position_to_motor, MAX_RANGE, velocity_to_motor, compute_time_of_movement
from posicssetup.instruments.linear_stage import LinearStageTDC001

config_file = 'config.json'

stage_vertical = LinearStageTDC001(config_file=config_file, name='vertical')
stage_horizontal = LinearStageTDC001(config_file=config_file, name='horizontal')
stage_vertical.home()
stage_horizontal.home()





