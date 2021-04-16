import numpy as np
import operator
import json
import pandas as pd


class NeuroDiagnosisParameters:
    """
    Singleton class to have access from anywhere in the code at the various parameters linked to a neuro diagnosis.
    """
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if NeuroDiagnosisParameters.__instance == None:
            NeuroDiagnosisParameters()
        return NeuroDiagnosisParameters.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if NeuroDiagnosisParameters.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            NeuroDiagnosisParameters.__instance = self

    def setup(self, type, tumor_elements):
        self.tumor_presence_state = False
        self.tumor_type = None
        self.tumor_multifocal = False
        self.tumor_parts = tumor_elements
        self.tumor_multifocal_distance = -1.

        if tumor_elements != 0:
            self.tumor_presence_state = True
            self.tumor_type = type
            if tumor_elements > 1:
                self.tumor_multifocal = True

        self.statistics = {}
        self.statistics['Main'] = {}
        self.statistics['Main']['Overall'] = TumorStatistics()
        if self.tumor_multifocal:
            for p in range(tumor_elements):
                self.statistics[str(p+1)] = {}
                self.statistics[str(p+1)]['Overall'] = TumorStatistics()

    def to_txt(self, filename):
        pfile = open(filename, 'a')
        pfile.write('######### Glioma RADS report #########\n')
        pfile.write('Tumor found: {}\n'.format(self.tumor_presence_state))
        if not self.tumor_presence_state:
            pfile.close()
            return
        pfile.write('Tumor multifocality: {}\n'.format(self.tumor_multifocal))

        pfile.close()
        return

    def to_csv(self, filename):
        values = [self.tumor_multifocal, self.tumor_parts, np.round(self.tumor_multifocal_distance, 2)]
        column_names = ['Multifocality', 'Tumor parts nb', 'Multifocal distance (mm)']

        values.extend([self.statistics['Main']['Overall'].mni_space_tumor_volume, -1.])
        column_names.extend(['Volume original (ml)', 'Volume in MNI (ml)'])

        values.extend([np.round(self.statistics['Main']['Overall'].left_laterality_percentage*100., 2),
                       np.round(self.statistics['Main']['Overall'].right_laterality_percentage*100., 2),
                       self.statistics['Main']['Overall'].laterality_midline_crossing])
        column_names.extend(['Left laterality (%)', 'Right laterality (%)', 'Midline crossing'])

        values.extend([np.round(self.statistics['Main']['Overall'].mni_space_expected_resectable_tumor_volume, 2),
                       np.round(self.statistics['Main']['Overall'].mni_space_expected_residual_tumor_volume, 2),
                       np.round(self.statistics['Main']['Overall'].mni_space_resectability_index, 3),
                       np.round(self.statistics['Main']['Overall'].mni_space_complexity_index, 3)])
        column_names.extend(['ExpectedResectableVolume (ml)', 'ExpectedResidualVolume (ml)', 'ResectionIndex', 'ComplexityIndex'])

        for l in self.statistics['Main']['Overall'].mni_space_lobes_overlap.keys():
            values.extend([self.statistics['Main']['Overall'].mni_space_lobes_overlap[l]])
            column_names.extend([l + '_overlap'])

        for t in self.statistics['Main']['Overall'].mni_space_tracts_overlap.keys():
            values.extend([self.statistics['Main']['Overall'].mni_space_tracts_overlap[t]])
            column_names.extend([t.split('.')[0][:-4] + '_overlap'])

        for t in self.statistics['Main']['Overall'].mni_space_tracts_distance.keys():
            values.extend([self.statistics['Main']['Overall'].mni_space_tracts_distance[t]])
            column_names.extend([t.split('.')[0][:-4] + '_distance'])

        for t in self.statistics['Main']['Overall'].mni_space_tracts_disconnection_max.keys():
            values.extend([self.statistics['Main']['Overall'].mni_space_tracts_disconnection_max[t]])
            column_names.extend([t.split('.')[0][:-4] + '_disconnection'])

        # for t in self.statistics['Main']['Overall'].mni_space_tracts_disconnection_prob.keys():
        #     values.extend([self.statistics['Main']['Overall'].mni_space_tracts_disconnection_prob[t]])
        #     column_names.extend([t.split('.')[0][:-4] + '_disconnection'])

        values_df = pd.DataFrame(np.asarray(values).reshape((1, len(values))), columns=column_names)
        values_df.to_csv(filename)


class TumorStatistics():
    def __init__(self):
        self.left_laterality_percentage = None
        self.right_laterality_percentage = None
        self.laterality_midline_crossing = None
        self.mni_space_tumor_volume = None
        self.mni_space_expected_resectable_tumor_volume = None
        self.mni_space_expected_residual_tumor_volume = None
        self.mni_space_resectability_index = None
        self.mni_space_complexity_index = None
        self.mni_space_lobes_overlap = {}
        self.mni_space_tracts_overlap = {}
        self.mni_space_tracts_distance = {}
        self.mni_space_tracts_disconnection_max = {}
        self.mni_space_tracts_disconnection_prob = {}
