import getopt
import os
import sys
import traceback
from segmentation.src.fit import predict
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def main_segmentation(input_filename, output_folder):
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = '-1'
    try:
        predict(input_filename=input_filename, output_path=output_folder, selected_model='MRI_Brain')
    except Exception as e:
        print('{}'.format(traceback.format_exc()))
