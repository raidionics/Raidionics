import json
import os
import logging
from aenum import Enum, unique

from utils.models_download import download_model
from utils.software_config import SoftwareConfigResources


@unique
class PipelineTaskType(Enum):
    """

    """
    _init_ = 'value string'

    MRISeqClass = 0, 'MRI sequence classification'
    NeuroPreopSeg = 1, 'Preoperative segmentation'
    NeuroPreopRep = 2, 'Preoperative reporting'
    NeuroPostopSeg = 3, 'Postoperative segmentation'
    NeuroPostopRep = 4, 'Postoperative reporting'

    def __str__(self):
        return self.string


@unique
class ModelNameType(Enum):
    """

    """
    _init_ = 'value string'

    HGGlioma = 0, 'MRI_GBM'
    LGGlioma = 1, 'MRI_LGGlioma'
    Meningioma = 2, 'MRI_Meningioma'
    Metastasis = 3, 'MRI_Metastase'
    MRISeqClass = 4, 'MRI_Sequence_Classifier'

    def __str__(self):
        return self.string


def create_pipeline(model_name: str, patient_parameters, task: str) -> dict:
    """
    Generates on-the-fly the pipeline that should be executed, based on predetermined use-cases.
    How to allow for all possible combinations of what to use/what to run/on which timestamps?

    @TODO. Still heavily hard-coded atm, will need to rely only on the pipeline json files
    @TODO. Postop segmentation not adapting to the number of inputs, defaulting to the 4 inputs.
    Returns
    -------
    dict
        A dictionary containing the Pipeline structure, which will be saved on disk as json.
    """
    # The model(s) must be downloaded first, since the pipeline.json file(s) must be used later for assembling
    # the backend pipeline... Have to organize it better, and prepare reporting pipelines for download?
    download_model(model_name)

    if task == 'folders_classification':
        return __create_folders_classification_pipeline()
    elif task == 'preop_segmentation':
        return __create_segmentation_pipeline(model_name, patient_parameters)
    elif task == 'postop_segmentation':
        download_model(model_name='MRI_GBM_Postop_FV_4p')
        return __create_postop_segmentation_pipeline(model_name, patient_parameters)
    elif task == 'other_segmentation':
        return __create_other_segmentation_pipeline(model_name, patient_parameters)
    elif task == 'preop_reporting':
        return __create_preop_reporting_pipeline(model_name, patient_parameters)
    elif task == 'postop_reporting':
        download_model(model_name='MRI_GBM_Postop_FV_4p')
        return __create_postop_reporting_pipeline(model_name, patient_parameters)
    else:
        return __create_custom_pipeline(task, model_name, patient_parameters)


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
    infile = open(os.path.join(SoftwareConfigResources.getInstance().models_path, model_name, 'pipeline.json'), 'rb')
    raw_pip = json.load(infile)

    pip = {}
    pip_num_int = 0
    if not SoftwareConfigResources.getInstance().user_preferences.use_manual_sequences:
        pip_num_int = pip_num_int + 1
        pip_num = str(pip_num_int)
        pip[pip_num] = {}
        pip[pip_num]["task"] = 'Classification'
        pip[pip_num]["inputs"] = {}
        pip[pip_num]["model"] = 'MRI_Sequence_Classifier'
        pip[pip_num]["description"] = "Classification of the MRI sequence type for all input scans"
        download_model(model_name='MRI_Sequence_Classifier')

    for steps in list(raw_pip.keys()):
        pip_num_int = pip_num_int + 1
        pip_num = str(pip_num_int)
        pip[pip_num] = raw_pip[steps]

    return pip


def __create_other_segmentation_pipeline(model_name, patient_parameters):
    pip = {}
    pip_num_int = 0

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
    pip[pip_num]["target"] = ["Lungs"]
    pip[pip_num]["model"] = "CT_Lungs"
    pip[pip_num]["description"] = "Lungs segmentation in T1CE (T0)"
    download_model(model_name='CT_Lungs')

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
    pip[pip_num]["target"] = ["Airways"]
    pip[pip_num]["model"] = "CT_Airways"
    pip[pip_num]["description"] = "Airways segmentation in T1CE (T0)"
    download_model(model_name="CT_Airways")

    return pip


