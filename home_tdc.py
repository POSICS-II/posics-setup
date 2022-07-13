import logging
from posicssetup.instruments.linear_stage import LinearStageTDC001

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s:%(message)s')
config_file = 'config.json'

stage_vertical = LinearStageTDC001(config_file=config_file, name='vertical')
stage_horizontal = LinearStageTDC001(config_file=config_file, name='horizontal')
stage_vertical.home()
stage_horizontal.home()





