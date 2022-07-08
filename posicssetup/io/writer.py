import h5py
import json
import logging
import numpy as np

logger = logging.getLogger(__name__)


class HDF5FileWriter:

    def __init__(self, config_file, n_channels, dtype=np.int):

        with open(config_file, 'r') as f:

            self.config = json.load(f)

        self.output_file = self.config['writer']['output_file']

        n_waveforms = self.config['trigger']['n_waveforms']
        n_samples = self.config['trigger']['n_samples']
        self.shape = (n_waveforms, n_channels, n_samples)

        self._file = h5py.File(self.output_file, 'r')
        self._file.create_dataset('waveforms', shape=self.shape, dtype=dtype)

