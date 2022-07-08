from posicssetup.instruments.linear_stage import LinearStageTDC001

config_file = 'config.json'

stage_vertical = LinearStageTDC001(config_file=config_file, name='vertical')
stage_horizontal = LinearStageTDC001(config_file=config_file, name='horizontal')

y_position = 20.32
x_position = 27.09

stage_vertical.move_to(x_position)
stage_horizontal.move_to(y_position)





