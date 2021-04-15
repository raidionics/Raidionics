import getopt
import os
import sys
import traceback
from diagnosis.src.diagnose import *
from diagnosis.src.Utils.configuration_parser import ResourcesConfiguration
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

#-i /home/dbouget/Documents/Code/Public/mri_brain-tumor_segmentation/resources/data/863_MR_T1_pre_1028.nii.gz -o ./Results -m MRI_Meningioma -g -1


def diagnose_main(input_volume_filename, input_segmentation_filename, output_folder):
    env = ResourcesConfiguration.getInstance()
    env.set_environment(output_dir=output_folder)
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = '-1'

    try:
        diagnose(input_filename=input_volume_filename, input_segmentation=input_segmentation_filename)
    except Exception as e:
        print('{}'.format(traceback.format_exc()))
