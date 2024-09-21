import logging
import os
import shutil
from pathlib import PurePath
import gdown
import traceback
import pandas as pd
import hashlib
import zipfile
import requests
from os.path import expanduser
from packaging import version
from utils.software_config import SoftwareConfigResources
from utils.data_structures.UserPreferencesStructure import UserPreferencesStructure


def get_available_cloud_models_list():
    cloud_models_list = []
    cloud_models_list_url = 'https://drive.google.com/uc?id=1vRUr0VXgnDFNq7AlB5ILyBCmW_sGuciP'
    cloud_models_list_filename = os.path.join(expanduser("~"), '.raidionics', 'resources', 'models',
                                              'cloud_models_list.csv')
    if os.name == 'nt':
        script_path_parts = list(PurePath(expanduser("~")).parts[:] + ('.raidionics', 'resources', 'models',
                                                                       'cloud_models_list.csv'))
        cloud_models_list_filename = PurePath()
        for x in script_path_parts:
            cloud_models_list_filename = cloud_models_list_filename.joinpath(x)

    # Initial v1.0/v1.1 - to deprecate!
    if version.parse(SoftwareConfigResources.getInstance().software_version) < version.parse("1.2"):
        try:
            os.makedirs(os.path.dirname(cloud_models_list_filename), exist_ok=True)
            # Always downloading the models list, to make sure the latest models are always available.
            gdown.download(url=cloud_models_list_url, output=cloud_models_list_filename)
        except Exception as e:
            print('Impossible to access the cloud models list on Google Drive.\n')
            print('{}'.format(traceback.format_exc()))
            logging.warning('Impossible to access the cloud models list on Google Drive with: \n {}'.format(traceback.format_exc()))
    elif version.parse(SoftwareConfigResources.getInstance().software_version) >= version.parse("1.2"):
        cloud_models_list_url = 'https://github.com/raidionics/Raidionics-models/releases/download/1.2.0/raidionics_cloud_models_list_github.csv'
        try:
            os.makedirs(os.path.dirname(cloud_models_list_filename), exist_ok=True)
            headers = {}
            response = requests.get(cloud_models_list_url, headers=headers, stream=True)
            response.raise_for_status()

            if response.status_code == requests.codes.ok:
                with open(cloud_models_list_filename, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1048576):
                        f.write(chunk)
        except Exception as e:
            print('Impossible to access the cloud models list on Github.\n')
            print('{}'.format(traceback.format_exc()))
            logging.warning('Impossible to access the cloud models list on Github with: \n {}'.format(traceback.format_exc()))

    if not os.path.exists(cloud_models_list_filename):
        logging.error('The cloud models list does not exist on disk at: {}'.format(cloud_models_list_filename))
    cloud_models_list = pd.read_csv(cloud_models_list_filename)
    return cloud_models_list


def download_model_ori(model_name):
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
            if not os.path.exists(models_archive_path) or (hashlib.md5(open(models_archive_path, 'rb').read()).hexdigest() != md5 and UserPreferencesStructure.getInstance().active_model_update):
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
            logging.error("[Software error] No model exists with the provided name: {}.\n".format(model_name))
    except Exception as e:
        logging.error('[Software error] Issue trying to collect the latest {} model with: \n {}'.format(model_name,
                                                                                       traceback.format_exc()))


def download_model(model_name: str):
    """
    Utilitarian method for downloading a model, hosted on Github, if no local version can be found or if the local version
    is outdated compared to the remote version.

    Parameters
    ----------
    model_name: str
        Unique name for the model to download, as specified inside the cloud models list file (.csv).
    """
    download_state = False
    extract_state = False
    try:
        cloud_models_list = get_available_cloud_models_list()
        if model_name in list(cloud_models_list['Model'].values):
            model_params = cloud_models_list.loc[cloud_models_list['Model'] == model_name]
            url = model_params['link'].values[0]
            md5 = model_params['sum'].values[0]
            tmp_dep = model_params['dependencies'].values[0]
            dep = list(tmp_dep.strip().split(';')) if tmp_dep == tmp_dep else []
            models_path = os.path.join(expanduser('~'), '.raidionics', 'resources', 'models')
            os.makedirs(models_path, exist_ok=True)
            models_archive_path = os.path.join(expanduser('~'), '.raidionics', 'resources', 'models',
                                               '.cache', model_name + '.zip')
            os.makedirs(os.path.dirname(models_archive_path), exist_ok=True)

            if not os.path.exists(models_archive_path) or\
                    (hashlib.md5(open(models_archive_path, 'rb').read()).hexdigest() != md5 and UserPreferencesStructure.getInstance().active_model_update):
                download_state = True

            if download_state:
                if os.path.exists(models_archive_path):
                    # Just in case, deleting the old cached archive, if a new one is to be downloaded
                    os.remove(models_archive_path)
                headers = {}

                response = requests.get(url, headers=headers, stream=True)
                response.raise_for_status()

                if response.status_code == requests.codes.ok:
                    with open(models_archive_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=1048576):
                            f.write(chunk)
                    extract_state = True
            else:
                zip_content = zipfile.ZipFile(models_archive_path).namelist()
                for f in zip_content:
                    if not os.path.exists(os.path.join(models_path, f)):
                        extract_state = True

            if extract_state:
                # Perform a force deletion of the model folder, if already existing, and before extraction
                # to avoid mixing files.
                if os.path.exists(os.path.join(models_path, model_name)):
                    shutil.rmtree(os.path.join(models_path, model_name))
                with zipfile.ZipFile(models_archive_path, 'r') as zip_ref:
                    zip_ref.extractall(models_path)

            for d in dep:
                if d == d:
                    download_model(d)
        else:
            logging.error("[Software error] No model exists with the provided name: {}.\n".format(model_name))
    except Exception as e:
        logging.error('[Software error] Issue trying to collect the latest {} model with: \n {}'.format(model_name,
                                                                                       traceback.format_exc()))
