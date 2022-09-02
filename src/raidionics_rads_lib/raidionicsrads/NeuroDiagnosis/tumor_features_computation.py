import logging
import traceback
import numpy as np
from typing import Tuple
from scipy.ndimage.measurements import center_of_mass
from scipy.ndimage import measurements
from skimage.measure import regionprops
from medpy.metric.binary import hd95


def compute_volume(volume: np.ndarray, spacing: tuple) -> float:
    """

    Parameters
    ----------
    volume : np.ndarray
        Tumor annotation mask.
    spacing : tuple
        Spacing values for the provided volume array in order to relate pixels to the metric space.
    Returns
    -------
    float
        Object volume in milliliters, rounded at two decimals.
    """
    result = 0.
    try:
        logging.debug("Computing tumor volume.")
        voxel_size = np.prod(spacing[0:3])
        volume_pixels = np.count_nonzero(volume)
        volume_mmcube = voxel_size * volume_pixels
        volume_ml = volume_mmcube * 1e-3
        result = np.round(volume_ml, 2)
    except Exception as e:
        logging.error('Volume computation failed.\n{}'.format(traceback.format_exc()))

    return result


def compute_multifocality(volume: np.ndarray, spacing: tuple,
                          volume_threshold: float = 0.,
                          distance_threshold: float = 0.) -> Tuple[bool, int, float]:
    """

    Parameters
    ----------
    volume : np.ndarray
        Tumor annotation mask.
    spacing : tuple
        Spacing values for the provided volume array in order to relate pixels to the metric space.
    volume_threshold: float
        Minimum volume, in milliliters, for a segmented object to be considered as a focus.
    distance_threshold: float
        Minimum distance, in millimeters, between two foci to consider actual multifocality.
    Returns
    -------
    bool
        Multifocality state, True if multiple focus and False otherwise.
    int
        Number of focus(i).
    float
        Maximum minimum distance between two foci.
    """
    multifocal_status = False
    multifocal_elements = 1
    multifocal_largest_minimum_distance = -1.

    try:
        logging.debug("Computing tumor multifocality.")
        tumor_clusters = measurements.label(volume)[0]
        tumor_clusters_labels = regionprops(tumor_clusters)

        if len(tumor_clusters_labels) > 1:
            multifocal_elements = 0

            # Computing the radius of the largest component.
            radiuses = []
            parts_labels = []
            for l in range(len(tumor_clusters_labels)):
                volume_ml = np.count_nonzero(tumor_clusters == (l + 1)) * np.prod(spacing[0:3]) * 1e-3
                if volume_ml >= volume_threshold:  # Discarding any tumor focus smaller than volume_threshold (in ml)
                    multifocal_elements = multifocal_elements + 1
                    radiuses.append(tumor_clusters_labels[l].equivalent_diameter / 2.)
                    parts_labels.append(l)
            max_radius = np.max(radiuses)
            max_radius_index = parts_labels[radiuses.index(max_radius)]

            # Computing the minimum distances between each focus
            main_tumor_label = np.zeros(volume.shape)
            main_tumor_label[tumor_clusters == (max_radius_index + 1)] = 1
            for l, lab in enumerate(parts_labels):
                if lab != max_radius_index:
                    satellite_label = np.zeros(volume.shape)
                    satellite_label[tumor_clusters == (lab + 1)] = 1
                    dist = hd95(satellite_label, main_tumor_label, voxelspacing=spacing, connectivity=1)
                    if multifocal_largest_minimum_distance is None:
                        multifocal_largest_minimum_distance = dist
                    elif dist > multifocal_largest_minimum_distance:
                        multifocal_largest_minimum_distance = dist

            if multifocal_largest_minimum_distance >= distance_threshold:
                multifocal_status = True
    except Exception as e:
        logging.error('Multifocality computation failed.\n{}'.format(traceback.format_exc()))

    return multifocal_status, multifocal_elements, multifocal_largest_minimum_distance


