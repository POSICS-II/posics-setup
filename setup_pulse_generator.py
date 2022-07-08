from posicssetup.instruments.pulse_generator import PulseGeneratorTG5011


inst = PulseGeneratorTG5011(config_file='config.json')

inst.set_main_out(True)
inst.set_synch_out(True)

inst.close()