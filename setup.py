import os
import gdown


def setup_repository():
    # Downloading, extracting atlases.
    atlases_url = '' # 'https://drive.google.com/uc?id=1QJZWF9CzgOiYzjzsRSu2LOkrzi2S6j_U'
    atlases_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'Atlases')
    os.makedirs(atlases_path, exist_ok=True)
    md5 = ''
    atlases_archive_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'atlases.zip')
    gdown.cached_download(url=atlases_url, path=atlases_archive_path, md5=md5)
    gdown.extractall(path=atlases_archive_path, to=atlases_path)
    os.remove(atlases_archive_path)

    # Downloading, extracting models.
    models_url = '' # 'https://drive.google.com/uc?id=1QJZWF9CzgOiYzjzsRSu2LOkrzi2S6j_U'
    models_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'models')
    os.makedirs(models_path, exist_ok=True)
    md5 = ''
    models_archive_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'models.zip')
    gdown.cached_download(url=models_url, path=models_archive_path, md5=md5)
    gdown.extractall(path=models_archive_path, to=models_path)
    os.remove(models_archive_path)


setup_repository()
