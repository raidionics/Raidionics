import logging

from utils.models_download import download_model

# @TODO. Have an Enum type for the different pipeline tasks? Which are predefined anyway now.


def create_pipeline(model_name: str, patient_parameters, task: str) -> dict:
    """
    Generates on-the-fly the pipeline that should be executed, based on predetermined use-cases.
    How to allow for all possible combinations of what to use/what to run/on which timestamps?

    Returns
    -------
    dict
        A dictionary containing the Pipeline structure, which will be saved on disk as json.
    """
    if task == 'folders_classification':
        return __create_folders_classification_pipeline()
    elif task == 'preop_segmentation':
        return __create_segmentation_pipeline(model_name, patient_parameters)
    elif task == 'postop_segmentation':
        return __create_postop_segmentation_pipeline(model_name, patient_parameters)
    elif task == 'preop_reporting':
        return __create_preop_reporting_pipeline(model_name, patient_parameters)
    elif task == 'postop_reporting':
        return __create_postop_reporting_pipeline(model_name, patient_parameters)
    else:
        logging.error("The requested pipeline task does not match any known task, with {}".format(task))
        return {}


def __create_folders_classification_pipeline():
    pip = {}
    pip_num_int = 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Classification'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["model"] = 'MRI_Sequence_Classifier'
    pip[pip_num]["description"] = "Classification of the MRI sequence type for all input scans"
    download_model(model_name='MRI_Sequence_Classifier')

    return pip


def __create_segmentation_pipeline(model_name, patient_parameters):
    """
    Brain segmentation should be performed by default, regardless of if the tumor segmentation model needs it.
    """
    pip = {}
    pip_num_int = 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Classification'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["model"] = 'MRI_Sequence_Classifier'
    pip[pip_num]["description"] = "Classification of the MRI sequence type for all input scans"
    download_model(model_name='MRI_Sequence_Classifier')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["target"] = ["Brain"]
    pip[pip_num]["model"] = "MRI_Brain"
    pip[pip_num]["description"] = "Brain segmentation in T1CE (T0)"
    download_model(model_name='MRI_Brain')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["target"] = ["Tumor"]
    pip[pip_num]["model"] = model_name
    pip[pip_num]["description"] = "Tumor segmentation in T1CE (T0)"
    download_model(model_name=model_name)

    return pip


