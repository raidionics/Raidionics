from diagnosis.src.diagnose import *
from diagnosis.src.Utils.configuration_parser import ResourcesConfiguration
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def diagnose_main(input_volume_filename, input_segmentation_filename, output_folder, preprocessing_scheme='P2',
                  gpu_id='-1'):
    env = ResourcesConfiguration.getInstance()
    env.set_environment(output_dir=output_folder)
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu_id

    diagnose(input_filename=input_volume_filename, input_segmentation=input_segmentation_filename,
             preprocessing_scheme=preprocessing_scheme)
