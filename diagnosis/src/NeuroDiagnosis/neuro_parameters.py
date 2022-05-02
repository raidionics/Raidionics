import numpy as np
import operator
import collections
import pandas as pd
import json


class NeuroDiagnosisParameters:
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
        pfile.write('########### NeuroRADS report ###########\n')
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
        pfile.write('  * Left hemisphere: {}%\n'.format(np.round(self.statistics['Main']['Overall'].left_laterality_percentage * 100., 2)))
        pfile.write('  * Right hemisphere: {}%\n'.format(np.round(self.statistics['Main']['Overall'].right_laterality_percentage * 100., 2)))
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
                    lobe_name = ' '.join(r.lower().replace('main', '').split('_')[1:])
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
        pfile.close()
        return

    def to_csv(self, filename):
        if not self.tumor_presence_state:
            return

        values = [self.tumor_multifocal, self.tumor_parts, np.round(self.tumor_multifocal_distance, 2)]
        column_names = ['Multifocality', 'Tumor parts nb', 'Multifocal distance (mm)']

        values.extend([self.statistics['Main']['Overall'].original_space_tumor_volume, self.statistics['Main']['Overall'].mni_space_tumor_volume])
        column_names.extend(['Volume original (ml)', 'Volume in MNI (ml)'])

        values.extend([np.round(self.statistics['Main']['Overall'].left_laterality_percentage*100., 2),
                       np.round(self.statistics['Main']['Overall'].right_laterality_percentage*100., 2),
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
                column_names.extend([t + '_' + r.split('.')[0][:-4] + '_overlap'])

        for t in self.statistics['Main']['Overall'].mni_space_subcortical_structures_distance.keys():
            for r in self.statistics['Main']['Overall'].mni_space_subcortical_structures_distance[t].keys():
                values.extend([self.statistics['Main']['Overall'].mni_space_subcortical_structures_distance[t][r]])
                column_names.extend([t + '_' + r.split('.')[0][:-4] + '_distance'])

        values_df = pd.DataFrame(np.asarray(values).reshape((1, len(values))), columns=column_names)
        values_df.to_csv(filename, index=False)

    def to_json(self, filename):
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

        param_json['Main']['Total'] = {}
        param_json['Main']['Total']['Volume original (ml)'] = self.statistics['Main']['Overall'].original_space_tumor_volume
        param_json['Main']['Total']['Volume in MNI (ml)'] = self.statistics['Main']['Overall'].mni_space_tumor_volume
        param_json['Main']['Total']['Left laterality (%)'] = np.round(self.statistics['Main']['Overall'].left_laterality_percentage*100., 2)
        param_json['Main']['Total']['Right laterality (%)'] = np.round(self.statistics['Main']['Overall'].right_laterality_percentage*100., 2)
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

        with open(filename, 'w', newline='\n') as outfile:
            json.dump(param_json, outfile, indent=4, sort_keys=True)
        return


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
        self.mni_space_cortical_structures_overlap = {}
        self.mni_space_subcortical_structures_overlap = {}
        self.mni_space_subcortical_structures_distance = {}
