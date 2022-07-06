#
# Copyright (C) 2018-2022 Pico Technology Ltd. See LICENSE file for terms.
#
# ps6000 RAPID BLOCK MODE EXAMPLE
# This example opens a 6000 driver device, sets up one channel and a trigger then collects 10 block of data in rapid succession.
# This data is then plotted as mV against time in ns.

import ctypes
from picosdk.ps6000 import ps6000 as ps
import numpy as np
from picosdk.functions import adc2mV, assert_pico_ok
import json
import matplotlib.pyplot as plt
from linearstage.utils import voltage_to_trigger_threshold, time_interval_to_timebase


with open('config.json', 'r') as f:

    data = json.load(f)
    config = data['daq']

status = {}


serial_1 = ctypes.c_char_p(config['trigger']['serial_1'].encode('utf-8'))
serial_2 = ctypes.c_char_p(config['trigger']['serial_2'].encode('utf-8'))
handle_1 = ctypes.c_int16()
handle_2 = ctypes.c_int16()
handles = [handle_1, handle_2]
serials = [serial_1, serial_2]

status['OpenUnit_1'] = ps.ps6000OpenUnit(ctypes.byref(handle_1), serial_1)
status['OpenUnit_2'] = ps.ps6000OpenUnit(ctypes.byref(handle_2), serial_2)
assert_pico_ok(status['OpenUnit_1'])
assert_pico_ok(status['OpenUnit_2'])

n_waveforms = config['trigger']['n_waveforms']
n_channels = 0
n_pre_samples = config['trigger']['n_pre_samples']
n_post_samples = config['trigger']['n_post_samples']
n_samples = n_pre_samples + n_post_samples
timebase = time_interval_to_timebase(config['trigger']['delta_t'])

couple = []

for channel_number, channel_config in config['channel'].items():

    handle = handles[channel_config['daq'] - 1]
    channel = ps.PS6000_CHANNEL['PS6000_CHANNEL_' + channel_config['name']]
    enable = channel_config['enable']
    coupling = ps.PS6000_COUPLING['PS6000_' + channel_config['coupling']]
    voltage_range = ps.PS6000_RANGE['PS6000_' + channel_config['range']]
    offset = channel_config['offset']
    bandwidth = ps.PS6000_BANDWIDTH_LIMITER['PS6000_' + channel_config['bandwidth']]

    status['SetChannel_' + channel_number] = ps.ps6000SetChannel(handle, channel, int(enable), coupling, voltage_range,
                                                                 offset, bandwidth)

    assert_pico_ok(status['SetChannel_' + channel_number])

    if enable:
        couple.append((channel_number, handle, channel, channel_config['daq']))
        n_channels += 1

print(status)

waveforms = [[(ctypes.c_int16 * n_samples)() for _ in range(n_waveforms)] for _ in range(n_channels)]

for handle in handles:

    trigger_config = config['trigger']

    enable = True
    source = ps.PS6000_CHANNEL['PS6000_' + trigger_config['source']]
    threshold = voltage_to_trigger_threshold(trigger_config['threshold'])
    direction = ps.PS6000_THRESHOLD_DIRECTION['PS6000_' + trigger_config['direction']]
    delay = trigger_config['delay']

    status['SetSimpleTrigger_' + str(handle.value)] = ps.ps6000SetSimpleTrigger(handle,
                                                                             enable,
                                                                             source,
                                                                             threshold,
                                                                             direction,
                                                                             delay,
                                                                             0)
    assert_pico_ok(status['SetSimpleTrigger_' + str(handle.value)])

    pParameter = ctypes.c_void_p()
    oversampling = 0
    status['MemorySegments_' + str(handle.value)] = ps.ps6000MemorySegments(handle, n_waveforms, None)
    status['SetNoOfCaptures_' + str(handle.value)] = ps.ps6000SetNoOfCaptures(handle, n_waveforms)
    status['RunBlock_' + str(handle.value)] = ps.ps6000RunBlock(handle, n_pre_samples, n_post_samples,
                                                             timebase, oversampling, None, 0, None, None)

    for segment in range(n_waveforms):

        for j in range(n_channels):

            waveform = waveforms[j][segment]
            channel = couple[j][2]
            status['SetDataBuffersBulk_{}_{}'.format(couple[j][0], segment)] = ps.ps6000SetDataBuffersBulk(
                handle, channel, ctypes.byref(waveform), None, n_samples, segment, 0)

    ready = ctypes.c_int16(0)
    check = ctypes.c_int16(0)
    while ready.value == check.value:
        status["IsReady_{}".format(str(handle.value))] = ps.ps6000IsReady(handle, ctypes.byref(ready))
        print(handle.value)


