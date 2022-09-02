import configparser
import os
import sys
import datetime
import time
from .configuration_parser import ResourcesConfiguration


def collect_segmentation_model_parameters(model_name):
    model_path = os.path.join(ResourcesConfiguration.getInstance().sintef_segmenter_path, 'resources', 'models', model_name)
    model_config_path = os.path.join(model_path, 'pre_processing.ini')
    model_config = configparser.ConfigParser()
    model_config.read(model_config_path)

    training_class_names = []
    training_class_thresholds = []

    if model_config.has_option('Training', 'classes'):
        if model_config['Training']['classes'].split('#')[0].strip() != '':
            training_class_names = [x.strip() for x in model_config['Training']['classes'].split('#')[0].split(',')]

    if model_config.has_option('Training', 'optimal_thresholds'):
        if model_config['Training']['optimal_thresholds'].split('#')[0].strip() != '':
            training_class_thresholds = [float(x.strip()) for x in model_config['Training']['optimal_thresholds'].split('#')[0].split(',')]

    return training_class_names, training_class_thresholds


def update_segmentation_runtime_parameters(section, key, value):
    runtime_path = os.path.join(ResourcesConfiguration.getInstance().sintef_segmenter_path, 'resources', 'data')
    runtime_config_path = os.path.join(runtime_path, 'runtime_config.ini')
    runtime_config = configparser.ConfigParser()
    runtime_config.read(runtime_config_path)

    if runtime_config.has_option(section, key):
        runtime_config[section][key] = value

    with open(runtime_config_path, 'w') as configfile:
        runtime_config.write(configfile)
