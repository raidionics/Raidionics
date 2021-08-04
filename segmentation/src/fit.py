from segmentation.src.Utils.configuration_parser import *
from segmentation.src.PreProcessing.pre_processing import run_pre_processing
from segmentation.src.Inference.predictions import run_predictions
from segmentation.src.Inference.predictions_reconstruction import reconstruct_post_predictions
from segmentation.src.Utils.io import dump_predictions

MODELS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../', 'resources/models')
sys.path.insert(1, MODELS_PATH)


def predict(input_filename, output_path, selected_model, brain_mask_filename=None):
    """

    """
    pre_processing_parameters = PreProcessingParser(model_name=selected_model)
    valid_extensions = ['.h5', '.hd5', '.hdf5', '.hdf', '.ckpt']
    model_path = ''
    for e, ext in enumerate(valid_extensions):
        model_path = os.path.join(MODELS_PATH, selected_model, 'model' + ext)
        if os.path.exists(model_path):
            break

    if not os.path.exists(model_path):
        raise ValueError('Could not find any model on Docker image matching the requested type \'{}\'.'.format(selected_model))

    nib_volume, resampled_volume, data, crop_bbox = run_pre_processing(filename=input_filename,
                                                                       pre_processing_parameters=pre_processing_parameters,
                                                                       storage_prefix=output_path,
                                                                       brain_mask_filename=brain_mask_filename)
    predictions = run_predictions(data=data, model_path=model_path, parameters=pre_processing_parameters)
    final_predictions = reconstruct_post_predictions(predictions=predictions, parameters=pre_processing_parameters,
                                                     crop_bbox=crop_bbox, nib_volume=nib_volume, resampled_volume=resampled_volume)
    dump_predictions(predictions=final_predictions, parameters=pre_processing_parameters, nib_volume=nib_volume,
                     storage_prefix=output_path)
