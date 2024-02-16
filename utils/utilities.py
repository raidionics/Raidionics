import logging
import shutil

from copy import deepcopy
from typing import List, Tuple
import time
from aenum import Enum, unique
from typing import Union
import os
import SimpleITK as sitk
import numpy as np


def get_type_from_string(enum_type: Enum, string: str) -> Union[str, int]:
    if type(string) == str:
        for i in range(len(list(enum_type))):
            #if string == list(EnumType)[i].name:
            if string == str(list(enum_type)[i]):
                return list(enum_type)[i]
        return -1
    elif type(string) == enum_type:
        return string
    else: #Unmanaged input type
        return -1


def input_file_category_disambiguation(input_filename: str) -> str:
    """
    Identifying whether the volume stored on disk under input_filename contains a raw MRI volume or is an integer-like
    volume with labels.
    The category belongs to [MRI, Annotation].

    Parameters
    ----------
    input_filename: str
        Disk location of the volume to disambiguate.

    Returns
    ----------
    str
        Human-readable category identified for the input.
    """
    category = None
    reader = sitk.ImageFileReader()
    reader.SetFileName(input_filename)
    image = reader.Execute()
    image_type = image.GetPixelIDTypeAsString()
    array = sitk.GetArrayFromImage(image)

    if len(np.unique(array)) > 255 or np.max(array) > 255 or np.min(array) < -1:
        category = "MRI"
    # If the input radiological volume has values within [0, 255] only. Empirical solution for now, since less than
    # 10 classes are usually handle at any given time.
    elif len(np.unique(array)) >= 25:
        category = "MRI"
    else:
        category = "Annotation"
    return category


def input_file_type_conversion(input_filename: str, output_folder: str) -> str:
    # Always converting the input file to nifti (if possible), otherwise will be discarded.
    # Saving anyway a correct nifti file inside the raidionics patient folder, for use in the backend.
    # @TODO. Do we catch a potential .seg file that would be coming from 3D Slicer for annotations?
    pre_file_extension = os.path.basename(input_filename).split('.')[0]
    file_extension = '.'.join(os.path.basename(input_filename).split('.')[1:])
    filename = input_filename
    if file_extension != 'nii' and file_extension != 'nii.gz':
        input_sitk = sitk.ReadImage(input_filename)
        nifti_outfilename = os.path.join(output_folder, pre_file_extension + '.nii.gz')
        sitk.WriteImage(input_sitk, nifti_outfilename)
        filename = nifti_outfilename
    else:
        filename = os.path.join(output_folder, os.path.basename(input_filename))
        if input_filename != filename and not os.path.exists(filename):
            shutil.copyfile(input_filename, filename)
        elif input_filename != filename and os.path.exists(filename):
            # In case of DICOM conversion, multiple files might have the same filename, hence the check and renaming.
            new_filename = os.path.join(output_folder, str(np.random.randint(0, 10000)) + "_" +
                                        os.path.basename(input_filename))
            while os.path.exists(new_filename):
                new_filename = os.path.join(output_folder, str(np.random.randint(0, 10000)) + "_" +
                                            os.path.basename(input_filename))
            shutil.copyfile(input_filename, new_filename)
            filename = new_filename

    return filename


def dicom_write_slice(writer: sitk.ImageFileWriter, series_tag_values: List[Tuple[str, str]], new_img: sitk.Image,
                      i: int, dest_dir: str) -> None:
    """
    Code snippet to save a SimpleITK Image object as DICOM, taken from
    https://simpleitk.readthedocs.io/en/v1.2.2/Examples/DicomSeriesFromArray/Documentation.html

    Parameters
    ----------
    writer: sitk.ImageFileWriter
        SimpleITK object performing the DICOM writing on disk.
    series_tag_values: List[Tuple[str, str]]
        DICOM metadata to store in the newly created DICOM object
    new_img: sitk.Image
        Radiological volume to store on disk as DICOM
    i: int
        Index of the current slice in the 3D radiological volume
    dest_dir: str
        Destination location on disk where the DICOM volume should be stored
    """
    image_slice = new_img[:, :, i]

    # Tags shared by the series.
    list(map(lambda tag_value: image_slice.SetMetaData(tag_value[0], tag_value[1]), series_tag_values))

    # Slice specific tags.
    image_slice.SetMetaData("0008|0012", time.strftime("%Y%m%d"))  # Instance Creation Date
    image_slice.SetMetaData("0008|0013", time.strftime("%H%M%S"))  # Instance Creation Time

    # Setting the type to CT preserves the slice location.
    image_slice.SetMetaData("0008|0060", "CT")  # set the type to CT so the thickness is carried over

    # (0020, 0032) image position patient determines the 3D spacing between slices.
    image_slice.SetMetaData("0020|0032", '\\'.join(map(str, new_img.TransformIndexToPhysicalPoint((0, 0, i)))))  # Image Position (Patient)
    image_slice.SetMetaData("0020,0013", str(i))  # Instance Number

    # Write to the output directory and add the extension dcm, to force writing in DICOM format.
    writer.SetFileName(os.path.join(dest_dir, str(i)+'.dcm'))
    writer.Execute(image_slice)