def __create_postop_segmentation_pipeline(model_name, patient_parameters):
    """
    The default postop segmentation model is the one with four inputs, but based on the loaded images another fitting
    model could be used.
    @TODO. Ideally, in the future, the disambiguation of the best model to use should be done in the backend. In that
    case, how to properly retrieve the corresponding pipeline.json?
    """
    postop_model_name = "MRI_GBM_Postop_FV_4p"
    if SoftwareConfigResources.getInstance().user_preferences.use_manual_sequences:
        postop_model_name = select_appropriate_postop_model(patient_parameters)
    infile = open(os.path.join(SoftwareConfigResources.getInstance().models_path, postop_model_name, 'pipeline.json'), 'rb')
    raw_pip = json.load(infile)

    pip = {}
    pip_num_int = 0
    if not SoftwareConfigResources.getInstance().user_preferences.use_manual_sequences:
        pip_num_int = pip_num_int + 1
        pip_num = str(pip_num_int)
        pip[pip_num] = {}
        pip[pip_num]["task"] = 'Classification'
        pip[pip_num]["inputs"] = {}
        pip[pip_num]["model"] = 'MRI_Sequence_Classifier'
        pip[pip_num]["description"] = "Classification of the MRI sequence type for all input scans"
        download_model(model_name='MRI_Sequence_Classifier')

    for steps in list(raw_pip.keys()):
        pip_num_int = pip_num_int + 1
        pip_num = str(pip_num_int)
        pip[pip_num] = raw_pip[steps]

    return pip


def __create_preop_reporting_pipeline(model_name, patient_parameters):
    """
    @TODO. The pipeline should be more generic or adjustable to the required inputs. Could have a collection of
    pipelines in .raidionics/resources/pipelines?
    Hard-coded for now, so that in v1.2 reporting works for LGGs.
    """
    infile = open(os.path.join(SoftwareConfigResources.getInstance().models_path, model_name, 'pipeline.json'), 'rb')
    raw_pip = json.load(infile)

    pip = {}
    pip_num_int = 0
    if not SoftwareConfigResources.getInstance().user_preferences.use_manual_sequences:
        pip_num_int = pip_num_int + 1
        pip_num = str(pip_num_int)
        pip[pip_num] = {}
        pip[pip_num]["task"] = 'Classification'
        pip[pip_num]["inputs"] = {}
        pip[pip_num]["model"] = 'MRI_Sequence_Classifier'
        pip[pip_num]["description"] = "Classification of the MRI sequence type for all input scans"
        download_model(model_name='MRI_Sequence_Classifier')

    for steps in list(raw_pip.keys()):
        pip_num_int = pip_num_int + 1
        pip_num = str(pip_num_int)
        pip[pip_num] = raw_pip[steps]

    # @TODO. Hard-coded, to remove/improve
    if "Meningioma" in model_name:
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
        download_model("MRI_Brain")

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 0
    pip[pip_num]["moving"]["sequence"] = "T1-CE" if "LGG" not in model_name else "FLAIR"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = -1
    pip[pip_num]["fixed"]["sequence"] = "MNI"
    pip[pip_num]["description"] = "Registration from T1CE (T0) to MNI space" if "LGG" not in model_name else "Registration from FLAIR (T0) to MNI space"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Apply registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 0
    pip[pip_num]["moving"]["sequence"] = "T1-CE" if "LGG" not in model_name else "FLAIR"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = -1
    pip[pip_num]["fixed"]["sequence"] = "MNI"
    pip[pip_num]["direction"] = "forward"
    pip[pip_num]["description"] = "Apply registration from T1CE (T0) to MNI space" if "LGG" not in model_name else "Apply registration from FLAIR (T0) to MNI space"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Apply registration'
    pip[pip_num]["moving"] = {}
    pip[pip_num]["moving"]["timestamp"] = 0
    pip[pip_num]["moving"]["sequence"] = "T1-CE" if "LGG" not in model_name else "FLAIR"
    pip[pip_num]["fixed"] = {}
    pip[pip_num]["fixed"]["timestamp"] = -1
    pip[pip_num]["fixed"]["sequence"] = "MNI"
    pip[pip_num]["direction"] = "inverse"
    pip[pip_num]["description"] = "Apply inverse registration from MNI space to T1CE (T0)" if "LGG" not in model_name else "Apply inverse registration from MNI space to FLAIR (T0)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Features computation'
    pip[pip_num]["input"] = {}
    pip[pip_num]["input"]["timestamp"] = 0
    pip[pip_num]["input"]["sequence"] = "T1-CE" if "LGG" not in model_name else "FLAIR"
    pip[pip_num]["target"] = "Tumor"
    pip[pip_num]["space"] = "MNI"
    pip[pip_num]["description"] = "Tumor features computation from T1CE (T0) in MNI space" if "LGG" not in model_name else "Tumor features computation from FLAIR (T0) in MNI space"

    return pip


