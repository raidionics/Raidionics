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
        self.statistics['Main']['CoM'] = TumorStatistics()
        if self.tumor_multifocal:
            for p in range(tumor_elements):
                self.statistics[str(p+1)] = {}
                self.statistics[str(p+1)]['Overall'] = TumorStatistics()
                self.statistics[str(p+1)]['CoM'] = TumorStatistics()

    def to_txt(self, filename):
        pfile = open(filename, 'a')
        pfile.write('######### Clinical report #########\n')
        pfile.write('Tumor type: {}\n'.format(self.tumor_type))
        pfile.write('Tumor found: {}\n'.format(self.tumor_presence_state))
        if not self.tumor_presence_state:
            pfile.close()
            return
        pfile.write('Tumor multifocality: {}\n'.format(self.tumor_multifocal))

        # Overall tumor parameters
        pfile.write('\nOverall tumor\n')
        pfile.write('\tCenter of mass laterality: {} with {}%\n'.format(self.statistics['Main']['CoM'].laterality,
                                                                        self.statistics['Main']['CoM'].laterality_percentage))
        pfile.write('\tCenter of mass lobe(s): ')
        for l in self.statistics['Main']['CoM'].mni_space_lobes_overlap.keys():
            pfile.write('{} ({}%), '.format(l, self.statistics['Main']['CoM'].mni_space_lobes_overlap[l]))
        pfile.write('\n')

        pfile.write('\tOverall volume: {}ml\n'.format(self.statistics['Main']['Overall'].mni_space_tumor_volume))
        pfile.write('\tOverall laterality: {} with {}%\n'.format(self.statistics['Main']['Overall'].laterality,
                                                                 np.round(self.statistics['Main']['Overall'].laterality_percentage*100., 2)))
        pfile.write('\tOverall lobe(s): ')
        for l in self.statistics['Main']['Overall'].mni_space_lobes_overlap.keys():
            pfile.write('{} ({}%), '.format(l, self.statistics['Main']['Overall'].mni_space_lobes_overlap[l]))
        pfile.write('\n')

        pfile.write('\tOverall tracts distances: ')
        for l in self.statistics['Main']['Overall'].mni_space_tracts_distance.keys():
            if self.statistics['Main']['Overall'].mni_space_tracts_distance[l] != -1.:
                pfile.write('{} ({}mm), '.format(l, np.round(self.statistics['Main']['Overall'].mni_space_tracts_distance[l], 2)))
        pfile.write('\n')

        pfile.write('\tOverall tracts overlaps: ')
        for l in self.statistics['Main']['Overall'].mni_space_tracts_overlap.keys():
            if self.statistics['Main']['Overall'].mni_space_tracts_overlap[l] > 0:
                pfile.write('{} ({}%), '.format(l, np.round(self.statistics['Main']['Overall'].mni_space_tracts_overlap[l]*100., 2)))
        pfile.write('\n')

        # Parameters for each tumor element
        if self.tumor_multifocal:
            for p in range(self.tumor_parts):
                tumor_component = str(p+1)
                pfile.write('\nTumor part {}\n'.format(tumor_component))
                pfile.write(
                    '\tCenter of mass laterality: {} with {}%\n'.format(self.statistics[tumor_component]['CoM'].laterality,
                                                                        self.statistics[tumor_component][
                                                                            'CoM'].laterality_percentage))
                pfile.write('\tCenter of mass lobe(s): ')
                for l in self.statistics[tumor_component]['CoM'].mni_space_lobes_overlap.keys():
                    pfile.write('{} ({}%), '.format(l, self.statistics[tumor_component]['CoM'].mni_space_lobes_overlap[l]))
                pfile.write('\n')

                pfile.write(
                    '\tOverall volume: {}ml\n'.format(self.statistics[tumor_component]['Overall'].mni_space_tumor_volume))
                pfile.write('\tOverall laterality: {} with {}%\n'.format(self.statistics[tumor_component]['Overall'].laterality,
                                                                         np.round(self.statistics[tumor_component][
                                                                                      'Overall'].laterality_percentage * 100.,
                                                                                  2)))
                pfile.write('\tOverall lobe(s): ')
                for l in self.statistics[tumor_component]['Overall'].mni_space_lobes_overlap.keys():
                    pfile.write('{} ({}%), '.format(l, self.statistics[tumor_component]['Overall'].mni_space_lobes_overlap[l]))
                pfile.write('\n')

                pfile.write('\tOverall tracts distances: ')
                for l in self.statistics[tumor_component]['Overall'].mni_space_tracts_distance.keys():
                    if self.statistics[tumor_component]['Overall'].mni_space_tracts_distance[l] != -1.:
                        pfile.write('{} ({}mm), '.format(l, np.round(
                            self.statistics[tumor_component]['Overall'].mni_space_tracts_distance[l], 2)))
                pfile.write('\n')

                pfile.write('\tOverall tracts overlaps: ')
                for l in self.statistics[tumor_component]['Overall'].mni_space_tracts_overlap.keys():
                    if self.statistics[tumor_component]['Overall'].mni_space_tracts_overlap[l] > 0:
                        pfile.write('{} ({}%), '.format(l, np.round(
                            self.statistics[tumor_component]['Overall'].mni_space_tracts_overlap[l] * 100., 2)))
                pfile.write('\n')

        pfile.close()
        return

    def to_json(self, filename):
        param_json = {}
        param_json['Overall'] = {}
        param_json['Overall']['Presence'] = self.tumor_presence_state
        if not self.tumor_presence_state:
            with open(filename, 'w') as outfile:
                json.dump(param_json, outfile)
            return

        param_json['Overall']['Type'] = self.tumor_type
        param_json['Overall']['Multifocal'] = self.tumor_multifocal
        param_json['Overall']['Components'] = self.tumor_parts

        param_json['Main'] = {}
        param_json['Main']['CenterOfMass'] = {}
        param_json['Main']['CenterOfMass']['Laterality'] = self.statistics['Main']['CoM'].laterality
        param_json['Main']['CenterOfMass']['Laterality_perc'] = self.statistics['Main']['CoM'].laterality_percentage
        param_json['Main']['CenterOfMass']['Lobe'] = []
        for l in self.statistics['Main']['CoM'].mni_space_lobes_overlap.keys():
            param_json['Main']['CenterOfMass']['Lobe'].append([l, self.statistics['Main']['CoM'].mni_space_lobes_overlap[l]])

        param_json['Main']['Total'] = {}
        param_json['Main']['Total']['Volume'] = self.statistics['Main']['Overall'].mni_space_tumor_volume
        param_json['Main']['Total']['Laterality'] = self.statistics['Main']['Overall'].laterality
        param_json['Main']['Total']['Laterality_perc'] = np.round(self.statistics['Main']['Overall'].laterality_percentage * 100., 2)
        param_json['Main']['Total']['Resectability'] = np.round(self.statistics['Main']['Overall'].mni_space_resectability_score * 100., 2)
        param_json['Main']['Total']['Lobe'] = []

        for l in self.statistics['Main']['Overall'].mni_space_lobes_overlap.keys():
            param_json['Main']['Total']['Lobe'].append([l, self.statistics['Main']['Overall'].mni_space_lobes_overlap[l]])

        param_json['Main']['Total']['Tract'] = {}
        param_json['Main']['Total']['Tract']['Distance'] = []

        for l in self.statistics['Main']['Overall'].mni_space_tracts_distance.keys():
            if self.statistics['Main']['Overall'].mni_space_tracts_distance[l] != -1.:
                param_json['Main']['Total']['Tract']['Distance'].append([l, np.round(self.statistics['Main']['Overall'].mni_space_tracts_distance[l], 2)])

        param_json['Main']['Total']['Tract']['Overlap'] = []
        for l in self.statistics['Main']['Overall'].mni_space_tracts_overlap.keys():
            if self.statistics['Main']['Overall'].mni_space_tracts_overlap[l] > 0:
                param_json['Main']['Total']['Tract']['Overlap'].append([l, np.round(self.statistics['Main']['Overall'].mni_space_tracts_overlap[l]*100., 2)])

        # Parameters for each tumor element
        if self.tumor_multifocal:
            for p in range(self.tumor_parts):
                tumor_component = str(p+1)
                param_json[tumor_component] = {}
                param_json[tumor_component]['CenterOfMass'] = {}
                param_json[tumor_component]['CenterOfMass']['Laterality'] = self.statistics[tumor_component]['CoM'].laterality
                param_json[tumor_component]['CenterOfMass']['Laterality_perc'] = self.statistics[tumor_component]['CoM'].laterality_percentage
                param_json[tumor_component]['CenterOfMass']['Lobe'] = []
                for l in self.statistics[tumor_component]['CoM'].mni_space_lobes_overlap.keys():
                    param_json[tumor_component]['CenterOfMass']['Lobe'].append([l, self.statistics[tumor_component]['CoM'].mni_space_lobes_overlap[l]])

                param_json[tumor_component]['Total'] = {}
                param_json[tumor_component]['Total']['Volume'] = self.statistics[tumor_component]['Overall'].mni_space_tumor_volume
                param_json[tumor_component]['Total']['Laterality'] = self.statistics[tumor_component]['Overall'].laterality
                param_json[tumor_component]['Total']['Laterality_perc'] = np.round(self.statistics[tumor_component]['Overall'].laterality_percentage * 100., 2)
                param_json[tumor_component]['Total']['Resectability'] = np.round(self.statistics[tumor_component]['Overall'].mni_space_resectability_score * 100., 2)

                param_json[tumor_component]['Total']['Lobe'] = []

                for l in self.statistics[tumor_component]['Overall'].mni_space_lobes_overlap.keys():
                    param_json[tumor_component]['Total']['Lobe'].append([l, self.statistics[tumor_component]['Overall'].mni_space_lobes_overlap[l]])

                param_json[tumor_component]['Total']['Tract'] = {}
                param_json[tumor_component]['Total']['Tract']['Distance'] = []

                for l in self.statistics[tumor_component]['Overall'].mni_space_tracts_distance.keys():
                    if self.statistics[tumor_component]['Overall'].mni_space_tracts_distance[l] != -1.:
                        param_json[tumor_component]['Total']['Tract']['Distance'].append([l, np.round(self.statistics[tumor_component]['Overall'].mni_space_tracts_distance[l], 2)])

                param_json[tumor_component]['Total']['Tract']['Overlap'] = []
                for l in self.statistics[tumor_component]['Overall'].mni_space_tracts_overlap.keys():
                    if self.statistics[tumor_component]['Overall'].mni_space_tracts_overlap[l] > 0:
                        param_json[tumor_component]['Total']['Tract']['Overlap'].append([l, np.round(self.statistics[tumor_component]['Overall'].mni_space_tracts_overlap[l] * 100., 2)])

        with open(filename, 'w', newline='\n') as outfile:
            json.dump(param_json, outfile)
        return
        # # Parameters for each tumor element
        # if self.tumor_multifocal:
        #     for p in range(self.tumor_parts):
        #         tumor_component = str(p+1)
        #         pfile.write('\nTumor part {}\n'.format(tumor_component))
        #         pfile.write(
        #             '\tCenter of mass laterality: {} with {}%\n'.format(self.statistics[tumor_component]['CoM'].laterality,
        #                                                                 self.statistics[tumor_component][
        #                                                                     'CoM'].laterality_percentage))
        #         pfile.write('\tCenter of mass lobe(s): ')
        #         for l in self.statistics[tumor_component]['CoM'].mni_space_lobes_overlap.keys():
        #             pfile.write('{} ({}%), '.format(l, self.statistics[tumor_component]['CoM'].mni_space_lobes_overlap[l]))
        #         pfile.write('\n')
        #
        #         pfile.write(
        #             '\tOverall volume: {}ml\n'.format(self.statistics[tumor_component]['Overall'].mni_space_tumor_volume))
        #         pfile.write('\tOverall laterality: {} with {}%\n'.format(self.statistics[tumor_component]['Overall'].laterality,
        #                                                                  np.round(self.statistics[tumor_component][
        #                                                                               'Overall'].laterality_percentage * 100.,
        #                                                                           2)))
        #         pfile.write('\tOverall lobe(s): ')
        #         for l in self.statistics[tumor_component]['Overall'].mni_space_lobes_overlap.keys():
        #             pfile.write('{} ({}%), '.format(l, self.statistics[tumor_component]['Overall'].mni_space_lobes_overlap[l]))
        #         pfile.write('\n')
        #
        #         pfile.write('\tOverall tracts distances: ')
        #         for l in self.statistics[tumor_component]['Overall'].mni_space_tracts_distance.keys():
        #             if self.statistics[tumor_component]['Overall'].mni_space_tracts_distance[l] != -1.:
        #                 pfile.write('{} ({}mm), '.format(l, np.round(
        #                     self.statistics[tumor_component]['Overall'].mni_space_tracts_distance[l], 2)))
        #         pfile.write('\n')
        #
        #         pfile.write('\tOverall tracts overlaps: ')
        #         for l in self.statistics[tumor_component]['Overall'].mni_space_tracts_overlap.keys():
        #             if self.statistics[tumor_component]['Overall'].mni_space_tracts_overlap[l] > 0:
        #                 pfile.write('{} ({}%), '.format(l, np.round(
        #                     self.statistics[tumor_component]['Overall'].mni_space_tracts_overlap[l] * 100., 2)))
        #         pfile.write('\n')

    def to_csv(self, filename):
        column_names = ['Multifocal', '# parts', 'Volume (ml)', 'Left laterality (%)', 'Right laterality (%)',
                        'Resectability score']
        values = [self.tumor_multifocal, self.tumor_parts, self.statistics['Main']['Overall'].mni_space_tumor_volume,
                  np.round(self.statistics['Main']['Overall'].left_laterality_percentage*100., 2),
                  np.round(self.statistics['Main']['Overall'].right_laterality_percentage*100., 2),
                  self.statistics['Main']['Overall'].mni_space_resectability_score]

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

        values_df = pd.DataFrame(np.asarray(values).reshape((1, len(values))), columns=column_names)
        values_df.to_csv(filename)


class TumorStatistics():
    def __init__(self):
        self.laterality = None
        self.laterality_percentage = None
        self.left_laterality_percentage = None
        self.right_laterality_percentage = None
        self.mni_space_tumor_volume = None
        self.mni_space_resectability_score = None
        self.mni_space_lobes_overlap = {}
        self.mni_space_tracts_overlap = {}
        self.mni_space_tracts_distance = {}
        self.mni_space_tracts_disconnection_max = {}
        self.mni_space_tracts_disconnection_mean = {}
