import os
import configparser
from os.path import expanduser
import nibabel as nib
from copy import deepcopy
from nibabel.processing import resample_to_output, resample_from_to
import numpy as np
from scipy.ndimage import rotate


class PatientParameters:
    def __init__(self):
        # Initially, everything is dumped in the software temp place, until a destination is chosen by the user.
        self.output_folder = os.path.join(expanduser("~"), '.neurorads', 'tmp_patient')
        os.makedirs(self.output_folder, exist_ok=True)  # Might have to erase the content of the folder for
        # every new patient, but then must be prompted on screen that it will be erased and removed from viewing within the software

        self.import_raw_data = {}
        self.import_display_data = {}

    def import_data(self, filename):
        """
        Saving the raw file, and preprocessing it to have fixed orientations and uint8 values.
        """
        base_name = os.path.basename(filename).split('.')[0]
        image_nib = nib.load(filename)
        image = image_nib.get_data()[:]

        self.import_raw_data[base_name] = deepcopy(image)
        resampled_input_ni = resample_to_output(image_nib, order=1)
        image_res = resampled_input_ni.get_data()[:]
        min_val = np.min(image_res)
        max_val = np.max(image_res)
        if (max_val - min_val) != 0:
            tmp = (image_res - min_val) / (max_val - min_val)
            image_res = tmp * 255.

        image_res2 = image_res.astype('uint8')
        self.import_display_data[base_name] = deepcopy(image_res2)
