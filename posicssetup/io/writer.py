import h5py
import json
import logging
import numpy as np
import atexit

logger = logging.getLogger(__name__)


class HDF5FileWriter:

    def __init__(self, config_file: str, basename: str):

        with open(config_file, 'r') as f:

            self.config = json.load(f)['writer']

        basename = basename
        self.output_file = basename + '.h5'
        self.compression = self.config['compression']
        self.compression_opts = self.config['compression_opts']

        self._file = h5py.File(self.output_file, 'x')
        self._file.create_group('waveforms')
        self._file.create_group('trigger')
        atexit.register(self.close)

    def close(self):

        self._file.close()

    def write_data(self, data: np.ndarray, name: str, group='waveforms'):

        logger.info('Writing dataset {}/{} (shape={}) to {}'.format(group, name, data.shape, self.output_file))
        self._file[group].create_dataset(name, data=data, compression=self.compression,
                                               compression_opts=self.compression_opts)


