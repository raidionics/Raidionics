import json
import os
import logging
from typing import Tuple
from copy import deepcopy
from aenum import Enum, unique

from utils.data_structures.PatientParametersStructure import PatientParameters
from utils.models_download import download_model
from utils.software_config import SoftwareConfigResources
from utils.data_structures.UserPreferencesStructure import UserPreferencesStructure
from utils.utilities import get_type_from_name, get_type_from_string


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
class TumorType(Enum):
    """

    """
    _init_ = 'value string'

    CE = 0, 'Contrast-enhancing'
    NCE = 1, 'Non contrast-enhancing'

    def __str__(self):
        return self.string


def create_pipeline(tumor_type: str, patient_parameters, task: str) -> dict:
    """
    Generates on-the-fly the pipeline that should be executed, based on predetermined use-cases.
    A deeper modularity will only be possible if using the backend directly, and hence customizing manually the
    json file describing the pipeline to execute.

    Parameters
    ----------
    :param tumor_type: Main type for the tumor, contrast-enhancing or non-contrast-enhancing for a neurological use-case
    :param patient_parameters: Dictionary of the input patient parameters

    Returns
    -------
    dict
        A dictionary containing the Pipeline structure, which will be saved on disk as json.
    """
    if task == 'folders_classification':
        return __create_folders_classification_pipeline()
    elif task == 'preop_segmentation':
        return __create_preop_segmentation_pipeline(tumor_type=tumor_type)
    elif 'postop_segmentation' in task:
        return __create_postop_segmentation_pipeline(tumor_type=tumor_type)
    elif task == 'other_segmentation':
        return __create_other_segmentation_pipeline(tumor_type=tumor_type)
    elif task == 'preop_reporting':
        return __create_preop_reporting_pipeline(tumor_type=tumor_type)
    elif task == 'postop_reporting':
        return __create_postop_reporting_pipeline(tumor_type=tumor_type)
    elif task == 'surgical_reporting':
        return __create_surgical_reporting_pipeline(tumor_type=tumor_type)
    else:
        return __create_custom_pipeline(task, tumor_type, patient_parameters)


def __create_folders_classification_pipeline():
    """

    """
    pip = {}
    if SoftwareConfigResources.getInstance().software_medical_specialty == "neurology":
        pip_num_int = 1
        pip_num = str(pip_num_int)
        pip[pip_num] = {}
        pip[pip_num]["task"] = 'Classification'
        pip[pip_num]["inputs"] = {}
        pip[pip_num]["target"] = ["MRSequence"]
        pip[pip_num]["model"] = 'MRI_SequenceClassifier'
        pip[pip_num]["description"] = "Classification of the MRI sequence type for all input scans"
        download_model(model_name='MRI_SequenceClassifier')
    else:
        raise ValueError(f"No input classification for {SoftwareConfigResources.getInstance().software_medical_specialty} yet.")

    return pip


def __create_preop_segmentation_pipeline(tumor_type: str) -> dict:
    """

    Parameters
    ----------
    :param tumor_type: Main type for the tumor

    Returns
    -------
    dict Matching pipeline for the requested task
    """
    pip = {}
    pip_num_int = 0
    if not UserPreferencesStructure.getInstance().use_manual_sequences:
        pip, pip_num_int = include_radiological_volume_classifier(pip=pip, pip_num_start=pip_num_int)

    if get_type_from_string(TumorType, tumor_type) == TumorType.CE:
        pip_num_int = pip_num_int + 1
        pip_num = str(pip_num_int)
        pip[pip_num] = {}
        pip[pip_num]["task"] = 'Model selection'
        pip[pip_num]["model"] = 'MRI_TumorCore'
        pip[pip_num]["timestamp"] = 0
        pip[pip_num]["format"] = "thresholding"
        pip[pip_num]["description"] = "Identifying the best tumor core segmentation model for existing inputs"
        download_model(model_name='MRI_TumorCore')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Model selection'
    pip[pip_num]["model"] = 'MRI_FLAIRChanges'
    pip[pip_num]["timestamp"] = 0
    pip[pip_num]["format"] = "thresholding"
    pip[pip_num]["description"] = "Identifying the best FLAIR changes segmentation model for existing inputs"
    download_model(model_name='MRI_FLAIRChanges')

    # @TODO. Might add other models here, such as the cavity model (even preop) for re-operation cases
    return pip


def __create_other_segmentation_pipeline(tumor_type: str) -> dict:
    raise ValueError("[Software error] Running a custom segmentation is not enabled right now!")
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


