import numpy as np
import operator
import collections
import json
import pandas as pd


class NeuroDiagnosisParameters:
    # """
    # Singleton class to have access from anywhere in the code at the various parameters linked to a neuro diagnosis.
    # """
    # __instance = None
    #
    # @staticmethod
    # def getInstance():
    #     """ Static access method. """
    #     if NeuroDiagnosisParameters.__instance == None:
    #         NeuroDiagnosisParameters()
    #     return NeuroDiagnosisParameters.__instance
    #
    # def __init__(self):
    #     """ Virtually private constructor. """
    #     if NeuroDiagnosisParameters.__instance != None:
    #         raise Exception("This class is a singleton!")
    #     else:
    #         NeuroDiagnosisParameters.__instance = self

    def __init__(self):
        pass

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
        pfile.write('######### GSI-RADS report #########\n')
        pfile.write('Tumor found: {}\n'.format(self.tumor_presence_state))
        if not self.tumor_presence_state:
            pfile.close()
            return
        pfile.write('Tumor multifocality: {}\n'.format(self.statistics['Main']['Overall'].tumor_multifocal))
        pfile.write('\tNumber tumor parts: {}\n'.format(self.statistics['Main']['Overall'].tumor_parts))
        pfile.write('\tLargest distance between components: {} (mm)\n'.format(np.round(self.statistics['Main']['Overall'].tumor_multifocal_distance, 2)))

        pfile.write('Volumes\n')
        pfile.write('\tOriginal space: {} (ml)\n'.format(self.statistics['Main']['Overall'].original_space_tumor_volume))
        pfile.write('\tMNI space: {} (ml)\n'.format(self.statistics['Main']['Overall'].mni_space_tumor_volume))

        pfile.write('Laterality\n')
        pfile.write('\tLeft hemisphere: {}%\n'.format(np.round(self.statistics['Main']['Overall'].left_laterality_percentage * 100., 2)))
        pfile.write('\tRight hemisphere: {}%\n'.format(np.round(self.statistics['Main']['Overall'].right_laterality_percentage * 100., 2)))
        pfile.write('\tMidline crossing: {}\n'.format(self.statistics['Main']['Overall'].laterality_midline_crossing))

        pfile.write('Resectability\n')
        pfile.write('\tExpected resectable volume: {} (ml)\n'.format(np.round(self.statistics['Main']['Overall'].mni_space_expected_resectable_tumor_volume, 2)))
        pfile.write('\tExpected residual volume: {} (ml)\n'.format(np.round(self.statistics['Main']['Overall'].mni_space_expected_residual_tumor_volume, 2)))
        pfile.write('\tResection index: {}\n'.format(np.round(self.statistics['Main']['Overall'].mni_space_resectability_index, 3)))
        pfile.write('\tComplexity index: {}\n'.format(np.round(self.statistics['Main']['Overall'].mni_space_complexity_index, 3)))

        pfile.write('Subcortical structures overlap\n')
        for t in self.statistics['Main']['Overall'].mni_space_lobes_overlap.keys():
            pfile.write('\t{} atlas\n'.format(t))
            lobes_ordered = collections.OrderedDict(sorted(self.statistics['Main']['Overall'].mni_space_lobes_overlap[t].items(), key=operator.itemgetter(1), reverse=True))
            for r in lobes_ordered.keys():
                if lobes_ordered[r] != 0:
                    lobe_name = ' '.join(r.lower().replace('main', '').split('_')[1:])
                    pfile.write('\t\t{}: {}%\n'.format(lobe_name, lobes_ordered[r]))

        pfile.write('White matter tracts overlap or distance\n')
        pfile.write('\tBrainLab atlas\n')
        tracts_ordered = collections.OrderedDict(sorted(self.statistics['Main']['Overall'].mni_space_tracts_overlap.items(), key=operator.itemgetter(1), reverse=True))
        for r in tracts_ordered.keys():
            if tracts_ordered[r] != 0:
                tract_name = ' '.join(r.lower().replace('main', '').replace('mni', '').split('.')[0].split('_'))
                pfile.write('\t\t{}: {}% overlap\n'.format(tract_name, np.round(tracts_ordered[r], 2)))

        pfile.write('\n')
        tracts_ordered = collections.OrderedDict(sorted(self.statistics['Main']['Overall'].mni_space_tracts_distance.items(), key=operator.itemgetter(1), reverse=False))
        for r in tracts_ordered.keys():
            if tracts_ordered[r] != -1.:
                tract_name = ' '.join(r.lower().replace('main', '').replace('mni', '').split('.')[0].split('_'))
                pfile.write('\t\t{}: {}mm away\n'.format(tract_name, np.round(tracts_ordered[r], 2)))
        pfile.close()
        return

    def to_csv(self, filename):
        values = [self.statistics['Main']['Overall'].tumor_multifocal, self.statistics['Main']['Overall'].tumor_parts,
                  np.round(self.statistics['Main']['Overall'].tumor_multifocal_distance, 2)]
        column_names = ['Multifocality', 'Tumor parts nb', 'Multifocal distance (mm)']

        values.extend([self.statistics['Main']['Overall'].original_space_tumor_volume, self.statistics['Main']['Overall'].mni_space_tumor_volume])
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

        for t in self.statistics['Main']['Overall'].mni_space_lobes_overlap.keys():
            for r in self.statistics['Main']['Overall'].mni_space_lobes_overlap[t].keys():
                values.extend([self.statistics['Main']['Overall'].mni_space_lobes_overlap[t][r]])
                column_names.extend([t + '_' + r.split('.')[0].lower().strip().replace('mni', '') + '_overlap'])

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
        self.original_space_tumor_volume = None
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