def __create_postop_segmentation_pipeline(model_name, patient_parameters):
    """

    """
    pip = {}
    pip_num_int = 0
    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Classification'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["model"] = 'MRI_Sequence_Classifier'
    pip[pip_num]["description"] = "Classification of the MRI sequence type for all input scans"
    download_model(model_name='MRI_Sequence_Classifier')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["target"] = ["Brain"]
    pip[pip_num]["model"] = "MRI_Brain"
    pip[pip_num]["description"] = "Brain segmentation in T1CE (T0)"
    download_model(model_name='MRI_Brain')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["target"] = ["Tumor"]
    pip[pip_num]["model"] = model_name
    pip[pip_num]["description"] = "Tumor segmentation in T1CE (T0)"
    download_model(model_name=model_name)

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["target"] = ["Brain"]
    pip[pip_num]["model"] = "MRI_Brain"
    pip[pip_num]["description"] = "Brain segmentation in T1CE (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 0
    pip[pip_num]["moving"]["sequence"] = "T1-CE"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = 1
    pip[pip_num]["fixed"]["sequence"] = "T1-CE"
    pip[pip_num]["description"] = "Registration from T1-CE (T0) to T1CE (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Apply registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 0
    pip[pip_num]["moving"]["sequence"] = "T1-CE"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = 1
    pip[pip_num]["fixed"]["sequence"] = "T1-CE"
    pip[pip_num]["direction"] = "forward"
    pip[pip_num]["description"] = "Apply registration from T1-CE (T0) to T1CE (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["sequence"] = "FLAIR"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "FLAIR"
    pip[pip_num]["target"] = ["Brain"]
    pip[pip_num]["model"] = "MRI_Brain"
    pip[pip_num]["description"] = "Brain segmentation in FLAIR (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 1
    pip[pip_num]["moving"]["sequence"] = "FLAIR"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = 1
    pip[pip_num]["fixed"]["sequence"] = "T1-CE"
    pip[pip_num]["description"] = "Registration from FLAIR (T1) to T1-CE (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Apply registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 1
    pip[pip_num]["moving"]["sequence"] = "FLAIR"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = 1
    pip[pip_num]["fixed"]["sequence"] = "T1-CE"
    pip[pip_num]["direction"] = "forward"
    pip[pip_num]["description"] = "Apply registration from FLAIR (T1) to T1-CE (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["sequence"] = "T1-w"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-w"
    pip[pip_num]["target"] = ["Brain"]
    pip[pip_num]["model"] = "MRI_Brain"
    pip[pip_num]["description"] = "Brain segmentation in T1-w (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 1
    pip[pip_num]["moving"]["sequence"] = "T1-w"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = 1
    pip[pip_num]["fixed"]["sequence"] = "T1-CE"
    pip[pip_num]["description"] = "Registration from T1-w (T1) to T1-CE (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Apply registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 1
    pip[pip_num]["moving"]["sequence"] = "T1-w"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = 1
    pip[pip_num]["fixed"]["sequence"] = "T1-CE"
    pip[pip_num]["direction"] = "forward"
    pip[pip_num]["description"] = "Apply registration from T1-w (T1) to T1-CE (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["1"] = {}
    pip[pip_num]["inputs"]["1"]["timestamp"] = 1
    pip[pip_num]["inputs"]["1"]["sequence"] = "T1-w"
    pip[pip_num]["inputs"]["1"]["labels"] = None
    pip[pip_num]["inputs"]["1"]["space"] = {}
    pip[pip_num]["inputs"]["1"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["1"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["2"] = {}
    pip[pip_num]["inputs"]["2"]["timestamp"] = 1
    pip[pip_num]["inputs"]["2"]["sequence"] = "FLAIR"
    pip[pip_num]["inputs"]["2"]["labels"] = None
    pip[pip_num]["inputs"]["2"]["space"] = {}
    pip[pip_num]["inputs"]["2"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["2"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["3"] = {}
    pip[pip_num]["inputs"]["3"]["timestamp"] = 0
    pip[pip_num]["inputs"]["3"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["3"]["labels"] = None
    pip[pip_num]["inputs"]["3"]["space"] = {}
    pip[pip_num]["inputs"]["3"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["3"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["4"] = {}
    pip[pip_num]["inputs"]["4"]["timestamp"] = 0
    pip[pip_num]["inputs"]["4"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["4"]["labels"] = "Tumor"
    pip[pip_num]["inputs"]["4"]["space"] = {}
    pip[pip_num]["inputs"]["4"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["4"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["target"] = ["Tumor"]
    pip[pip_num]["model"] = "MRI_Tumor_Postop"
    pip[pip_num]["description"] = "Tumor segmentation in T1-CE (T1)"
    # download_model(model_name='MRI_Tumor_Postop')

    return pip


def __create_preop_reporting_pipeline(model_name, patient_parameters):
    """

    """
    pip = {}
    pip_num_int = 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Classification'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["model"] = 'MRI_Sequence_Classifier'
    pip[pip_num]["description"] = "Classification of the MRI sequence type for all input scans"
    download_model(model_name='MRI_Sequence_Classifier')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["target"] = ["Brain"]
    pip[pip_num]["model"] = "MRI_Brain"
    pip[pip_num]["description"] = "Brain segmentation in T1CE (T0)"
    download_model(model_name='MRI_Brain')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["target"] = ["Tumor"]
    pip[pip_num]["model"] = model_name
    pip[pip_num]["description"] = "Tumor segmentation in T1CE (T0)"
    download_model(model_name=model_name)

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 0
    pip[pip_num]["moving"]["sequence"] = "T1-CE"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = -1
    pip[pip_num]["fixed"]["sequence"] = "MNI"
    pip[pip_num]["description"] = "Registration from T1CE (T0) to MNI space"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Apply registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 0
    pip[pip_num]["moving"]["sequence"] = "T1-CE"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = -1
    pip[pip_num]["fixed"]["sequence"] = "MNI"
    pip[pip_num]["direction"] = "forward"
    pip[pip_num]["description"] = "Apply registration from T1CE (T0) to MNI space"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Apply registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 0
    pip[pip_num]["moving"]["sequence"] = "T1-CE"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = -1
    pip[pip_num]["fixed"]["sequence"] = "MNI"
    pip[pip_num]["direction"] = "inverse"
    pip[pip_num]["description"] = "Apply inverse registration from MNI space to T1CE (T0)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Features computation'
    pip[pip_num]["input"] = {}
    pip[pip_num]["input"]["timestamp"] = 0
    pip[pip_num]["input"]["sequence"] = "T1-CE"
    pip[pip_num]["target"] = "Tumor"
    pip[pip_num]["space"] = "MNI"
    pip[pip_num]["description"] = "Tumor features computation from T0 in MNI space"

    return pip


def __create_postop_reporting_pipeline(model_name, patient_parameters):
    """

    """
    pip = {}
    pip_num_int = 0
    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Classification'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["model"] = 'MRI_Sequence_Classifier'
    pip[pip_num]["description"] = "Classification of the MRI sequence type for all input scans"
    download_model(model_name='MRI_Sequence_Classifier')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["target"] = ["Brain"]
    pip[pip_num]["model"] = "MRI_Brain"
    pip[pip_num]["description"] = "Brain segmentation in T1CE (T0)"
    download_model(model_name='MRI_Brain')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 0
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["target"] = ["Tumor"]
    pip[pip_num]["model"] = model_name
    pip[pip_num]["description"] = "Tumor segmentation in T1CE (T0)"
    download_model(model_name=model_name)

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["target"] = ["Brain"]
    pip[pip_num]["model"] = "MRI_Brain"
    pip[pip_num]["description"] = "Brain segmentation in T1CE (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 0
    pip[pip_num]["moving"]["sequence"] = "T1-CE"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = 1
    pip[pip_num]["fixed"]["sequence"] = "T1-CE"
    pip[pip_num]["description"] = "Registration from T1-CE (T0) to T1CE (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Apply registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 0
    pip[pip_num]["moving"]["sequence"] = "T1-CE"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = 1
    pip[pip_num]["fixed"]["sequence"] = "T1-CE"
    pip[pip_num]["direction"] = "forward"
    pip[pip_num]["description"] = "Apply registration from T1-CE (T0) to T1CE (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["sequence"] = "FLAIR"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "FLAIR"
    pip[pip_num]["target"] = ["Brain"]
    pip[pip_num]["model"] = "MRI_Brain"
    pip[pip_num]["description"] = "Brain segmentation in FLAIR (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 1
    pip[pip_num]["moving"]["sequence"] = "FLAIR"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = 1
    pip[pip_num]["fixed"]["sequence"] = "T1-CE"
    pip[pip_num]["description"] = "Registration from FLAIR (T1) to T1-CE (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Apply registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 1
    pip[pip_num]["moving"]["sequence"] = "FLAIR"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = 1
    pip[pip_num]["fixed"]["sequence"] = "T1-CE"
    pip[pip_num]["direction"] = "forward"
    pip[pip_num]["description"] = "Apply registration from FLAIR (T1) to T1-CE (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["sequence"] = "T1-w"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-w"
    pip[pip_num]["target"] = ["Brain"]
    pip[pip_num]["model"] = "MRI_Brain"
    pip[pip_num]["description"] = "Brain segmentation in T1-w (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 1
    pip[pip_num]["moving"]["sequence"] = "T1-w"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = 1
    pip[pip_num]["fixed"]["sequence"] = "T1-CE"
    pip[pip_num]["description"] = "Registration from T1-w (T1) to T1-CE (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Apply registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 1
    pip[pip_num]["moving"]["sequence"] = "T1-w"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = 1
    pip[pip_num]["fixed"]["sequence"] = "T1-CE"
    pip[pip_num]["direction"] = "forward"
    pip[pip_num]["description"] = "Apply registration from T1-w (T1) to T1-CE (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Segmentation'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["inputs"]["0"] = {}
    pip[pip_num]["inputs"]["0"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["0"]["labels"] = None
    pip[pip_num]["inputs"]["0"]["space"] = {}
    pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["1"] = {}
    pip[pip_num]["inputs"]["1"]["timestamp"] = 1
    pip[pip_num]["inputs"]["1"]["sequence"] = "T1-w"
    pip[pip_num]["inputs"]["1"]["labels"] = None
    pip[pip_num]["inputs"]["1"]["space"] = {}
    pip[pip_num]["inputs"]["1"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["1"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["2"] = {}
    pip[pip_num]["inputs"]["2"]["timestamp"] = 1
    pip[pip_num]["inputs"]["2"]["sequence"] = "FLAIR"
    pip[pip_num]["inputs"]["2"]["labels"] = None
    pip[pip_num]["inputs"]["2"]["space"] = {}
    pip[pip_num]["inputs"]["2"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["2"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["3"] = {}
    pip[pip_num]["inputs"]["3"]["timestamp"] = 0
    pip[pip_num]["inputs"]["3"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["3"]["labels"] = None
    pip[pip_num]["inputs"]["3"]["space"] = {}
    pip[pip_num]["inputs"]["3"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["3"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["4"] = {}
    pip[pip_num]["inputs"]["4"]["timestamp"] = 0
    pip[pip_num]["inputs"]["4"]["sequence"] = "T1-CE"
    pip[pip_num]["inputs"]["4"]["labels"] = "Tumor"
    pip[pip_num]["inputs"]["4"]["space"] = {}
    pip[pip_num]["inputs"]["4"]["space"]["timestamp"] = 1
    pip[pip_num]["inputs"]["4"]["space"]["sequence"] = "T1-CE"
    pip[pip_num]["target"] = ["Tumor"]
    pip[pip_num]["model"] = "MRI_Tumor_Postop"
    pip[pip_num]["description"] = "Tumor segmentation in T1-CE (T1)"
    # download_model(model_name='MRI_Tumor_Postop')

    #@TODO. Needs to include the reporting part
    return pip