def __create_postop_segmentation_pipeline(tumor_type: str) -> dict:
    """
    Setting the pipeline for running the different available models for a postoperative timestamp.

    @TODO. Should there be a structures refinement step, as in between the different segmentation output, or do we
    consider to be performed only as part of the standardized reporting?
    """
    pip = {}
    pip_num_int = 0
    if not UserPreferencesStructure.getInstance().use_manual_sequences:
        pip, pip_num_int = include_radiological_volume_classifier(pip=pip, pip_num_start=pip_num_int)

    # A postoperative model would in general required an associated preoperative timestamp (might need the preop data).
    # If only a single timestamp is loaded in Raidionics, and the postop_segmentation button was pressed, then it is
    # assumed to be the postoperative timestamp.
    postop_ts = 1
    if len(SoftwareConfigResources.getInstance().get_active_patient().investigation_timestamps) == 1:
        postop_ts = 0

    if get_type_from_string(TumorType, tumor_type) == TumorType.CE:
        pip_num_int = pip_num_int + 1
        pip_num = str(pip_num_int)
        pip[pip_num] = {}
        pip[pip_num]["task"] = 'Model selection'
        pip[pip_num]["model"] = 'MRI_TumorCE_Postop'
        pip[pip_num]["timestamp"] = postop_ts
        pip[pip_num]["format"] = "thresholding"
        pip[pip_num]["description"] = "Identifying the best rest enhancing tumor segmentation model for existing inputs"
        download_model(model_name='MRI_TumorCE_Postop')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Model selection'
    pip[pip_num]["model"] = 'MRI_FLAIRChanges'
    pip[pip_num]["timestamp"] = postop_ts
    pip[pip_num]["format"] = "thresholding"
    pip[pip_num]["description"] = "Identifying the best FLAIR changes segmentation model for existing inputs"
    download_model(model_name='MRI_FLAIRChanges')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Model selection'
    pip[pip_num]["model"] = 'MRI_Cavity'
    pip[pip_num]["timestamp"] = postop_ts
    pip[pip_num]["format"] = "thresholding"
    pip[pip_num]["description"] = "Identifying the best resection cavity segmentation model for existing inputs"
    download_model(model_name='MRI_Cavity')

    return pip


def __create_preop_reporting_pipeline(tumor_type: str) -> dict:
    """
    @TODO. The pipeline should be more generic or adjustable to the required inputs. Could have a collection of
    pipelines in .raidionics/resources/pipelines?
    Hard-coded for now, so that in v1.2 reporting works for LGGs.

    @TODO. Should the timestamp be forwarded here also, to feed the ModelSelection (working whether preop or postop)
    """
    pip = {}
    pip_num_int = 0
    if not UserPreferencesStructure.getInstance().use_manual_sequences:
        pip, pip_num_int = include_radiological_volume_classifier(pip=pip, pip_num_start=pip_num_int)

    if get_type_from_string(TumorType, tumor_type) == TumorType.CE:
        pip_num_int = pip_num_int + 1
        pip_num = str(pip_num_int)
        pip[pip_num] = {}
        pip[pip_num]["task"] = 'Model selection'
        pip[pip_num]["model"] = 'MRI_TumorCore'
        pip[pip_num]["timestamp"] = 0
        pip[pip_num]["format"] = "thresholding"
        pip[pip_num]["description"] = "Identifying the best tumor core segmentation model for existing inputs"
        download_model(model_name='MRI_TumorCore')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Model selection'
    pip[pip_num]["model"] = 'MRI_FLAIRChanges'
    pip[pip_num]["timestamp"] = 0
    pip[pip_num]["format"] = "thresholding"
    pip[pip_num]["description"] = "Identifying the best FLAIR changes segmentation model for existing inputs"
    download_model(model_name='MRI_FLAIRChanges')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Reporting selection'
    pip[pip_num]["scope"] = "standalone"
    pip[pip_num]["tumor_type"] = tumor_type.lower()
    pip[pip_num]["timestamps"] = [0]
    pip[pip_num]["description"] = "Setting up the reporting steps for features computation in T0"

    return pip


