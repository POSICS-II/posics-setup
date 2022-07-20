from posicssetup.instruments.linear_stage import LinearStageTDC001
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s:%(message)s')

config_file = 'config.json'

stage_vertical = LinearStageTDC001(config_file=config_file, name='vertical')
stage_horizontal = LinearStageTDC001(config_file=config_file, name='horizontal')

x_position = 28.8
y_position = 25.82

stage_horizontal.move_to(x_position)
stage_vertical.move_to(y_position)





