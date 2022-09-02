import logging
from typing import Tuple, Any, List
import numpy as np
import nibabel as nib
from nibabel.processing import resample_to_output
from ..Utils.volume_utilities import intensity_normalization, resize_volume
from ..Utils.io import load_nifti_volume
from .mediastinum_clipping import mediastinum_clipping, mediastinum_clipping_DL
from .brain_clipping import crop_MR_background
from ..Utils.configuration_parser import ImagingModalityType
from ..Utils.configuration_parser import ConfigResources


def run_pre_processing(filename: str, pre_processing_parameters: ConfigResources,
                       storage_path: str) -> Tuple[nib.Nifti1Image, nib.Nifti1Image, np.ndarray, List[int]]:
    """

    Parameters
    ----------
    filename : str
        Filepath of the input volume (CT or MRI) to use.
    pre_processing_parameters : :obj:`ConfigResources`
        Loaded configuration specifying runtime parameters.
    storage_path: str
        Folder where the computed results should be stored.

    Returns
    -------
    nib.Nifti1Image
        Original Nifti object from loading the content of filename.
    nib.Nifti1Image
        Nifti object after conversion to a normalized space (resample_to_output).
    np.ndarray
        Fully preprocessed volume ready for inference.
    List[int]
        Indices of a bounding region within the preprocessed volume for additional cropping
         (e.g. coordinates around the brain or lungs).
         The bounding region is expressed as: [minx, miny, minz, maxx, maxy, maxz].
    """
    logging.debug("Preprocessing - Extracting input data.")
    nib_volume = load_nifti_volume(filename)

    logging.debug("Preprocessing - Resampling.")
    new_spacing = pre_processing_parameters.output_spacing
    if pre_processing_parameters.output_spacing == None:
        tmp = np.min(nib_volume.header.get_zooms())
        new_spacing = [tmp, tmp, tmp]

    library = pre_processing_parameters.preprocessing_library
    if library == 'nibabel':
        resampled_volume = resample_to_output(nib_volume, new_spacing, order=1)
        data = resampled_volume.get_data().astype('float32')

    logging.debug("Preprocessing - Clipping and intensity normalization.")
    crop_bbox = None
    if pre_processing_parameters.imaging_modality == ImagingModalityType.CT:
        # Exclude background
        if pre_processing_parameters.crop_background is not None and pre_processing_parameters.crop_background != 'false':
                #data, crop_bbox = mediastinum_clipping(volume=data, parameters=pre_processing_parameters)
                data, crop_bbox = mediastinum_clipping_DL(filename, data, new_spacing, storage_path, pre_processing_parameters)
        # Normalize values
        data = intensity_normalization(volume=data, parameters=pre_processing_parameters)
        # set intensity range
        mins, maxs = pre_processing_parameters.intensity_target_range
        data *= maxs  # @TODO: Modify it such that it handles scaling to i.e. [-1, -1]
    else:
        # Normalize values
        data = intensity_normalization(volume=data, parameters=pre_processing_parameters)
        # Exclude background
        if pre_processing_parameters.crop_background is not None:
            data, crop_bbox = crop_MR_background(filename, data, new_spacing, storage_path, pre_processing_parameters)

    logging.debug("Preprocessing - Volume resizing.")
    data = resize_volume(data, pre_processing_parameters.new_axial_size, pre_processing_parameters.slicing_plane,
                         order=1)

    if pre_processing_parameters.swap_training_input:
        data = np.transpose(data, axes=(1, 0, 2))

    return nib_volume, resampled_volume, data, crop_bbox