cmaxSamples_1 = ctypes.c_int32(n_samples)
cmaxSamples_2 = ctypes.c_int32(n_samples)
status["GetValuesBulk_1"] = ps.ps6000GetValuesBulk(handle_1, ctypes.byref(cmaxSamples_1), 0, n_waveforms - 1, 0, 0, None)
status["GetValuesBulk_2"] = ps.ps6000GetValuesBulk(handle_2, ctypes.byref(cmaxSamples_2), 0, n_waveforms - 1, 0, 0, None)


for i in range(n_waveforms):
    data_1 = np.ctypeslib.as_array(waveforms[0][i])
    data_2 = np.ctypeslib.as_array(waveforms[1][i])
    data_3 = np.ctypeslib.as_array(waveforms[2][i])
    data_4 = np.ctypeslib.as_array(waveforms[3][i])
    data_5 = np.ctypeslib.as_array(waveforms[4][i])
    data_6 = np.ctypeslib.as_array(waveforms[5][i])

    plt.figure()
    plt.plot(data_1, label='channel_1')
    plt.plot(data_2, label='channel_2')
    plt.plot(data_3, label='channel_3')
    plt.plot(data_4, label='channel_4')
    plt.plot(data_5, label='channel_5')
    plt.plot(data_6, label='channel_6')
    plt.legend(loc='best')
    plt.savefig('test_{}.png'.format(i))

for key, val in status.items():
    assert_pico_ok(val)

for handle in handles:

    ps.ps6000Stop(handle)
    ps.ps6000CloseUnit(handle)


print(status)
exit()

# Setting the number of sample to be collected
preTriggerSamples = 400
postTriggerSamples = 400
maxsamples = preTriggerSamples + postTriggerSamples

# Gets timebase innfomation
# Warning: When using this example it may not be possible to access all Timebases as all channels are enabled by default when opening the scope.
# To access these Timebases, set any unused analogue channels to off.
# Handle = chandle
# Timebase = 2 = timebase
# Nosample = maxsamples
# TimeIntervalNanoseconds = ctypes.byref(timeIntervalns)
# MaxSamples = ctypes.byref(returnedMaxSamples)
# Segement index = 0
timebase = 2
timeIntervalns = ctypes.c_float()
returnedMaxSamples = ctypes.c_int16()
status["GetTimebase"] = ps.ps6000GetTimebase2(handle, timebase, maxsamples, ctypes.byref(timeIntervalns), 1, ctypes.byref(returnedMaxSamples), 0)
assert_pico_ok(status["GetTimebase"])
print(status)

# Creates a overlow location for data
overflow = ctypes.c_int16()
# Creates converted types maxsamples
cmaxSamples = ctypes.c_int32(maxsamples)

# Handle = Chandle
# nSegments = 10
# nMaxSamples = ctypes.byref(cmaxSamples)

status["MemorySegments"] = ps.ps6000MemorySegments(handle, 10, ctypes.byref(cmaxSamples))
assert_pico_ok(status["MemorySegments"])

# sets number of captures
status["SetNoOfCaptures"] = ps.ps6000SetNoOfCaptures(handle, 10)
assert_pico_ok(status["SetNoOfCaptures"])

# Starts the block capture
# Handle = chandle
# Number of prTriggerSamples
# Number of postTriggerSamples
# Timebase = 2 = 4ns (see Programmer's guide for more information on timebases)
# time indisposed ms = None (This is not needed within the example)
# Segment index = 0
# LpRead = None
# pParameter = None
status["runblock"] = ps.ps6000RunBlock(handle, preTriggerSamples, postTriggerSamples, timebase, 1, None, 0, None, None)
assert_pico_ok(status["runblock"])
print(status)

# Create buffers ready for assigning pointers for data collection
bufferAMax = (ctypes.c_int16 * maxsamples)()
bufferAMin = (ctypes.c_int16 * maxsamples)() # used for downsampling which isn't in the scope of this example

