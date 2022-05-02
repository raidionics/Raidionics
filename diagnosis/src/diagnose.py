from diagnosis.src.NeuroDiagnosis.neuro_diagnostics import *


def diagnose(input_filename, input_segmentation, tumor_type, preprocessing_scheme):
    """

    """
    runner = NeuroDiagnostics(input_filename=input_filename, input_segmentation=input_segmentation,
                              preprocessing_scheme=preprocessing_scheme)
    runner.prepare_to_run()
    if tumor_type and tumor_type.strip() != "":
        runner.tumor_type = tumor_type
    runner.run()