def __create_postop_reporting_pipeline(tumor_type: str) -> dict:
    """

    """

    pip = {}
    pip_num_int = 0
    if not UserPreferencesStructure.getInstance().use_manual_sequences:
        pip, pip_num_int = include_radiological_volume_classifier(pip=pip, pip_num_start=pip_num_int)

    # A postoperative model would in general required an associated preoperative timestamp (might need the preop data).
    # If only a single timestamp is loaded in Raidionics, and the postop_segmentation button was pressed, then it is
    # assumed to be the postoperative timestamp.
    postop_ts = 1
    if len(SoftwareConfigResources.getInstance().get_active_patient().investigation_timestamps) == 1:
        postop_ts = 0

    if get_type_from_string(TumorType, tumor_type) == TumorType.CE:
        pip_num_int = pip_num_int + 1
        pip_num = str(pip_num_int)
        pip[pip_num] = {}
        pip[pip_num]["task"] = 'Model selection'
        pip[pip_num]["model"] = 'MRI_TumorCE_Postop'
        pip[pip_num]["timestamp"] = postop_ts
        pip[pip_num]["format"] = "thresholding"
        pip[pip_num]["description"] = "Identifying the best tumor core segmentation model for existing inputs"
        download_model(model_name='MRI_TumorCE_Postop')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Model selection'
    pip[pip_num]["model"] = 'MRI_FLAIRChanges'
    pip[pip_num]["timestamp"] = postop_ts
    pip[pip_num]["format"] = "thresholding"
    pip[pip_num]["description"] = "Identifying the best FLAIR changes segmentation model for existing inputs"
    download_model(model_name='MRI_FLAIRChanges')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Model selection'
    pip[pip_num]["model"] = 'MRI_Cavity'
    pip[pip_num]["timestamp"] = postop_ts
    pip[pip_num]["format"] = "thresholding"
    pip[pip_num]["description"] = "Identifying the best resection cavity segmentation model for existing inputs"
    download_model(model_name='MRI_Cavity')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Reporting selection'
    pip[pip_num]["scope"] = "standalone"
    pip[pip_num]["tumor_type"] = tumor_type.lower()
    pip[pip_num]["timestamps"] = [postop_ts]
    pip[pip_num]["description"] = f"Setting up the reporting steps for features computation in T{postop_ts}"

    return pip


