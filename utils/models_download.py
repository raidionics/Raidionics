import os
import gdown
import traceback
import pandas as pd
from os.path import expanduser

def get_available_cloud_models_list():
    cloud_models_list = []
    cloud_models_list_url = 'https://drive.google.com/uc?id=1vRUr0VXgnDFNq7AlB5ILyBCmW_sGuciP'
    try:
        # cloud_models_list_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../resources', 'models',
        #                                           'cloud_models_list.csv')
        cloud_models_list_filename = os.path.join(expanduser("~"), '.neurorads', 'resources/models',
                                                  'cloud_models_list.csv')
        gdown.cached_download(url=cloud_models_list_url, path=cloud_models_list_filename,
                              md5='1545f2cab1df9a6d3fb561c5e497b89f')
        cloud_models_list = pd.read_csv(cloud_models_list_filename)
    except Exception as e:
        print('Impossible to access the cloud models list.\n')
        print('{}'.format(traceback.format_exc()))

    return cloud_models_list


def download_model(model_name):
    cloud_models_list = get_available_cloud_models_list()
    if model_name in list(cloud_models_list['Model'].values):
        model_params = cloud_models_list.loc[cloud_models_list['Model'] == model_name]
        url = model_params['link'].values[0]
        md5 = model_params['sum'].values[0]
        dep = list(model_params['dependencies'].values)
        #models_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../resources', 'models')
        models_path = os.path.join(expanduser('~'), '.neurorads', 'resources', 'models')
        os.makedirs(models_path, exist_ok=True)
        # models_archive_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../resources', 'models',
        #                                    '.cache', model_name + '.zip')
        models_archive_path = os.path.join(expanduser('~'), '.neurorads', 'resources', 'models',
                                           '.cache', model_name + '.zip')
        os.makedirs(os.path.dirname(models_archive_path), exist_ok=True)
        gdown.cached_download(url=url, path=models_archive_path, md5=md5)
        gdown.extractall(path=models_archive_path, to=models_path)
        # os.remove(models_archive_path)

        for d in dep:
            if d == d:
                download_model(d)
    else:
        print("No model exists with the provided name: {}.\n".format(model_name))
