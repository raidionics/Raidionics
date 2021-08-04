from diagnosis.src.NeuroDiagnosis.neuro_diagnostics import *


def diagnose(input_filename, input_segmentation, preprocessing_scheme):
    """

    """
    runner = NeuroDiagnostics(input_filename=input_filename, input_segmentation=input_segmentation,
                              preprocessing_scheme=preprocessing_scheme)
    runner.run()

