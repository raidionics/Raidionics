import os
import configparser
from os.path import expanduser
import nibabel as nib
from copy import deepcopy
from nibabel.processing import resample_to_output, resample_from_to
import numpy as np
from scipy.ndimage import rotate
import json


class PatientParameters:
    def __init__(self, id):
        self.patient_id = id.replace(" ", '_').strip()
        # Initially, everything is dumped in the software temp place, until a destination is chosen by the user.
        # Should we have a patient-named folder, so that the user only needs to choose the global destination directory
        self.output_folder = os.path.join(expanduser("~"), '.neurorads', 'tmp_patient')
        os.makedirs(self.output_folder, exist_ok=True)  # Might have to erase the content of the folder for
        # every new patient, but then must be prompted on screen that it will be erased and removed from viewing within the software

        self.patient_parameters_project_filename = os.path.join(self.output_folder, self.patient_id + '_scene.neurorads')
        self.patient_parameters_project_json = {}
        self.patient_parameters_project_json['Parameters'] = {}
        self.patient_parameters_project_json['Parameters']['Default'] = {}
        self.patient_parameters_project_json['Parameters']['Default']['Patient name'] = self.patient_id
        self.patient_parameters_project_json['Parameters']['Diagnosis'] = {}
        self.patient_parameters_project_json['Volumes'] = {}
        self.patient_parameters_project_json['Volumes']['Raw'] = {}
        self.patient_parameters_project_json['Volumes']['Display'] = {}

        self.import_raw_data = {}
        self.import_display_data = {}

    def update_id(self, new_id):
        self.patient_id = new_id.replace(" ", '_').strip()
        self.patient_parameters_project_filename = os.path.join(self.output_folder, self.patient_id + '_scene.neurorads')
        self.patient_parameters_project_json['Parameters']['Default']['Patient name'] = self.patient_id

    def import_patient(self, filename):
        self.patient_parameters_project_filename = filename
        self.output_folder = os.path.dirname(self.patient_parameters_project_filename)
        with open(self.patient_parameters_project_filename, 'r') as infile:
            self.patient_parameters_project_json = json.load(infile)

        for disp in list(self.patient_parameters_project_json['Volumes']['Display'].keys()):
            img_nii = nib.load(self.patient_parameters_project_json['Volumes']['Display'][disp])
            img = img_nii.get_data()[:].astype('uint8')
            self.import_display_data[disp] = deepcopy(img)

    def import_data(self, filename):
        """
        Saving the raw file, and preprocessing it to have fixed orientations and uint8 values.
        """
        base_name = os.path.basename(filename).split('.')[0]
        image_nib = nib.load(filename)
        image = image_nib.get_data()[:]

        self.import_raw_data[base_name] = deepcopy(image)
        self.patient_parameters_project_json['Volumes']['Raw'][base_name] = filename

        resampled_input_ni = resample_to_output(image_nib, order=1)
        image_res = resampled_input_ni.get_data()[:]
        min_val = np.min(image_res)
        max_val = np.max(image_res)
        if (max_val - min_val) != 0:
            tmp = (image_res - min_val) / (max_val - min_val)
            image_res = tmp * 255.

        image_res2 = image_res.astype('uint8')
        self.import_display_data[base_name] = deepcopy(image_res2)

    def save_patient(self):
        for i, disp in enumerate(list(self.import_display_data.keys())):
            volume_dump_filename = os.path.join(self.output_folder, disp + '_display.nii.gz')
            self.patient_parameters_project_json['Volumes']['Display'][disp] = volume_dump_filename
            nib.save(nib.Nifti1Image(self.import_display_data[disp],
                                     affine=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]),
                     volume_dump_filename)

        # Saving the json file last, as it must be populated from the previous dumps beforehand
        with open(self.patient_parameters_project_filename, 'w') as outfile:
            json.dump(self.patient_parameters_project_json, outfile)