# Setting the data buffer location for data collection from channel A
# Handle = Chandle
# source = ps6000_channel_A = 0
# Buffer max = ctypes.byref(bufferAMax)
# Buffer min = ctypes.byref(bufferAMin)
# Buffer length = maxsamples
# Segment index = 0
# Ratio mode = ps6000_Ratio_Mode_None = 0
status["SetDataBuffersBulk"] = ps.ps6000SetDataBuffersBulk(handle, 0, ctypes.byref(bufferAMax), ctypes.byref(bufferAMin), maxsamples, 0, 0)
assert_pico_ok(status["SetDataBuffersBulk"])
print(status)

# Create buffers ready for assigning pointers for data collection
bufferAMax1 = (ctypes.c_int16 * maxsamples)()
bufferAMin1 = (ctypes.c_int16 * maxsamples)() # used for downsampling which isn't in the scope of this example

# Setting the data buffer location for data collection from channel A
# Handle = Chandle
# source = ps6000_channel_A = 0
# Buffer max = ctypes.byref(bufferAMax)
# Buffer min = ctypes.byref(bufferAMin)
# Buffer length = maxsamples
# Segment index = 1
# Ratio mode = ps6000_Ratio_Mode_None = 0
status["SetDataBuffersBulk"] = ps.ps6000SetDataBuffersBulk(handle, 0, ctypes.byref(bufferAMax1), ctypes.byref(bufferAMin1), maxsamples, 1, 0)
assert_pico_ok(status["SetDataBuffersBulk"])

# Create buffers ready for assigning pointers for data collection
bufferAMax2 = (ctypes.c_int16 * maxsamples)()
bufferAMin2 = (ctypes.c_int16 * maxsamples)() # used for downsampling which isn't in the scope of this example

# Setting the data buffer location for data collection from channel A
# Handle = Chandle
# source = ps6000_channel_A = 0
# Buffer max = ctypes.byref(bufferAMax)
# Buffer min = ctypes.byref(bufferAMin)
# Buffer length = maxsamples
# Segment index = 2
# Ratio mode = ps6000_Ratio_Mode_None = 0
status["SetDataBuffersBulk"] = ps.ps6000SetDataBuffersBulk(handle, 0, ctypes.byref(bufferAMax2), ctypes.byref(bufferAMin2), maxsamples, 2, 0)
assert_pico_ok(status["SetDataBuffersBulk"])


# Create buffers ready for assigning pointers for data collection
bufferAMax3 = (ctypes.c_int16 * maxsamples)()
bufferAMin3 = (ctypes.c_int16 * maxsamples)() # used for downsampling which isn't in the scope of this example

# Setting the data buffer location for data collection from channel A
# Handle = Chandle
# source = ps6000_channel_A = 0
# Buffer max = ctypes.byref(bufferAMax)
# Buffer min = ctypes.byref(bufferAMin)
# Buffer length = maxsamples
# Segment index = 3
# Ratio mode = ps6000_Ratio_Mode_None = 0
status["SetDataBuffersBulk"] = ps.ps6000SetDataBuffersBulk(handle, 0, ctypes.byref(bufferAMax3), ctypes.byref(bufferAMin3), maxsamples, 3, 0)
assert_pico_ok(status["SetDataBuffersBulk"])

# Create buffers ready for assigning pointers for data collection
bufferAMax4 = (ctypes.c_int16 * maxsamples)()
bufferAMin4 = (ctypes.c_int16 * maxsamples)() # used for downsampling which isn't in the scope of this example

# Setting the data buffer location for data collection from channel A
# Handle = Chandle
# source = ps6000_channel_A = 0
# Buffer max = ctypes.byref(bufferAMax)
# Buffer min = ctypes.byref(bufferAMin)
# Buffer length = maxsamples
# Segment index = 4
# Ratio mode = ps6000_Ratio_Mode_None = 0
status["SetDataBuffersBulk"] = ps.ps6000SetDataBuffersBulk(handle, 0, ctypes.byref(bufferAMax4), ctypes.byref(bufferAMin4), maxsamples, 4, 0)
assert_pico_ok(status["SetDataBuffersBulk"])

# Create buffers ready for assigning pointers for data collection
bufferAMax5 = (ctypes.c_int16 * maxsamples)()
bufferAMin5 = (ctypes.c_int16 * maxsamples)() # used for downsampling which isn't in the scope of this example

