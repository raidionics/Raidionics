import numpy as np
import operator
import json


class MediastinumDiagnosisParameters:
    """
    Singleton class to have access from anywhere in the code at the various parameters linked to a mediastinum diagnosis.
    """
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if MediastinumDiagnosisParameters.__instance == None:
            MediastinumDiagnosisParameters()
        return MediastinumDiagnosisParameters.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if MediastinumDiagnosisParameters.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            MediastinumDiagnosisParameters.__instance = self
            self.statistics = {}

    def setup_lymphnodes(self, nb_elements):
        self.lymph_nodes_count = nb_elements
        self.statistics['LymphNodes'] = {}
        self.statistics['LymphNodes']['Overall'] = None
        for p in range(nb_elements):
            self.statistics['LymphNodes'][str(p+1)] = LymphNodeStatistics()

    def to_txt(self, filename):
        pfile = open(filename, 'a')
        pfile.write('######### Clinical report #########\n')

        pfile.close()
        return

    def to_json(self, filename):
        param_json = {}
        param_json['Overall'] = {}
        param_json['Overall']['Lymphnodes_count'] = self.lymph_nodes_count

        param_json['LymphNodes'] = {}
        for p in range(self.lymph_nodes_count):
            tumor_component = str(p + 1)
            param_json['LymphNodes'][tumor_component] = {}
            param_json['LymphNodes'][tumor_component]['Volume'] = self.statistics['LymphNodes'][tumor_component].volume
            param_json['LymphNodes'][tumor_component]['Axis_diameters'] = self.statistics['LymphNodes'][tumor_component].axis_diameters

        with open(filename, 'w', newline='\n') as outfile:
            json.dump(param_json, outfile)
        return


class LymphNodeStatistics():
    def __init__(self):
        self.laterality = None
        self.volume = None
        self.axis_diameters = []
        self.stations_overlap = {}