def __create_surgical_reporting_pipeline(tumor_type: str) -> dict:
    """

    """

    pip = {}
    pip_num_int = 0
    if not UserPreferencesStructure.getInstance().use_manual_sequences:
        pip, pip_num_int = include_radiological_volume_classifier(pip=pip, pip_num_start=pip_num_int)

    if len(SoftwareConfigResources.getInstance().get_active_patient().investigation_timestamps) < 2:
        raise ValueError("[Software error] Computing a surgical report requires data from at least two timepoints (i.e., preop and postop)")

    if get_type_from_string(TumorType, tumor_type) == TumorType.CE:
        pip_num_int = pip_num_int + 1
        pip_num = str(pip_num_int)
        pip[pip_num] = {}
        pip[pip_num]["task"] = 'Model selection'
        pip[pip_num]["model"] = 'MRI_TumorCore'
        pip[pip_num]["timestamp"] = 0
        pip[pip_num]["format"] = "thresholding"
        pip[pip_num]["description"] = "Identifying the best tumor core segmentation model for existing inputs"
        download_model(model_name='MRI_TumorCore')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Model selection'
    pip[pip_num]["model"] = 'MRI_FLAIRChanges'
    pip[pip_num]["timestamp"] = 0
    pip[pip_num]["format"] = "thresholding"
    pip[pip_num]["description"] = "Identifying the best FLAIR changes segmentation model for existing inputs"
    download_model(model_name='MRI_FLAIRChanges')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Model selection'
    pip[pip_num]["model"] = 'MRI_Cavity'
    pip[pip_num]["timestamp"] = 0
    pip[pip_num]["format"] = "thresholding"
    pip[pip_num]["description"] = "Identifying the best resection cavity segmentation model for existing inputs"
    download_model(model_name='MRI_Cavity')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Reporting selection'
    pip[pip_num]["scope"] = "standalone"
    pip[pip_num]["tumor_type"] = tumor_type.lower()
    pip[pip_num]["timestamps"] = [0]
    pip[pip_num]["description"] = f"Setting up the reporting steps for features computation in T{1}"

    if get_type_from_string(TumorType, tumor_type) == TumorType.CE:
        pip_num_int = pip_num_int + 1
        pip_num = str(pip_num_int)
        pip[pip_num] = {}
        pip[pip_num]["task"] = 'Model selection'
        pip[pip_num]["model"] = 'MRI_TumorCE_Postop'
        pip[pip_num]["timestamp"] = 1
        pip[pip_num]["format"] = "thresholding"
        pip[pip_num]["description"] = "Identifying the best tumor core segmentation model for existing inputs"
        download_model(model_name='MRI_TumorCE_Postop')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Model selection'
    pip[pip_num]["model"] = 'MRI_FLAIRChanges'
    pip[pip_num]["timestamp"] = 1
    pip[pip_num]["format"] = "thresholding"
    pip[pip_num]["description"] = "Identifying the best FLAIR changes segmentation model for existing inputs"
    download_model(model_name='MRI_FLAIRChanges')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Model selection'
    pip[pip_num]["model"] = 'MRI_Cavity'
    pip[pip_num]["timestamp"] = 1
    pip[pip_num]["format"] = "thresholding"
    pip[pip_num]["description"] = "Identifying the best resection cavity segmentation model for existing inputs"
    download_model(model_name='MRI_Cavity')

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Reporting selection'
    pip[pip_num]["scope"] = "standalone"
    pip[pip_num]["tumor_type"] = tumor_type.lower()
    pip[pip_num]["timestamps"] = [1]
    pip[pip_num]["description"] = f"Setting up the reporting steps for features computation in T{1}"

    pip_num_int = pip_num_int + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Reporting selection'
    pip[pip_num]["scope"] = "surgical"
    pip[pip_num]["tumor_type"] = tumor_type.lower()
    pip[pip_num]["timestamps"] = [0, 1]
    pip[pip_num]["description"] = f"Setting up the reporting steps for the standardized surgical report"

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
        pip[pip_num]["target"] = ["MRSequence"]
        pip[pip_num]["model"] = 'MRI_SequenceClassifier'
        pip[pip_num]["description"] = "Classification of the MRI sequence type for all input scans"
        download_model(model_name='MRI_SequenceClassifier')
    elif split_task[0] == "Segmentation":
        if not UserPreferencesStructure.getInstance().use_manual_sequences:
            pip_num_int = pip_num_int + 1
            pip_num = str(pip_num_int)
            pip[pip_num] = {}
            pip[pip_num]["task"] = 'Classification'
            pip[pip_num]["inputs"] = {}
            pip[pip_num]["target"] = ["MRSequence"]
            pip[pip_num]["model"] = 'MRI_SequenceClassifier'
            pip[pip_num]["description"] = "Classification of the MRI sequence type for all input scans"
            download_model(model_name='MRI_SequenceClassifier')

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

        if split_task[1] == 'FLAIRChanges' or split_task[1] == 'Cavity':
            pip_num_int = pip_num_int + 1
            pip_num = str(pip_num_int)
            pip[pip_num] = {}
            pip[pip_num]["task"] = 'Model selection'
            pip[pip_num]["model"] = tumor_type
            pip[pip_num]["timestamp"] = int(split_task[2][1])  # Grabbing the number inside T0/T1/etc...
            pip[pip_num]["description"] = "Identifying the best segmentation model for existing inputs"
        elif split_task[1] == 'Brain':
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
    Method for selecting the best postoperative glioblastoma segmentation model based on available inputs.
    Should it be deported in the RADS backend?
    """
    model_name = "MRI_GBM_Postop_FV_1p"
    if not UserPreferencesStructure.getInstance().use_manual_sequences:
        # Case where the model selection should then be deported to the backend, or the MRI sequence identification
        # should happen before calling a segmentation/reporting pipeline?
        return "MRI_GBM_Postop_FV_4p"

    exist_preop_t1 = False
    exist_postop_t1ce = False
    exist_postop_t1w = False
    exist_postop_flair = False

    for v in list(patient_parameters.mri_volumes.keys()):
        volume_object = patient_parameters.mri_volumes[v]
        if volume_object.timestamp_uid == "T0":
            if volume_object.get_sequence_type_str() == "T1-CE":
                exist_preop_t1 = True
        elif volume_object.timestamp_uid == "T1":
            if volume_object.get_sequence_type_str() == "T1-CE":
                exist_postop_t1ce = True
            elif volume_object.get_sequence_type_str() == "T1-w":
                exist_postop_t1w = True
            elif volume_object.get_sequence_type_str() == "FLAIR":
                exist_postop_flair = True

    if exist_postop_t1ce and exist_postop_t1w:
        model_name = "MRI_GBM_Postop_FV_2p"
    if exist_postop_t1ce and exist_postop_t1w and exist_postop_flair:
        model_name = "MRI_GBM_Postop_FV_3p"
    if exist_postop_t1ce and exist_postop_t1w and exist_preop_t1:
        model_name = "MRI_GBM_Postop_FV_4p"
    if exist_postop_t1ce and exist_postop_t1w and exist_postop_flair and exist_preop_t1:
        model_name = "MRI_GBM_Postop_FV_5p"
    return model_name

def include_radiological_volume_classifier(pip: dict, pip_num_start: int) -> Tuple[dict, int]:
    pip_num_int = pip_num_start + 1
    pip_num = str(pip_num_int)
    pip[pip_num] = {}
    pip[pip_num]["task"] = 'Classification'
    pip[pip_num]["inputs"] = {}
    pip[pip_num]["target"] = ["MRSequence"]
    pip[pip_num]["model"] = 'MRI_SequenceClassifier'
    pip[pip_num]["description"] = "Classification of the MRI sequence type for all input scans"
    download_model(model_name='MRI_SequenceClassifier')

    return pip, pip_num_int