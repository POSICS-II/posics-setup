import logging
import math

FACTOR_POSITION = 34554.96
FACTOR_TIME = 2048 / (6 * 1E6)
MAX_RANGE = 50  # mm
MAX_VELOCITY = 2.4  # mm /s
MAX_ACCELERATION = 4.5  # mm /s /s
WAIT_TIME = 1.5  # s

logger = logging.getLogger(__name__)


def voltage_to_adc(voltage, voltage_max, max_value=32512):

    adc = int(voltage / voltage_max * max_value)

    return adc


def voltage_to_trigger_threshold(voltage):

    voltage_max = 1
    voltage_min = -1

    if (voltage <= voltage_max) and (voltage >= voltage_min):

        threshold = voltage_to_adc(voltage, voltage_max)
        return threshold

    else:

        raise ValueError


def time_interval_to_timebase(delta_t):

    if delta_t <= 3.2E-9:

        if (delta_t % 200E-12) != 0:

            raise ValueError

        else:

            timebase = int(math.log2(delta_t/200E-12))
            return timebase

    else:

        raise NotImplementedError


def position_to_motor(x, factor=FACTOR_POSITION):

    if x > MAX_RANGE:

        x = MAX_RANGE

        logger.warning('Input position {} is bigger than maximum position {}'.format(x, MAX_RANGE))

    elif x < 0:

        x = 0

        logger.warning('Input position {} is smaller than 0'.format(x))

    return int(x*factor)


def motor_to_position(x, factor=FACTOR_POSITION):

    return x / factor


def velocity_to_motor(v, factor=FACTOR_POSITION, t=FACTOR_TIME):

    if v > MAX_VELOCITY:

        v = MAX_VELOCITY

    elif v < 0:

        v = 0

    return int(v * t * factor * 65536)


def acceleration_to_motor(a, factor=FACTOR_POSITION, t=FACTOR_TIME):

    if a > MAX_ACCELERATION:

        a = MAX_ACCELERATION

    elif a < 0:

        a = 0

    return int(factor * t**2 * 65536 * a)


def compute_time_of_movement(x, v, a, x0=0):

    t = abs(x - x0)/v + v / a

    return t
