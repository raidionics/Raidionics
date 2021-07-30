# import os, sys, math
# from tensorflow.python.keras.models import load_model
# import nibabel as nib
# from nibabel.processing import *
# from nibabel import four_to_three
# from segmentation.src.Utils.volume_utilities import *
# from segmentation.src.Utils.configuration_parser import *
#
# MODELS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../', 'models')
# print(MODELS_PATH)
# sys.path.insert(1, MODELS_PATH)
#
#
# def predict_MR(input_volume_path, output_mask_path, pre_processing_parameters, model_path):
#     predictions_type = 'binary'
#     print("Extracting data...")
#     nib_volume = nib.load(input_volume_path)
#     if len(nib_volume.shape) > 3:
#         if len(nib_volume.shape) == 4: #Common problem
#             nib_volume = four_to_three(nib_volume)[0]
#         else: #DWI volumes
#             nib_volume = nib.Nifti1Image(nib_volume.get_data()[:, :, :, 0, 0], affine=nib_volume.affine)
#
#     print("Pre-processing...")
#     # Normalize spacing
#     spacing = np.min(nib_volume.header.get_zooms())
#     resampled_volume = resample_to_output(nib_volume, [spacing, spacing, spacing], order=1)
#     data = resampled_volume.get_data()
#     resampled_shape = data.shape
#
#     # Normalize values
#     data = intensity_normalization(volume=data, parameters=pre_processing_parameters)
#     crop_bbox = None
#     if pre_processing_parameters.crop_background:
#         data, crop_bbox = crop_MR(data, parameters=pre_processing_parameters)
#     MR = resize_volume(data, pre_processing_parameters, order=1)
#     del data
#
#     print("Loading model...")
#     model = load_model(model_path, compile=False)
#
#     print("Predicting...")
#     # split data into chunks and predict
#     slab_size = pre_processing_parameters.slab_size
#
#     if pre_processing_parameters.swap_training_input:
#         MR = np.transpose(MR, axes=(1, 0, 2))
#
#     print('Pre-proc shape: {}'.format(MR.shape))
#     final_result = np.zeros_like(MR)
#     MR = np.expand_dims(MR, axis=-1)
#     if pre_processing_parameters.non_overlapping:
#         count = 0
#         scale = math.ceil(MR.shape[-2]/slab_size)
#         for chunk in range(scale):
#             slab = np.zeros(MR.shape[:-2] + (slab_size, ), dtype=np.float32)
#             tmp = MR[:, :, int(chunk*slab_size):int((chunk + 1)*slab_size), 0]
#             slab[:, :, :tmp.shape[2]] = tmp
#             slab = np.expand_dims(np.expand_dims(slab, axis=0), axis=-1)
#             slab = model.predict(slab)
#             final_result[..., int(chunk*slab_size):int((chunk + 1)*slab_size)] = slab[0, :, :, :tmp.shape[-1], 1]
#             print(count)
#             count += 1
#         del tmp
#     else:
#         half_slab_size = int(slab_size/2)
#         for slice in range(half_slab_size, MR.shape[2] - slab_size):
#             slab_MR = MR[:, :, slice - half_slab_size:slice + half_slab_size, 0]
#             if np.sum(slab_MR > 0.1) == 0:
#                 continue
#
#             result = model.predict(np.reshape(slab_MR, (1, MR.shape[0], MR.shape[1], slab_size, 1)))
#             final_result[:, :, slice] = result[0, :, :, half_slab_size, 1]
#
#     print('Begin predictions reconstruction in input space.')
#     if predictions_type == 'binary':
#         final_result = (final_result >= pre_processing_parameters.predictions_confidence_thresholds[0]).astype(np.uint8)  # convert to binary volume
#     # else:
#     #     data = final_result
#
#     if pre_processing_parameters.swap_training_input:
#         final_result = np.transpose(final_result, axes=(1, 0, 2))  # undo transpose
#
#     # Undo resizing (which is performed in function crop())
#     if crop_bbox is not None:
#         final_result = resize(final_result, (crop_bbox[3]-crop_bbox[0], crop_bbox[4]-crop_bbox[1], crop_bbox[5]-crop_bbox[2]),
#                       order=0, preserve_range=True)
#         # Undo cropping (which is performed in function crop())
#         new_data = np.zeros(resampled_shape, dtype=np.float32)
#         new_data[crop_bbox[0]:crop_bbox[3], crop_bbox[1]:crop_bbox[4], crop_bbox[2]:crop_bbox[5]] = final_result
#     else:
#         # @TODO: should also resize when there is no bbox!!
#         new_data = resize(final_result, resampled_volume.get_data().shape, order=0, preserve_range=True)
#
#     del final_result
#
#     print("Writing to file...")
#     # Create NIFTI image using the resampled_volume header as template
#     img = nib.Nifti1Image(new_data, affine=resampled_volume.affine)
#     # Save segmentation data adjusted to original size
#     resampled_lab = resample_from_to(img, nib_volume, order=0)
#
#     if nib_volume.shape != resampled_lab.shape:
#         print('Aborting -- dimensions are mismatching between input and obtained labels.')
#
#     print('Type of the saved labels: {}'.format(img.get_data_dtype()))
#     nib.save(resampled_lab, output_mask_path)
#     print(input_volume_path)
#     print(output_mask_path)
