import shutil

import time
from aenum import Enum, unique
from typing import Union
import os
import SimpleITK as sitk
import numpy as np
import rt_utils


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

    # @TODO. Have encountered FLAIR images with integer values in [0, 255], from DICOM conversion, which will be
    # failed associated as annotations...
    if len(np.unique(array)) > 255 or np.max(array) > 255 or np.min(array) < -1:
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


def convert_results_as_dicom_rtstruct(patient_parameters):
    # @TODO. Preferences option to always dump the RTStruct additionally.
    # Create one structure for each MRI, and save on disk only if not empty.

    ts_uids = patient_parameters.get_all_timestamps_uids()
    for ts in ts_uids:
        image_uids = patient_parameters.get_all_mri_volumes_for_timestamp(timestamp_uid=ts)
        for im_uid in image_uids:
            image_object = patient_parameters.get_mri_by_uid(mri_uid=im_uid)
            linked_annotation_uids = patient_parameters.get_all_annotations_for_mri(mri_volume_uid=im_uid)
            existing_annotations = len(linked_annotation_uids) != 0
            if existing_annotations:
                # @TODO. Should the original DICOM files be used, or just convert on the fly with the existing
                # DICOM tags, already stored in the Image structure?
                existing_dicom = image_object.get_dicom_metadata() is not None
                dicom_folderpath = os.path.join(os.path.dirname(image_object.get_usable_input_filepath()),
                                                image_object.display_name, 'volume')
                os.makedirs(dicom_folderpath, exist_ok=True)
                original_image_sitk = sitk.ReadImage(image_object.get_usable_input_filepath())
                direction = original_image_sitk.GetDirection()
                writer = sitk.ImageFileWriter()
                writer.KeepOriginalImageUIDOn()
                modification_time = time.strftime("%H%M%S")
                modification_date = time.strftime("%Y%m%d")

                if not existing_dicom:
                    series_tag_values = [("0010|0020", patient_parameters.unique_id),  # Patient ID
                                         ("0008|0031", modification_time),  # Series Time
                                         ("0008|0021", modification_date),  # Series Date
                                         ("0008|0008", "DERIVED\\SECONDARY"),  # Image Type
                                         ("0020|000e", "0000000." + modification_date + ".1" + modification_time), # Series Instance UID
                                         ("0020|0037", '\\'.join(map(str, (
                                         direction[0], direction[3], direction[6],  # Image Orientation (Patient)
                                         direction[1], direction[4], direction[7])))),
                                         ("0008|103e", "Created-Raidionics")]  # Series Description
                else:
                    # @TODO. Bug when using all the existing tags, not properly loadable in 3D Slicer...
                    original_series_tag_values = image_object.get_dicom_metadata()
                    # original_series_tag_values["0020|0037"] = '\\'.join(map(str, (
                    #                      direction[0], direction[3], direction[6],  # Image Orientation (Patient)
                    #                      direction[1], direction[4], direction[7])))
                    # original_series_tag_values["0008|103e"] = "Created-Raidionics"
                    # original_series_tag_values["0008|0008"] = "DERIVED\\SECONDARY"
                    # original_series_tag_values["0008|0031"] = modification_time
                    # original_series_tag_values["0008|0021"] = modification_date
                    # original_series_tag_values = list(original_series_tag_values.items())
                    series_tag_values = [("0010|0020", original_series_tag_values['0010|0020']),  # Patient ID
                                         ("0008|0031", modification_time),  # Series Time
                                         ("0008|0021", modification_date),  # Series Date
                                         ("0008|0008", "DERIVED\\SECONDARY"),  # Image Type
                                         ("0020|000e", original_series_tag_values['0020|000e'] + modification_date + ".1" + modification_time), # Series Instance UID
                                         ("0020|0037", '\\'.join(map(str, (
                                         direction[0], direction[3], direction[6],  # Image Orientation (Patient)
                                         direction[1], direction[4], direction[7])))),
                                         ("0008|103e", "Created-Raidionics")]  # Series Description

                # Write slices to output directory
                list(map(lambda i: dicom_write_slice(writer, series_tag_values, original_image_sitk, i,
                                                     dicom_folderpath), range(original_image_sitk.GetDepth())))

                # @TODO. Should we check that it already exists on disk, to append to it, rather than building it from scratch?
                rt_struct = rt_utils.RTStructBuilder.create_new(dicom_series_path=dicom_folderpath)
                for anno_uid in linked_annotation_uids:
                    anno = patient_parameters.get_annotation_by_uid(annotation_uid=anno_uid)
                    anno_sitk = sitk.ReadImage(anno.raw_input_filepath)
                    anno_roi = sitk.GetArrayFromImage(anno_sitk).transpose((1, 2, 0)).astype('bool')
                    rt_struct.add_roi(mask=anno_roi, color=anno.get_display_color()[0:3],
                                      name=anno.get_annotation_class_str())
                # @TODO. Should also include the atlas structures later on?

                dest_rt_struct_filename = os.path.join(os.path.dirname(image_object.get_usable_input_filepath()),
                                                       image_object.display_name,
                                                       image_object.display_name + '_structures')
                rt_struct.save(dest_rt_struct_filename)
            else:
                # Skipping radiological volumes without any annotation linked to.
                pass


def dicom_write_slice(writer, series_tag_values, new_img, i, dest_dir):
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
