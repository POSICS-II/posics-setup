import ctypes
import time

from picosdk.ps6000 import ps6000 as ps
import numpy as np
from picosdk.functions import assert_pico_ok
import json
from posicssetup.utils.utils import voltage_to_trigger_threshold, time_interval_to_timebase
import logging

logger = logging.getLogger(__name__)


class PicoScope6000:

    def __init__(self, config_file, serial):

        with open(config_file) as f:

            self.config = json.load(f)['daq']

        self._handle = ctypes.c_int16()
        self._serial = ctypes.c_char_p(serial.encode('utf-8'))
        self.status = dict()

        self.status['OpenUnit'] = ps.ps6000OpenUnit(ctypes.byref(self._handle), self._serial)
        self.handle = self._handle.value
        self.serial = serial

        self.n_waveforms = self.config['trigger']['n_waveforms']
        self.n_pre_samples = self.config['trigger']['n_pre_samples']
        self.n_post_samples = self.config['trigger']['n_post_samples']
        self.n_samples = self.n_pre_samples + self.n_post_samples
        self.delta_t = self.config['trigger']['delta_t']
        self.timebase = time_interval_to_timebase(self.delta_t)
        self.trigger_threshold = voltage_to_trigger_threshold(self.config['trigger']['threshold'])
        self.trigger_direction = self.config['trigger']['direction']
        self.trigger_delay = self.config['trigger']['delay']
        self.trigger_source = self.config['trigger']['source']

        self.n_channels = self._setup_channels()

        self._data = (((ctypes.c_int16 * self.n_samples) * self.n_channels) * self.n_waveforms)()
        self.times = np.linspace(0, stop=self.n_samples * self.delta_t, num=self.n_samples) - self.trigger_delay

    def __del__(self):

        self.status['Stop'] = ps.ps6000Stop(self._handle)
        self.status['CloseUnit'] = ps.ps6000CloseUnit(self._handle)

    def __str__(self):

        return str(self.status)

    def _setup_channels(self):

        if self.config['trigger']['serial_1'] == self.serial:

            self.channels = [(1, True, "A"), (2, True, "B"), (3, True, "C"), (4, True, "D")]

        elif self.config['trigger']['serial_2'] == self.serial:

            self.channels = [(5, True, "A"), (6, True, "B"), (7, True, "C"), (8, True, "D")]

        n_channels = 0

        for i, (channel_id, _, _) in enumerate(self.channels):

            config = self.config['channel'][str(channel_id)]
            channel = ps.PS6000_CHANNEL['PS6000_CHANNEL_' + config['name']]
            enable = int(config['enable'])
            coupling = ps.PS6000_COUPLING['PS6000_' + config['coupling']]
            voltage_range = ps.PS6000_RANGE['PS6000_' + config['range']]
            offset = config['offset']
            bandwidth = ps.PS6000_BANDWIDTH_LIMITER['PS6000_' + config['bandwidth']]

            self.status['SetChannel_' + str(channel_id)] = ps.ps6000SetChannel(self._handle,
                                                                          channel,
                                                                          enable,
                                                                          coupling,
                                                                          voltage_range,
                                                                          offset,
                                                                          bandwidth)
            self.channels[i] = (self.channels[i][0], bool(enable), config["name"])
            if bool(enable):
                n_channels += 1

        return n_channels

    def _setup_trigger(self):

        enable = True
        source = ps.PS6000_CHANNEL['PS6000_' + self.trigger_source]
        threshold = self.trigger_threshold
        direction = ps.PS6000_THRESHOLD_DIRECTION['PS6000_' + self.trigger_direction]
        delay = self.trigger_delay

        self.status['SetSimpleTrigger'] = ps.ps6000SetSimpleTrigger(self._handle, enable, source, threshold, direction,
                                                                    delay, 0)

        self.status['MemorySegments'] = ps.ps6000MemorySegments(self._handle, self.n_waveforms, None)
        self.status['SetNoOfCaptures'] = ps.ps6000SetNoOfCaptures(self._handle, self.n_waveforms)

        oversampling = 0
        self.status['RunBlock'] = ps.ps6000RunBlock(self._handle, self.n_pre_samples,
                                                    self.n_post_samples, self.timebase,
                                                    oversampling, None, 0, None, None)

        logger.info("Trigger ready for oscilloscope {} ({})".format(self.handle, self.serial))

    def _setup_data(self):

        for segment in range(self.n_waveforms):
            for channel_id, enable, channel_name in self.channels:

                if enable:

                    channel = ps.PS6000_CHANNEL['PS6000_CHANNEL_' + channel_name]
                    self.status['SetDataBuffersBulk_{}_{}'.format(segment, channel_name)] = ps.ps6000SetDataBuffersBulk(
                        self._handle, channel, ctypes.byref(self._data[segment][channel]), None, self.n_samples, segment, 0)
        logger.info("Data buffer ready for oscilloscope {} ({})".format(self.handle, self.serial))

    def check_status(self):

        for key, val in self.status.items():

            logger.debug("Checking callback of function ps6000{}()".format(key))
            assert_pico_ok(val)

    def read_data(self):

        self.check_status()

        ready = ctypes.c_int16(0)
        check = ctypes.c_int16(0)
        while ready.value == check.value:
            self.status["IsReady"] = ps.ps6000IsReady(self._handle, ctypes.byref(ready))
            time.sleep(0.1)

        cmaxSamples = ctypes.c_int32(self.n_samples)
        self.status["GetValuesBulk"] = ps.ps6000GetValuesBulk(self._handle, ctypes.byref(cmaxSamples), 0,
                                                           self.n_waveforms - 1, 0, 0, None)

        data = np.ctypeslib.as_array(self._data)

        return data
