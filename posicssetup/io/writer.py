import h5py
import json
import logging
import numpy as np
import atexit

logger = logging.getLogger(__name__)


class HDF5FileWriter:

    def __init__(self, config_file):

        with open(config_file, 'r') as f:

            self.config = json.load(f)['writer']

        self.output_file = self.config['output_file']
        self.compression = self.config['compression']
        self.compression_opts = self.config['compression_opts']

        self._file = h5py.File(self.output_file, 'x')
        self._file.create_group('waveforms')
        atexit.register(self.close)

    def close(self):

        self._file.close()

    def write_data(self, data: np.ndarray, name: str):

        self._file['waveforms'].create_dataset(name, data=data, compression=self.compression,
                                               compression_opts=self.compression_opts)