# Setting the data buffer location for data collection from channel A
# Handle = Chandle
# source = ps6000_channel_A = 0
# Buffer max = ctypes.byref(bufferAMax)
# Buffer min = ctypes.byref(bufferAMin)
# Buffer length = maxsamples
# Segment index = 5
# Ratio mode = ps6000_Ratio_Mode_None = 0
status["SetDataBuffersBulk"] = ps.ps6000SetDataBuffersBulk(handle, 0, ctypes.byref(bufferAMax5), ctypes.byref(bufferAMin5), maxsamples, 5, 0)
assert_pico_ok(status["SetDataBuffersBulk"])

# Create buffers ready for assigning pointers for data collection
bufferAMax6 = (ctypes.c_int16 * maxsamples)()
bufferAMin6 = (ctypes.c_int16 * maxsamples)() # used for downsampling which isn't in the scope of this example

# Setting the data buffer location for data collection from channel A
# Handle = Chandle
# source = ps6000_channel_A = 0
# Buffer max = ctypes.byref(bufferAMax)
# Buffer min = ctypes.byref(bufferAMin)
# Buffer length = maxsamples
# Segment index = 6
# Ratio mode = ps6000_Ratio_Mode_None = 0
status["SetDataBuffersBulk"] = ps.ps6000SetDataBuffersBulk(handle, 0, ctypes.byref(bufferAMax6), ctypes.byref(bufferAMin6), maxsamples, 6, 0)
assert_pico_ok(status["SetDataBuffersBulk"])

# Create buffers ready for assigning pointers for data collection
bufferAMax7 = (ctypes.c_int16 * maxsamples)()
bufferAMin7 = (ctypes.c_int16 * maxsamples)() # used for downsampling which isn't in the scope of this example

# Setting the data buffer location for data collection from channel A
# Handle = Chandle
# source = ps6000_channel_A = 0
# Buffer max = ctypes.byref(bufferAMax)
# Buffer min = ctypes.byref(bufferAMin)
# Buffer length = maxsamples
# Segment index = 7
# Ratio mode = ps6000_Ratio_Mode_None = 0
status["SetDataBuffersBulk"] = ps.ps6000SetDataBuffersBulk(handle, 0, ctypes.byref(bufferAMax7), ctypes.byref(bufferAMin7), maxsamples, 7, 0)
assert_pico_ok(status["SetDataBuffersBulk"])

# Create buffers ready for assigning pointers for data collection
bufferAMax8 = (ctypes.c_int16 * maxsamples)()
bufferAMin8 = (ctypes.c_int16 * maxsamples)() # used for downsampling which isn't in the scope of this example

# Setting the data buffer location for data collection from channel A
# Handle = Chandle
# source = ps6000_channel_A = 0
# Buffer max = ctypes.byref(bufferAMax)
# Buffer min = ctypes.byref(bufferAMin)
# Buffer length = maxsamples
# Segment index = 8
# Ratio mode = ps6000_Ratio_Mode_None = 0
status["SetDataBuffersBulk"] = ps.ps6000SetDataBuffersBulk(handle, 0, ctypes.byref(bufferAMax8), ctypes.byref(bufferAMin8), maxsamples, 8, 0)
assert_pico_ok(status["SetDataBuffersBulk"])

# Create buffers ready for assigning pointers for data collection
bufferAMax9 = (ctypes.c_int16 * maxsamples)()
bufferAMin9 = (ctypes.c_int16 * maxsamples)() # used for downsampling which isn't in the scope of this example

# Setting the data buffer location for data collection from channel A
# Handle = Chandle
# source = ps6000_channel_A = 0
# Buffer max = ctypes.byref(bufferAMax)
# Buffer min = ctypes.byref(bufferAMin)
# Buffer length = maxsamples
# Segment index = 9
# Ratio mode = ps6000_Ratio_Mode_None = 0
status["SetDataBuffersBulk"] = ps.ps6000SetDataBuffersBulk(handle, 0, ctypes.byref(bufferAMax9), ctypes.byref(bufferAMin9), maxsamples, 9, 0)
assert_pico_ok(status["SetDataBuffersBulk"])

# Creates a overlow location for data
overflow = (ctypes.c_int16 * 10)()
# Creates converted types maxsamples
cmaxSamples = ctypes.c_int32(maxsamples)