def __create_postop_reporting_pipeline(model_name, patient_parameters):
    """

    """
    pip = {}
    pip_num_int = 0
    if not SoftwareConfigResources.getInstance().user_preferences.use_manual_sequences:
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
    pip[pip_num]["description"] = "Registration from T1CE (T0) to T1CE (T1)"

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
    pip[pip_num]["description"] = "Apply registration from T1CE (T0) to T1CE (T1)"

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
    pip[pip_num]["description"] = "Registration from FLAIR (T1) to T1CE (T1)"

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
    pip[pip_num]["description"] = "Apply registration from FLAIR (T1) to T1CE (T1)"

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
    pip[pip_num]["description"] = "Brain segmentation in T1w (T1)"

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
    pip[pip_num]["description"] = "Registration from T1w (T1) to T1CE (T1)"

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
    pip[pip_num]["description"] = "Apply registration from T1w (T1) to T1CE (T1)"

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
    pip[pip_num]["model"] = "MRI_GBM_Postop_FV_4p"
    pip[pip_num]["description"] = "Tumor segmentation in T1CE (T1)"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = "Surgical reporting"
    pip[pip_num]["description"] = "Postoperative report computing."

    return pip


def __create_custom_pipeline(task, tumor_type, patient_parameters):
    split_task = task.split('_')
    pip = {}
    pip_num_int = 0

    if split_task[0] == "Classification":
        pip_num_int = pip_num_int + 1
        pip_num = str(pip_num_int)
        pip[pip_num] = {}
        pip[pip_num]["task"] = 'Classification'
        pip[pip_num]["inputs"] = {}
        pip[pip_num]["model"] = 'MRI_Sequence_Classifier'
        pip[pip_num]["description"] = "Classification of the MRI sequence type for all input scans"
        download_model(model_name='MRI_Sequence_Classifier')
    elif split_task[0] == "Segmentation":
        if not SoftwareConfigResources.getInstance().user_preferences.use_manual_sequences:
            pip_num_int = pip_num_int + 1
            pip_num = str(pip_num_int)
            pip[pip_num] = {}
            pip[pip_num]["task"] = 'Classification'
            pip[pip_num]["inputs"] = {}
            pip[pip_num]["model"] = 'MRI_Sequence_Classifier'
            pip[pip_num]["description"] = "Classification of the MRI sequence type for all input scans"
            download_model(model_name='MRI_Sequence_Classifier')

        base_model_name = "MRI_" if SoftwareConfigResources.getInstance().software_medical_specialty == "neurology" else "CT_"
        timestamp_order = int(split_task[2][1:])
        if SoftwareConfigResources.getInstance().software_medical_specialty == "thoracic" and split_task[1] != "Lungs":
            pip_num_int = pip_num_int + 1
            pip_num = str(pip_num_int)
            pip[pip_num] = {}
            pip[pip_num]["task"] = 'Segmentation'
            pip[pip_num]["inputs"] = {}
            pip[pip_num]["inputs"]["0"] = {}
            pip[pip_num]["inputs"]["0"]["timestamp"] = timestamp_order
            pip[pip_num]["inputs"]["0"]["sequence"] = "T1-CE"
            pip[pip_num]["inputs"]["0"]["labels"] = None
            pip[pip_num]["inputs"]["0"]["space"] = {}
            pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = timestamp_order
            pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-CE"
            pip[pip_num]["target"] = ["Lungs"]
            pip[pip_num]["model"] = "CT_Lungs"
            pip[pip_num]["description"] = "Lungs segmentation in T1CE (T{})".format(str(timestamp_order))
            download_model(model_name="CT_Lungs")

        if split_task[1] == 'Tumor':
            infile = open(os.path.join(SoftwareConfigResources.getInstance().models_path, tumor_type, 'pipeline.json'),
                          'rb')
            raw_pip = json.load(infile)

            for steps in list(raw_pip.keys()):
                pip_num_int = pip_num_int + 1
                pip_num = str(pip_num_int)
                pip[pip_num] = raw_pip[steps]
        if split_task[1] == 'Brain':
            infile = open(os.path.join(SoftwareConfigResources.getInstance().models_path, tumor_type, 'pipeline.json'),
                          'rb')
            raw_pip = json.load(infile)
            ts_inputs = patient_parameters.get_all_mri_volumes_for_timestamp(split_task[2])
            for input in ts_inputs:
                volume_input = patient_parameters.get_mri_by_uid(input)
                matching_ts = patient_parameters.get_timestamp_by_uid(volume_input.timestamp_uid)
                adjusted_pip = raw_pip
                adjusted_pip["1"]["inputs"]["0"]["timestamp"] = int(matching_ts.order)
                adjusted_pip["1"]["inputs"]["0"]["sequence"] = volume_input.get_sequence_type_str()
                adjusted_pip["1"]["inputs"]["0"]["space"]["timestamp"] = int(matching_ts.order)
                adjusted_pip["1"]["inputs"]["0"]["space"]["sequence"] = volume_input.get_sequence_type_str()
                adjusted_pip["1"]["description"] = adjusted_pip["1"]["description"].replace("T1CE", volume_input.get_sequence_type_str()).replace("T0", "T"+str(matching_ts.order))
                for steps in list(adjusted_pip.keys()):
                    pip_num_int = pip_num_int + 1
                    pip_num = str(pip_num_int)
                    pip[pip_num] = adjusted_pip[steps]
        else:
            for k in SoftwareConfigResources.getInstance().get_annotation_types_for_specialty():
                model_name = base_model_name + k if k != "Tumor" else tumor_type
                pip_num_int = pip_num_int + 1
                pip_num = str(pip_num_int)
                pip[pip_num] = {}
                pip[pip_num]["task"] = 'Segmentation'
                pip[pip_num]["inputs"] = {}
                pip[pip_num]["inputs"]["0"] = {}
                pip[pip_num]["inputs"]["0"]["timestamp"] = timestamp_order
                pip[pip_num]["inputs"]["0"]["sequence"] = "T1-CE"
                pip[pip_num]["inputs"]["0"]["labels"] = None
                pip[pip_num]["inputs"]["0"]["space"] = {}
                pip[pip_num]["inputs"]["0"]["space"]["timestamp"] = timestamp_order
                pip[pip_num]["inputs"]["0"]["space"]["sequence"] = "T1-CE"
                pip[pip_num]["target"] = [k]
                pip[pip_num]["model"] = model_name
                pip[pip_num]["description"] = k + " segmentation in T1CE (T{})".format(str(timestamp_order))
                download_model(model_name=model_name)
    return pip


def select_appropriate_postop_model(patient_parameters) -> str:
    """
    Temporary method, which will be deported in the backend, for selecting the best postoperative glioblastoma
    segmentation model based on available inputs.
    """
    model_name = "MRI_GBM_Postop_FV_4p"

    return model_name
