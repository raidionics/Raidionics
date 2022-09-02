from .Utils.configuration_parser import ResourcesConfiguration
from .NeuroDiagnosis.neuro_diagnostics import *
from .MediastinumDiagnosis.mediastinum_diagnostics import *
import logging


def run_rads(config_filename: str, logging_filename: str = None) -> None:
    """

    """
    ResourcesConfiguration.getInstance().set_environment(config_path=config_filename)
    if logging_filename:
        logging.basicConfig(filename=logging_filename, filemode='a',
                            format="%(asctime)s ; %(name)s ; %(levelname)s ; %(message)s", datefmt='%d/%m/%Y %H.%M')
        logging.getLogger().setLevel(logging.DEBUG)

    input_filename = ResourcesConfiguration.getInstance().input_volume_filename
    logging.info("Starting diagnosis for file: {}.".format(input_filename))
    start = time.time()
    diagnosis_task = ResourcesConfiguration.getInstance().diagnosis_task

    if diagnosis_task == 'neuro_diagnosis':
        runner = NeuroDiagnostics(input_filename=input_filename)
        runner.run()
    elif diagnosis_task == 'mediastinum_diagnosis':
        runner = MediastinumDiagnostics(input_filename=input_filename)
        runner.run()
    else:
        raise AttributeError('The provided diagnosis task {} is not supported yet.'.format(diagnosis_task))
    logging.info('Total time for generating the standardized report: {} seconds.'.format(time.time() - start))
