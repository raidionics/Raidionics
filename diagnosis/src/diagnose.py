from diagnosis.src.Utils.configuration_parser import ResourcesConfiguration
from diagnosis.src.NeuroDiagnosis.neuro_diagnostics import *


def diagnose(input_filename, input_segmentation):
    """

    """
    runner = NeuroDiagnostics(input_filename=input_filename, input_segmentation=input_segmentation)
    runner.run()