# Checks data collection to finish the capture
ready = ctypes.c_int16(0)
check = ctypes.c_int16(0)
while ready.value == check.value:
    status["isReady"] = ps.ps6000IsReady(handle, ctypes.byref(ready))

# Handle = chandle
# noOfSamples = ctypes.byref(cmaxSamples)
# fromSegmentIndex = 0
# ToSegmentIndex = 9
# DownSampleRatio = 0
# DownSampleRatioMode = 0
# Overflow = ctypes.byref(overflow)

status["GetValuesBulk"] = ps.ps6000GetValuesBulk(handle, ctypes.byref(cmaxSamples), 0, 9, 0, 0, ctypes.byref(overflow))
assert_pico_ok(status["GetValuesBulk"])

# Handle = chandle
# Times = Times = (ctypes.c_int16*10)() = ctypes.byref(Times)
# Timeunits = TimeUnits = ctypes.c_char() = ctypes.byref(TimeUnits)
# Fromsegmentindex = 0
# Tosegementindex = 9
Times = (ctypes.c_int16*10)()
TimeUnits = ctypes.c_char()
status["GetValuesTriggerTimeOffsetBulk"] = ps.ps6000GetValuesTriggerTimeOffsetBulk64(handle, ctypes.byref(Times), ctypes.byref(TimeUnits), 0, 9)
assert_pico_ok(status["GetValuesTriggerTimeOffsetBulk"])

# Finds the max ADC count
maxADC = ctypes.c_int16(32512)

print(np.asarray(overflow, dtype=ctypes.c_short))
# Converts ADC from channel A to mV
print(bufferAMax)
print(np.asarray(bufferAMax, dtype=ctypes.c_short))
adc2mVChAMax = adc2mV(bufferAMax, range_A, maxADC)
print(type(adc2mVChAMax))
print(type(adc2mVChAMax[0]))
# adc2mVChAMax = np.asarray(adc2mVChAMax, dtype=ctypes.c_)
"""adc2mVChAMax1 =  adc2mV(bufferAMax1, chARange, maxADC)
adc2mVChAMax2 =  adc2mV(bufferAMax2, chARange, maxADC)
adc2mVChAMax3 =  adc2mV(bufferAMax3, chARange, maxADC)
adc2mVChAMax4 =  adc2mV(bufferAMax4, chARange, maxADC)
adc2mVChAMax5 =  adc2mV(bufferAMax5, chARange, maxADC)
adc2mVChAMax6 =  adc2mV(bufferAMax6, chARange, maxADC)
adc2mVChAMax7 =  adc2mV(bufferAMax7, chARange, maxADC)
adc2mVChAMax8 =  adc2mV(bufferAMax8, chARange, maxADC)
adc2mVChAMax9 =  adc2mV(bufferAMax9, chARange, maxADC)
"""

# Creates the time data
print('xD')
print(cmaxSamples.value - 1)
print(timeIntervalns.value, cmaxSamples.value)
print(np.linspace(0, 10, 10))
time = np.arange(maxsamples)
print(time)
# time = np.linspace(0., float(cmaxSamples.value -1) * float(timeIntervalns.value), int(cmaxSamples.value),dtype=float)
print(time)
print("lol")
# Plots the data from channel A onto a graph
plt.figure()
print("hello")
plt.plot(time, time)
# plt.plot(time, np.asarray(bufferAMax, dtype=ctypes.c_short))
print("hello")
# plt.plot(time, adc2mVChAMax1[:])
# plt.plot(time, adc2mVChAMax2[:])
# plt.plot(time, adc2mVChAMax3[:])
# plt.plot(time, adc2mVChAMax4[:])
# plt.plot(time, adc2mVChAMax5[:])
# plt.plot(time, adc2mVChAMax6[:])
# plt.plot(time, adc2mVChAMax7[:])
# plt.plot(time, adc2mVChAMax8[:])
 # plt.plot(time, adc2mVChAMax9[:])
print("hello")
plt.xlabel('Time (ns)')
plt.ylabel('Voltage (mV)')
print("hello")
plt.savefig('test.png')

# plt.show()

# Stops the scope
# Handle = chandle
status["stop"] = ps.ps6000Stop(handle)
assert_pico_ok(status["stop"])

# Closes the unit
# Handle = chandle
status["close"] = ps.ps6000CloseUnit(handle)
assert_pico_ok(status["close"])

# Displays the staus returns
print(status)