def compute_lateralisation(volume: np.ndarray, brain_mask: np.ndarray,
                           target: str = 'full') -> Tuple[float, float, bool]:
    """

    Parameters
    ----------
    volume : np.ndarray
        Tumor annotation mask.
    brain_mask: np.ndarray
        Brain mask with lateralization information, the right hemisphere has label 1 and the left has label 2.
    target: str
        ['com', 'full'] In 'com', the lateralisation is computed over the tumor center of mass. In 'full', the whole
        tumor extent is used to compute the lateralisation.
    Returns
    -------
    float
        Percentage of tumor overlap with the brain right hemisphere
    float
        Percentage of tumor overlap with the brain left hemisphere
    bool
        True if the tumor overlaps with both hemispheres, and False otherwise.
    """
    left_hemisphere_percentage = 0.
    right_hemisphere_percentage = 0.
    midline_crossing = False

    try:
        logging.debug("Computing tumor lateralization.")
        # Computing the lateralisation for the center of mass
        if target == 'com':
            com_lateralisation = None
            com = center_of_mass(volume == 1)
            com_lateralization = brain_mask[int(np.round(com[0])) - 3:int(np.round(com[0])) + 3,
                                 int(np.round(com[1]))-3:int(np.round(com[1]))+3,
                                 int(np.round(com[2]))-3:int(np.round(com[2]))+3]
            com_sides_touched = list(np.unique(com_lateralization))
            if 0 in com_sides_touched:
                com_sides_touched.remove(0)
            percentage_each_com_side = [np.count_nonzero(com_lateralization == x) / np.count_nonzero(com_lateralization) for x in com_sides_touched]
            max_per = np.max(percentage_each_com_side)
            if com_sides_touched[percentage_each_com_side.index(max_per)] == 1:
                com_lateralisation = 'Right'
            else:
                com_lateralisation = 'Left'

            left_hemisphere_percentage = 100. if com_lateralisation == 'Right' else 0.
            right_hemisphere_percentage = 100. if com_lateralisation == 'Left' else 0.
            midline_crossing = True if len(com_sides_touched) == 2 else False
        elif target == 'full':
            # Computing the lateralisation for the overall tumor extent
            right_side_percentage = np.count_nonzero((brain_mask == 1) & (volume != 0)) / np.count_nonzero((volume != 0))
            left_side_percentage = np.count_nonzero((brain_mask == 2) & (volume != 0)) / np.count_nonzero((volume != 0))

            left_hemisphere_percentage = np.round(left_side_percentage * 100., 2)
            right_hemisphere_percentage = np.round(right_side_percentage * 100., 2)
            midline_crossing = True if max(left_hemisphere_percentage, right_hemisphere_percentage) < 100. else False
        else:
            pass
    except Exception as e:
        logging.error('Lateralisation computation failed.\n{}'.format(traceback.format_exc()))

    return left_hemisphere_percentage, right_hemisphere_percentage, midline_crossing


def compute_resectability_index(volume: np.ndarray, resectability_map: np.ndarray) -> Tuple[float, float, float]:
    """

    Parameters
    ----------
    volume : np.ndarray
        Tumor annotation mask.
    resectability_map: np.ndarray
        Probability map with computed resectability for each voxel, as introduced in Amsterdam's article.
        Should add the article DOI here.
    Returns
    -------
    float
        Residual tumor volume in milliliters.
    float
        Resectable volume in milliliters.
    float
        Average resectability.
    """

    residual_tumor_volume = 0.
    resectable_volume = 0.
    avg_resectability = 0.

    try:
        logging.debug("Computing tumor resectability index.")
        resectability_map = np.nan_to_num(resectability_map)
        tumor_voxels_count = np.count_nonzero(volume)
        total_resectability = np.sum(resectability_map[volume != 0])
        resectable_volume = total_resectability * 1e-3
        residual_tumor_volume = (tumor_voxels_count * 1e-3) - resectable_volume
        avg_resectability = total_resectability / tumor_voxels_count
    except Exception as e:
        logging.error('Resectability index computation failed.\n{}'.format(traceback.format_exc()))
    return residual_tumor_volume, resectable_volume, avg_resectability
