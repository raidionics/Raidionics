from __future__ import division
import os
import time
import datetime
import calendar
import numpy as np
import subprocess
import shutil
import zipfile
import gzip
from dipy.align.reslice import reslice
import ants
from diagnosis.src.Processing.brain_processing import *


class ANTsRegistration:
    """

    """
    def __init__(self):
        self.ants_reg_dir = ResourcesConfiguration.getInstance().ants_reg_dir
        self.ants_apply_dir = ResourcesConfiguration.getInstance().ants_apply_dir
        self.registration_folder = os.path.join(ResourcesConfiguration.getInstance().output_folder, 'registration/')
        os.makedirs(self.registration_folder, exist_ok=True)
        self.transform_names = []
        self.inverse_transform_names = []
        self.backend = 'python'  # cpp, python

    def clean(self):
        shutil.copyfile(src=os.path.join(self.registration_folder, 'Warped.nii.gz'),
                        dst=os.path.join(ResourcesConfiguration.getInstance().output_folder, 'input_to_mni.nii.gz'))
        shutil.copyfile(src=os.path.join(self.registration_folder, 'input_tumor_mask_reg_atlas.nii.gz'),
                        dst=os.path.join(ResourcesConfiguration.getInstance().output_folder, 'input_tumor_to_mni.nii.gz'))
        shutil.copyfile(src=os.path.join(self.registration_folder, os.path.basename(ResourcesConfiguration.getInstance().neuro_mni_atlas_lobes_mask_filepath).split('.')[0] + '_reg_input.nii.gz'),
                        dst=os.path.join(ResourcesConfiguration.getInstance().output_folder, 'mni_lobes_to_input.nii.gz'))
        if not ResourcesConfiguration.getInstance().diagnosis_full_trace:
            if os.path.exists(self.registration_folder):
                shutil.rmtree(self.registration_folder)

    def compute_registration(self, moving, fixed, registration_method):
        if self.backend == 'python':
            self.compute_registration_python(moving, fixed, registration_method)
        elif self.backend == 'cpp':
            self.compute_registration_cpp(moving, fixed, registration_method)

    def compute_registration_cpp(self, moving, fixed, registration_method):
        print("STARTING REGISTRATION FOR PATIENT.")

        if registration_method == 'sq':
            script_path = os.path.join(self.ants_reg_dir, 'antsRegistrationSyNQuick.sh')
            registration_method = 's'
        else:
            script_path = os.path.join(self.ants_reg_dir, 'antsRegistrationSyN.sh')

        try:
            subprocess.call(["{script}".format(script=script_path),
                             '-d{dim}'.format(dim=3),
                             '-f{fixed}'.format(fixed=fixed),
                             '-m{moving}'.format(moving=moving),
                             '-o{output}'.format(output=self.registration_folder),
                             '-t{trans}'.format(trans=registration_method),
                             '-n{cores}'.format(cores=8),
                             ])

            if registration_method == 's':
                self.transform_names = ['1Warp.nii.gz', '0GenericAffine.mat']
                self.inverse_transform_names = ['1InverseWarp.nii.gz', '0GenericAffine.mat']

            os.rename(src=os.path.join(self.registration_folder, 'Warped.nii.gz'),
                      dst=os.path.join(self.registration_folder, 'input_volume_to_MNI.nii.gz'))
        except Exception as e:
            print('Exception caught during registration. Error message: {}'.format(e))

    def compute_registration_python(self, moving, fixed, registration_method):
        print("STARTING REGISTRATION FOR PATIENT.")

        moving_ants = ants.image_read(moving, dimension=3)
        fixed_ants = ants.image_read(fixed, dimension=3)
        try:
            self.reg_transform = ants.registration(fixed_ants, moving_ants, 'antsRegistrationSyNQuick[s]')
            warped_input = ants.apply_transforms(fixed=fixed_ants,
                                                  moving=moving_ants,
                                                  transformlist=self.reg_transform['fwdtransforms'],
                                                  interpolator='linear',
                                                  whichtoinvert=[False, False])
            warped_input_filename = os.path.join(self.registration_folder, 'input_volume_to_MNI.nii.gz')
            ants.image_write(warped_input, warped_input_filename)
        except Exception as e:
            print('Exception caught during registration. Error message: {}'.format(e))

    def apply_registration_transform(self, moving, fixed, interpolation='nearestNeighbor'):
        if self.backend == 'python':
            self.apply_registration_transform_python(moving, fixed, interpolation)
        elif self.backend == 'cpp':
            self.apply_registration_transform_cpp(moving, fixed, interpolation)

    def apply_registration_transform_python(self, moving, fixed, interpolation='nearestNeighbor'):
        moving_ants = ants.image_read(moving, dimension=3)
        fixed_ants = ants.image_read(fixed, dimension=3)
        try:
            warped_input = ants.apply_transforms(fixed=fixed_ants,
                                                 moving=moving_ants,
                                                 transformlist=self.reg_transform['fwdtransforms'],
                                                 interpolator=interpolation,
                                                 whichtoinvert=[False, False])
            warped_input_filename = os.path.join(self.registration_folder, 'input_segmentation_to_MNI.nii.gz')
            ants.image_write(warped_input, warped_input_filename)
        except Exception as e:
            print('Exception caught during applying registration transform. Error message: {}'.format(e))

    def apply_registration_transform_cpp(self, moving, fixed, interpolation='NearestNeighbor'):
        """
        Apply a registration transform onto the corresponding moving image.
        """
        optimization_method = 'Linear' if interpolation == 'linear' else 'NearestNeighbor'
        print("Apply registration transform to input volume.")
        script_path = os.path.join(self.ants_apply_dir, 'antsApplyTransforms')

        transform_filenames = [os.path.join(self.registration_folder, x) for x in self.transform_names]
        moving_registered_filename = os.path.join(self.registration_folder, 'input_segmentation_to_MNI.nii.gz')  #os.path.join(self.registration_folder, os.path.basename(moving).split('.')[0] + '_reg_atlas.nii.gz')

        if len(transform_filenames) == 4:
            args = ("{script}".format(script=script_path),
                    "-d", "3",
                    '-r', '{fixed}'.format(fixed=fixed),
                    '-i', '{moving}'.format(moving=moving),
                    '-t', '{transform}'.format(transform=transform_filenames[0]),
                    '-t', '{transform}'.format(transform=transform_filenames[1]),
                    '-t', '{transform}'.format(transform=transform_filenames[2]),
                    '-t', '{transform}'.format(transform=transform_filenames[3]),
                    '-o', '{output}'.format(output=moving_registered_filename),
                    '-n', '{type}'.format(type=optimization_method))
        elif len(transform_filenames) == 2:
            args = ("{script}".format(script=script_path),
                    "-d", "3",
                    '-r', '{fixed}'.format(fixed=fixed),
                    '-i', '{moving}'.format(moving=moving),
                    '-t', '{transform}'.format(transform=transform_filenames[0]),
                    '-t', '{transform}'.format(transform=transform_filenames[1]),
                    '-o', '{output}'.format(output=moving_registered_filename),
                    '-n', '{type}'.format(type=optimization_method))
        elif len(transform_filenames) == 1:
            args = ("{script}".format(script=script_path),
                    "-d", "3",
                    '-r', '{fixed}'.format(fixed=fixed),
                    '-i', '{moving}'.format(moving=moving),
                    '-t', '{transform}'.format(transform=transform_filenames[0]),
                    '-o', '{output}'.format(output=moving_registered_filename),
                    '-n', '{type}'.format(type=optimization_method))
        elif len(transform_filenames) == 0:
            raise ValueError('List of transforms is empty.')

        # Or just:
        # args = "bin/bar -c somefile.xml -d text.txt -r aString -f anotherString".split()
        try:
            popen = subprocess.Popen(args, stdout=subprocess.PIPE)
            popen.wait()
            output = popen.stdout.read()
        except Exception as e:
            print('Failed to apply transforms on input image with {}'.format(e))

    def apply_registration_inverse_transform_python(self, moving, fixed, interpolation='nearestNeighbor'):
        moving_ants = ants.image_read(moving, dimension=3)
        fixed_ants = ants.image_read(fixed, dimension=3)
        try:
            warped_input = ants.apply_transforms(fixed=fixed_ants,
                                                 moving=moving_ants,
                                                 transformlist=self.reg_transform['invtransforms'],
                                                 interpolator=interpolation,
                                                 whichtoinvert=[True, False])
            warped_input_filename = os.path.join(self.registration_folder, 'input_anatomical_regions.nii.gz')
            ants.image_write(warped_input, warped_input_filename)
        except Exception as e:
            print('Exception caught during applying registration inverse transform. Error message: {}'.format(e))

    def apply_registration_transform_labels(self, moving, fixed):
        """
        Apply a registration transform onto the corresponding moving labels.
        """
        optimization_method = 'NearestNeighbor'
        print("Apply registration transform to input volume annotation.")
        script_path = os.path.join(self.ants_apply_dir, 'antsApplyTransforms')

        transform_filenames = [os.path.join(self.registration_folder, x) for x in self.transform_names]
        moving_registered_filename = os.path.join(self.registration_folder,
                                                  os.path.basename(moving).split('.')[0] + '_reg_atlas.nii.gz')

        if len(transform_filenames) == 4:
            args = ("{script}".format(script=script_path),
                    "-d", "3",
                    '-r', '{fixed}'.format(fixed=fixed),
                    '-i', '{moving}'.format(moving=moving),
                    '-t', '{transform}'.format(transform=transform_filenames[0]),
                    '-t', '{transform}'.format(transform=transform_filenames[1]),
                    '-t', '{transform}'.format(transform=transform_filenames[2]),
                    '-t', '{transform}'.format(transform=transform_filenames[3]),
                    '-o', '{output}'.format(output=moving_registered_filename),
                    '-n', '{type}'.format(type=optimization_method))
        elif len(transform_filenames) == 2:
            args = ("{script}".format(script=script_path),
                    "-d", "3",
                    '-r', '{fixed}'.format(fixed=fixed),
                    '-i', '{moving}'.format(moving=moving),
                    '-t', '{transform}'.format(transform=transform_filenames[0]),
                    '-t', '{transform}'.format(transform=transform_filenames[1]),
                    '-o', '{output}'.format(output=moving_registered_filename),
                    '-n', '{type}'.format(type=optimization_method))
        elif len(transform_filenames) == 1:
            args = ("{script}".format(script=script_path),
                    "-d", "3",
                    '-r', '{fixed}'.format(fixed=fixed),
                    '-i', '{moving}'.format(moving=moving),
                    '-t', '{transform}'.format(transform=transform_filenames[0]),
                    '-o', '{output}'.format(output=moving_registered_filename),
                    '-n', '{type}'.format(type=optimization_method))
        elif len(transform_filenames) == 0:
            raise ValueError('List of transforms is empty.')

        # Or just:
        # args = "bin/bar -c somefile.xml -d text.txt -r aString -f anotherString".split()
        try:
            popen = subprocess.Popen(args, stdout=subprocess.PIPE)
            popen.wait()
            output = popen.stdout.read()
        except Exception as e:
            print('Failed to apply transforms on input image with {}'.format(e))

    def apply_registration_inverse_transform(self, moving, fixed, interpolation='nearestNeighbor'):
        if self.backend == 'python':
            self.apply_registration_inverse_transform_python(moving, fixed, interpolation)
        elif self.backend == 'cpp':
            self.apply_registration_inverse_transform_cpp(moving, fixed, interpolation)

    def apply_registration_inverse_transform_cpp(self, moving, fixed, interpolation='NearestNeighbor'):
        """
        Apply an inverse registration transform onto the corresponding moving labels.
        """
        optimization_method = 'NearestNeighbor' if interpolation == 'nearestNeighbor' else 'Linear'
        print("Apply registration transform to input volume annotation.")
        script_path = os.path.join(self.ants_apply_dir, 'antsApplyTransforms')

        transform_filenames = [os.path.join(self.registration_folder, x) for x in self.inverse_transform_names]
        moving_registered_filename = os.path.join(self.registration_folder, 'input_anatomical_regions.nii.gz') #os.path.join(self.registration_folder, os.path.basename(moving).split('.')[0] + '_reg_input.nii.gz')

        if len(transform_filenames) == 4:  # Combined case?
            args = ("{script}".format(script=script_path),
                    "-d", "3",
                    '-r', '{fixed}'.format(fixed=fixed),
                    '-i', '{moving}'.format(moving=moving),
                    '-t', '{transform}'.format(transform=transform_filenames[0]),
                    '-t', '[{transform}, 1]'.format(transform=transform_filenames[1]),
                    '-t', '{transform}'.format(transform=transform_filenames[2]),
                    '-t', '[{transform}, 1]'.format(transform=transform_filenames[3]),
                    '-o', '{output}'.format(output=moving_registered_filename),
                    '-n', '{type}'.format(type=optimization_method))
        elif len(transform_filenames) == 2:  # SyN case with a .mat file and a .nii.gz file
            args = ("{script}".format(script=script_path),
                    "-d", "3",
                    '-r', '{fixed}'.format(fixed=fixed),
                    '-i', '{moving}'.format(moving=moving),
                    '-t', '{transform}'.format(transform=transform_filenames[0]),
                    '-t', '[{transform}, 1]'.format(transform=transform_filenames[1]),
                    '-o', '{output}'.format(output=moving_registered_filename),
                    '-n', '{type}'.format(type=optimization_method))
        elif len(transform_filenames) == 1:  # Rigid case with only an .mat file
            args = ("{script}".format(script=script_path),
                    "-d", "3",
                    '-r', '{fixed}'.format(fixed=fixed),
                    '-i', '{moving}'.format(moving=moving),
                    '-t', '[{transform}, 1]'.format(transform=transform_filenames[0]),
                    '-o', '{output}'.format(output=moving_registered_filename),
                    '-n', '{type}'.format(type=optimization_method))
        elif len(transform_filenames) == 0:
            raise ValueError('List of transforms is empty.')

        # Or just:
        # args = "bin/bar -c somefile.xml -d text.txt -r aString -f anotherString".split()
        try:
            popen = subprocess.Popen(args, stdout=subprocess.PIPE)
            popen.wait()
            output = popen.stdout.read()
        except Exception as e:
            print('Failed to apply inverse transforms on input image with {}'.format(e))