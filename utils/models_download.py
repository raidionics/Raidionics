import logging
import os
import gdown
import traceback
import pandas as pd
import hashlib
import zipfile
from os.path import expanduser
from utils.software_config import SoftwareConfigResources


def get_available_cloud_models_list():
    cloud_models_list = []
    cloud_models_list_url = 'https://drive.google.com/uc?id=1vRUr0VXgnDFNq7AlB5ILyBCmW_sGuciP'  # Initial v1.0/v1.1
    if SoftwareConfigResources.getInstance().software_version == "1.2":
        cloud_models_list_url = 'https://drive.google.com/uc?id=12tFP9trt8CLS6UBfNpodlRUwfSqZJJNQ'
    try:
        cloud_models_list_filename = os.path.join(expanduser("~"), '.raidionics', 'resources/models',
                                                  'cloud_models_list.csv')
        os.makedirs(os.path.dirname(cloud_models_list_filename), exist_ok=True)
        # Always downloading the models list, to make sure the latest models are always available.
        gdown.download(url=cloud_models_list_url, output=cloud_models_list_filename)
        cloud_models_list = pd.read_csv(cloud_models_list_filename)
    except Exception as e:
        print('Impossible to access the cloud models list.\n')
        print('{}'.format(traceback.format_exc()))
        logging.warning('Impossible to access the cloud models list with: \n {}'.format(traceback.format_exc()))

    return cloud_models_list


def download_model(model_name):
    """
    @TODO. In case the model could not be downloaded, maybe depending on firewall/security issues (e.g., on Windows),
    an error message with "Cannot retrieve the public link of the file" will appear. This should be then shown in a
    QMessageBox to the user, with a message asking to go manually download and place the model where it should,
    providing the Google Drive link....

    """
    download_state = False
    extract_state = False
    try:
        cloud_models_list = get_available_cloud_models_list()
        if model_name in list(cloud_models_list['Model'].values):
            model_params = cloud_models_list.loc[cloud_models_list['Model'] == model_name]
            url = model_params['link'].values[0]
            md5 = model_params['sum'].values[0]
            dep = list(model_params['dependencies'].values)
            models_path = os.path.join(expanduser('~'), '.raidionics', 'resources', 'models')
            os.makedirs(models_path, exist_ok=True)
            models_archive_path = os.path.join(expanduser('~'), '.raidionics', 'resources', 'models',
                                               '.cache', model_name + '.zip')
            os.makedirs(os.path.dirname(models_archive_path), exist_ok=True)
            if not os.path.exists(models_archive_path) or (hashlib.md5(open(models_archive_path, 'rb').read()).hexdigest() != md5 and SoftwareConfigResources.getInstance().user_preferences.active_model_update):
                download_state = True

            if download_state:
                gdown.cached_download(url=url, path=models_archive_path, md5=md5)
                gdown.extractall(path=models_archive_path, to=models_path)
            else:
                zip_content = zipfile.ZipFile(models_archive_path).namelist()
                for f in zip_content:
                    if not os.path.exists(os.path.join(models_path, f)):
                        extract_state = True
                if extract_state:
                    gdown.extractall(path=models_archive_path, to=models_path)

            for d in dep:
                if d == d:
                    download_model(d)
        else:
            print("No model exists with the provided name: {}.\n".format(model_name))
            logging.error("No model exists with the provided name: {}.\n".format(model_name))
    except Exception as e:
        print('Issue trying to collect the latest {} model.\n'.format(model_name))
        print('{}'.format(traceback.format_exc()))
        logging.error('Issue trying to collect the latest {} model with: \n {}'.format(model_name,
                                                                                       traceback.format_exc()))
