import logging
import traceback

import numpy as np
import operator
import json
import pandas as pd
import collections


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

    def to_txt(self, filename: str) -> None:
        """

        Exporting the computed tumor characteristics and standardized report in filename.

        Parameters
        ----------
        filename : str
            Filename which should end in .txt .
        Returns
        -------
        None
        """
        try:
            logging.info("Exporting neuro-parameters to text in {}.".format(filename))
            pfile = open(filename, 'a')
            pfile.write('########### Raidionics clinical report ###########\n')
            pfile.write('Tumor found: {}\n'.format(self.tumor_presence_state))
            if not self.tumor_presence_state:
                pfile.close()
                return
            pfile.write('Tumor multifocality: {}\n'.format(self.tumor_multifocal))
            pfile.write('  * Number tumor parts: {}\n'.format(self.tumor_parts))
            pfile.write('  * Largest distance between components: {} (mm)\n'.format(np.round(self.tumor_multifocal_distance, 2)))

            pfile.write('\nVolumes\n')
            pfile.write('  * Original space: {} (ml)\n'.format(np.round(self.statistics['Main']['Overall'].original_space_tumor_volume, 2)))
            pfile.write('  * MNI space: {} (ml)\n'.format(self.statistics['Main']['Overall'].mni_space_tumor_volume))

            pfile.write('\nLaterality\n')
            pfile.write('  * Left hemisphere: {}%\n'.format(self.statistics['Main']['Overall'].left_laterality_percentage))
            pfile.write('  * Right hemisphere: {}%\n'.format(self.statistics['Main']['Overall'].right_laterality_percentage))
            pfile.write('  * Midline crossing: {}\n'.format(self.statistics['Main']['Overall'].laterality_midline_crossing))

            if self.tumor_type == 'High-Grade Glioma':
                pfile.write('\nResectability\n')
                pfile.write('  * Expected residual volume: {} (ml)\n'.format(np.round(self.statistics['Main']['Overall'].mni_space_expected_residual_tumor_volume, 2)))
                pfile.write('  * Resection index: {}\n'.format(np.round(self.statistics['Main']['Overall'].mni_space_resectability_index, 3)))

            pfile.write('\nCortical structures overlap\n')
            for t in self.statistics['Main']['Overall'].mni_space_cortical_structures_overlap.keys():
                pfile.write('  * {} atlas\n'.format(t))
                lobes_ordered = collections.OrderedDict(sorted(self.statistics['Main']['Overall'].mni_space_cortical_structures_overlap[t].items(), key=operator.itemgetter(1), reverse=True))
                for r in lobes_ordered.keys():
                    if lobes_ordered[r] != 0:
                        lobe_name = ' '.join(r.lower().replace('main', '').split('_')[:])
                        pfile.write('    - {}: {}%\n'.format(lobe_name, lobes_ordered[r]))

            pfile.write('\nSubcortical structures overlap or distance\n')
            for t in self.statistics['Main']['Overall'].mni_space_subcortical_structures_overlap.keys():
                pfile.write('  * {} atlas\n'.format(t))
                tracts_ordered = collections.OrderedDict(sorted(self.statistics['Main']['Overall'].mni_space_subcortical_structures_overlap[t].items(), key=operator.itemgetter(1), reverse=True))
                for r in tracts_ordered.keys():
                    if tracts_ordered[r] != 0:
                        tract_name = ' '.join(r.lower().replace('main', '').replace('mni', '').split('.')[0].split('_'))
                        pfile.write('    - {}: {}% overlap\n'.format(tract_name, np.round(tracts_ordered[r], 2)))

                pfile.write('\n')
                tracts_ordered = collections.OrderedDict(sorted(self.statistics['Main']['Overall'].mni_space_subcortical_structures_distance[t].items(), key=operator.itemgetter(1), reverse=False))
                for r in tracts_ordered.keys():
                    if tracts_ordered[r] != -1.:
                        tract_name = ' '.join(r.lower().replace('main', '').replace('mni', '').split('.')[0].split('_'))
                        pfile.write('    - {}: {}mm away\n'.format(tract_name, np.round(tracts_ordered[r], 2)))

            # Parameters for each tumor element
            # if self.tumor_multifocal:
            #     for p in range(self.tumor_parts):
            #         tumor_component = str(p+1)
            #         pfile.write('\nTumor part {}\n'.format(tumor_component))

            pfile.close()
        except Exception as e:
            logging.error("Neuro-parameters export to text failed with {}.\n".format(traceback.format_exc()))
        return

    def to_json(self, filename: str) -> None:
        # @TODO. to modify
        try:
            logging.info("Exporting neuro-parameters to json in {}.".format(filename))
            param_json = {}
            param_json['Overall'] = {}
            param_json['Overall']['Presence'] = self.tumor_presence_state
            if not self.tumor_presence_state:
                with open(filename, 'w') as outfile:
                    json.dump(param_json, outfile)
                return

            param_json['Overall']['Type'] = self.tumor_type
            param_json['Overall']['Multifocality'] = self.tumor_multifocal
            param_json['Overall']['Tumor parts nb'] = self.tumor_parts
            param_json['Overall']['Multifocal distance (mm)'] = np.round(self.tumor_multifocal_distance, 2)

            param_json['Main'] = {}
            # param_json['Main']['CenterOfMass'] = {}
            # param_json['Main']['CenterOfMass']['Laterality'] = self.statistics['Main']['CoM'].laterality
            # param_json['Main']['CenterOfMass']['Laterality_perc'] = self.statistics['Main']['CoM'].laterality_percentage
            # param_json['Main']['CenterOfMass']['Lobe'] = []
            # for l in self.statistics['Main']['CoM'].mni_space_cortical_structures_overlap.keys():
            #     param_json['Main']['CenterOfMass']['Lobe'].append([l, self.statistics['Main']['CoM'].mni_space_cortical_structures_overlap[l]])

            param_json['Main']['Total'] = {}
            param_json['Main']['Total']['Volume original (ml)'] = self.statistics['Main']['Overall'].original_space_tumor_volume
            param_json['Main']['Total']['Volume in MNI (ml)'] = self.statistics['Main']['Overall'].mni_space_tumor_volume
            param_json['Main']['Total']['Left laterality (%)'] = self.statistics['Main']['Overall'].left_laterality_percentage
            param_json['Main']['Total']['Right laterality (%)'] = self.statistics['Main']['Overall'].right_laterality_percentage
            param_json['Main']['Total']['Midline crossing'] = self.statistics['Main']['Overall'].laterality_midline_crossing

            if self.tumor_type == 'High-Grade Glioma':
                param_json['Main']['Total']['ExpectedResidualVolume (ml)'] = np.round(self.statistics['Main']['Overall'].mni_space_expected_residual_tumor_volume, 2)
                param_json['Main']['Total']['ResectionIndex'] = np.round(self.statistics['Main']['Overall'].mni_space_resectability_index, 3)

            param_json['Main']['Total']['CorticalStructures'] = {}
            for t in self.statistics['Main']['Overall'].mni_space_cortical_structures_overlap.keys():
                param_json['Main']['Total']['CorticalStructures'][t] = {}
                for r in self.statistics['Main']['Overall'].mni_space_cortical_structures_overlap[t].keys():
                    param_json['Main']['Total']['CorticalStructures'][t][r] = self.statistics['Main']['Overall'].mni_space_cortical_structures_overlap[t][r]

            param_json['Main']['Total']['SubcorticalStructures'] = {}

            for t in self.statistics['Main']['Overall'].mni_space_subcortical_structures_overlap.keys():
                param_json['Main']['Total']['SubcorticalStructures'][t] = {}
                param_json['Main']['Total']['SubcorticalStructures'][t]['Overlap'] = {}
                param_json['Main']['Total']['SubcorticalStructures'][t]['Distance'] = {}
                for ov in self.statistics['Main']['Overall'].mni_space_subcortical_structures_overlap[t].keys():
                    param_json['Main']['Total']['SubcorticalStructures'][t]['Overlap'][ov] = self.statistics['Main']['Overall'].mni_space_subcortical_structures_overlap[t][ov]
                for di in self.statistics['Main']['Overall'].mni_space_subcortical_structures_distance[t].keys():
                    param_json['Main']['Total']['SubcorticalStructures'][t]['Distance'][di] = self.statistics['Main']['Overall'].mni_space_subcortical_structures_distance[t][di]

            # Parameters for each tumor element
            # if self.tumor_multifocal:
            #     for p in range(self.tumor_parts):
            #         tumor_component = str(p+1)
            #         param_json[tumor_component] = {}
            #         param_json[tumor_component]['CenterOfMass'] = {}
            #         param_json[tumor_component]['CenterOfMass']['Laterality'] = self.statistics[tumor_component]['CoM'].laterality
            #         param_json[tumor_component]['CenterOfMass']['Laterality_perc'] = self.statistics[tumor_component]['CoM'].laterality_percentage
            #         param_json[tumor_component]['CenterOfMass']['Lobe'] = []
            #         for l in self.statistics[tumor_component]['CoM'].mni_space_cortical_structures_overlap.keys():
            #             param_json[tumor_component]['CenterOfMass']['Lobe'].append([l, self.statistics[tumor_component]['CoM'].mni_space_cortical_structures_overlap[l]])
            #
            #         param_json[tumor_component]['Total'] = {}
            #         param_json[tumor_component]['Total']['Volume'] = self.statistics[tumor_component]['Overall'].mni_space_tumor_volume
            #         param_json[tumor_component]['Total']['Laterality'] = self.statistics[tumor_component]['Overall'].laterality
            #         param_json[tumor_component]['Total']['Laterality_perc'] = np.round(self.statistics[tumor_component]['Overall'].laterality_percentage * 100., 2)
            #         param_json[tumor_component]['Total']['Resectability'] = np.round(self.statistics[tumor_component]['Overall'].mni_space_resectability_score * 100., 2)
            #
            #         param_json[tumor_component]['Total']['Lobe'] = []
            #
            #         for l in self.statistics[tumor_component]['Overall'].mni_space_cortical_structures_overlap.keys():
            #             param_json[tumor_component]['Total']['Lobe'].append([l, self.statistics[tumor_component]['Overall'].mni_space_cortical_structures_overlap[l]])
            #
            #         param_json[tumor_component]['Total']['Tract'] = {}
            #         param_json[tumor_component]['Total']['Tract']['Distance'] = []
            #
            #         for l in self.statistics[tumor_component]['Overall'].mni_space_tracts_distance.keys():
            #             if self.statistics[tumor_component]['Overall'].mni_space_tracts_distance[l] != -1.:
            #                 param_json[tumor_component]['Total']['Tract']['Distance'].append([l, np.round(self.statistics[tumor_component]['Overall'].mni_space_tracts_distance[l], 2)])
            #
            #         param_json[tumor_component]['Total']['Tract']['Overlap'] = []
            #         for l in self.statistics[tumor_component]['Overall'].mni_space_tracts_overlap.keys():
            #             if self.statistics[tumor_component]['Overall'].mni_space_tracts_overlap[l] > 0:
            #                 param_json[tumor_component]['Total']['Tract']['Overlap'].append([l, np.round(self.statistics[tumor_component]['Overall'].mni_space_tracts_overlap[l] * 100., 2)])

            with open(filename, 'w', newline='\n') as outfile:
                json.dump(param_json, outfile, indent=4, sort_keys=True)
        except Exception as e:
            logging.error("Neuro-parameters export to json failed with {}.\n".format(traceback.format_exc()))

        return

    def to_csv(self, filename: str) -> None:
        try:
            logging.info("Exporting neuro-parameters to csv in {}.".format(filename))

            if not self.tumor_presence_state:
                return
            values = [self.tumor_multifocal, self.tumor_parts, np.round(self.tumor_multifocal_distance, 2)]
            column_names = ['Multifocality', 'Tumor parts nb', 'Multifocal distance (mm)']

            values.extend([self.statistics['Main']['Overall'].original_space_tumor_volume, self.statistics['Main']['Overall'].mni_space_tumor_volume])
            column_names.extend(['Volume original (ml)', 'Volume in MNI (ml)'])

            values.extend([self.statistics['Main']['Overall'].left_laterality_percentage,
                           self.statistics['Main']['Overall'].right_laterality_percentage,
                           self.statistics['Main']['Overall'].laterality_midline_crossing])
            column_names.extend(['Left laterality (%)', 'Right laterality (%)', 'Midline crossing'])

            if self.tumor_type == 'High-Grade Glioma':
                values.extend([np.round(self.statistics['Main']['Overall'].mni_space_expected_residual_tumor_volume, 2),
                               np.round(self.statistics['Main']['Overall'].mni_space_resectability_index, 3)])
                column_names.extend(['ExpectedResidualVolume (ml)', 'ResectionIndex'])

            for t in self.statistics['Main']['Overall'].mni_space_cortical_structures_overlap.keys():
                for r in self.statistics['Main']['Overall'].mni_space_cortical_structures_overlap[t].keys():
                    values.extend([self.statistics['Main']['Overall'].mni_space_cortical_structures_overlap[t][r]])
                    column_names.extend([r.split('.')[0].lower().strip() + '_overlap'])

            for t in self.statistics['Main']['Overall'].mni_space_subcortical_structures_overlap.keys():
                for r in self.statistics['Main']['Overall'].mni_space_subcortical_structures_overlap[t].keys():
                    values.extend([self.statistics['Main']['Overall'].mni_space_subcortical_structures_overlap[t][r]])
                    column_names.extend([t + r.split('.')[0][:-4] + '_overlap'])

            for t in self.statistics['Main']['Overall'].mni_space_subcortical_structures_distance.keys():
                for r in self.statistics['Main']['Overall'].mni_space_subcortical_structures_overlap[t].keys():
                    values.extend([self.statistics['Main']['Overall'].mni_space_subcortical_structures_distance[t][r]])
                    column_names.extend([t + r.split('.')[0][:-4] + '_distance'])

            values_df = pd.DataFrame(np.asarray(values).reshape((1, len(values))), columns=column_names)
            values_df.to_csv(filename, index=False)
        except Exception as e:
            logging.error("Neuro-parameters export to csv failed with {}.\n".format(traceback.format_exc()))


# @TODO. Might need another class for holding all patient information (i.e. multiple sequences and multiple timestamps)
class TumorStatistics():
    """
    Specific class for holding the computed tumor characteristics/features.
    """
    def __init__(self):
        self.left_laterality_percentage = None
        self.right_laterality_percentage = None
        self.laterality_midline_crossing = None
        self.original_space_tumor_volume = None
        self.mni_space_tumor_volume = None
        self.mni_space_expected_resectable_tumor_volume = None
        self.mni_space_expected_residual_tumor_volume = None
        self.mni_space_resectability_index = None
        self.mni_space_cortical_structures_overlap = {}
        self.mni_space_subcortical_structures_overlap = {}
        self.mni_space_subcortical_structures_distance = {}
