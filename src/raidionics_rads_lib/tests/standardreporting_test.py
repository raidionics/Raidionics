import os
import shutil
import configparser
import logging
import sys
import subprocess
import traceback

try:
    import gdown
    if int(gdown.__version__.split('.')[0]) < 4 or int(gdown.__version__.split('.')[1]) < 4:
        subprocess.check_call([sys.executable, "-m", "pip", "install", 'gdown==4.4.0'])
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'gdown==4.4.0'])
    import gdown


def standardreporting_test():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info("Running standard reporting unit test.\n")
    logging.info("Downloading unit test resources.\n")
    test_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'unit_tests_results_dir')
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)

    try:
        test_image_url = 'https://drive.google.com/uc?id=1GIQUku7hTl9EmjJ9r32kIh9SmCxdTR_u'  # MNI T1 atlas
        brain_model_url = 'https://drive.google.com/uc?id=1d6FeuQsLWliW_0-rqN8VL82l6AlD3kRs'  # Brain model
        test_model_url = 'https://drive.google.com/uc?id=1PfM7RAi5JGEPFqLcYOlZY1JJ85QmNYkU'  # Meningioma model

        archive_dl_dest = os.path.join(test_dir, 'inference_volume.zip')
        gdown.cached_download(url=test_image_url, path=archive_dl_dest)
        gdown.extractall(path=archive_dl_dest, to=test_dir)

        archive_dl_dest = os.path.join(test_dir, 'brain-model.zip')
        gdown.cached_download(url=brain_model_url, path=archive_dl_dest)
        gdown.extractall(path=archive_dl_dest, to=test_dir)

        archive_dl_dest = os.path.join(test_dir, 'model.zip')
        gdown.cached_download(url=test_model_url, path=archive_dl_dest)
        gdown.extractall(path=archive_dl_dest, to=test_dir)
    except Exception as e:
        logging.error("Error during resources download with: \n {}.\n".format(traceback.format_exc()))
        shutil.rmtree(test_dir)
        raise ValueError("Error during resources download.\n")

    logging.info("Preparing configuration file.\n")
    try:
        rads_config = configparser.ConfigParser()
        rads_config.add_section('Default')
        rads_config.set('Default', 'task', 'neuro_diagnosis')
        rads_config.set('Default', 'caller', 'raidionics')
        rads_config.add_section('System')
        rads_config.set('System', 'gpu_id', "-1")
        rads_config.set('System', 'input_filename', os.path.join(test_dir, 'patient_mni.nii'))
        rads_config.set('System', 'output_folder', test_dir)
        rads_config.set('System', 'model_folder', os.path.join(test_dir, 'MRI_Meningioma'))
        rads_config.add_section('Runtime')
        rads_config.set('Runtime', 'reconstruction_method', 'thresholding')
        rads_config.set('Runtime', 'reconstruction_order', 'resample_first')
        rads_config.add_section('Neuro')
        rads_config.set('Neuro', 'cortical_features', 'MNI')
        rads_config.set('Neuro', 'subcortical_features', '')
        rads_config_filename = os.path.join(test_dir, 'rads_config.ini')
        with open(rads_config_filename, 'w') as outfile:
            rads_config.write(outfile)

        logging.info("Standardized reporting CLI unit test started.\n")
        try:
            import platform
            if platform.system() == 'Windows':
                subprocess.check_call(['raidionicsrads',
                                       '{config}'.format(config=rads_config_filename),
                                       '--verbose', 'debug'], shell=True)
            else:
                subprocess.check_call(['raidionicsrads',
                                       '{config}'.format(config=rads_config_filename),
                                       '--verbose', 'debug'])
        except Exception as e:
            logging.error("Error during Standardized reporting CLI unit test with: \n {}.\n".format(traceback.format_exc()))
            shutil.rmtree(test_dir)
            raise ValueError("Error during Standardized reporting CLI unit test.\n")

        logging.info("Collecting and comparing results.\n")
        report_filename = os.path.join(test_dir, 'neuro_standardized_report.json')
        if not os.path.exists(report_filename):
            logging.error("Standardized reporting CLI unit test failed, no report was generated.\n")
            shutil.rmtree(test_dir)
            raise ValueError("Standardized reporting CLI unit test failed, no report was generated.\n")
        logging.info("Standardized reporting CLI unit test succeeded.\n")

        logging.info("Running standardized reporting unit test.\n")
        from raidionicsrads.compute import run_rads
        run_rads(rads_config_filename)

        logging.info("Collecting and comparing results.\n")
        report_filename = os.path.join(test_dir, 'neuro_standardized_report.json')
        if not os.path.exists(report_filename):
            logging.error("Standardized reporting unit test failed, no report was generated.\n")
            shutil.rmtree(test_dir)
            raise ValueError("Standardized reporting unit test failed, no report was generated.\n")
    except Exception as e:
        logging.error("Error during standardized reporting unit test with: \n {}.\n".format(traceback.format_exc()))
        shutil.rmtree(test_dir)
        raise ValueError("Error during standardized reporting unit test with.\n")

    logging.info("Standard reporting unit test succeeded.\n")
    shutil.rmtree(test_dir)


standardreporting_test()
