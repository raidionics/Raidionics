import numpy as np
import scipy.ndimage.measurements as smeas
import scipy.ndimage.morphology as smo
from copy import deepcopy


def mediastinum_clipping(volume, parameters):
    intensity_threshold = -250
    airmetal_mask = deepcopy(volume)
    airmetal_mask[airmetal_mask > intensity_threshold] = 0
    airmetal_mask[airmetal_mask <= intensity_threshold] = 1

    airmetal_mask = smo.binary_closing(airmetal_mask, iterations=5)

    labels, nb_components = smeas.label(airmetal_mask)
    airmetal_pieces = smeas.find_objects(labels, min(nb_components, 1000))

    nums = []
    for p in enumerate(airmetal_pieces):
        bb = p[1]
        z = (bb[2].stop - bb[2].start)
        y = (bb[1].stop - bb[1].start)
        x = (bb[0].stop - bb[0].start)
        nums.append(x * y * z)

    # Should check if the first two or three elements are "as big". If two the following code is correct, if three
    # something should be changed so that the lungs is the third (normally?) and background the first two.
    ind_bg = nums.index(np.max(nums)) + 1
    nums.remove(np.max(nums))
    ind_lungs = nums.index(
        np.max(nums)) + 1 + 1  # +1 because find_objects labels start at 1, and +1 because we remove one value above
    # ind_lungs = nums.index(sorted(nums, reverse=True)[0])+1
    # for l in range(nb_components):
    #   nums.append(np.count_nonzero(np.where(labels == l)))

    background_mask = np.copy(labels)
    background_mask[background_mask != ind_bg] = 0

    lungstrachea_mask = np.copy(labels)
    lungstrachea_mask[lungstrachea_mask != ind_lungs] = 0
    lungstrachea_mask[lungstrachea_mask == ind_lungs] = 1

    lungs_boundingbox = airmetal_pieces[ind_lungs - 1]  # Because indexing starts at 0, so have to decrease by one
    crop_bbox = [lungs_boundingbox[0].start, lungs_boundingbox[1].start, lungs_boundingbox[2].start,
            lungs_boundingbox[0].stop, lungs_boundingbox[1].stop, lungs_boundingbox[2].stop]

    cropped_volume = volume[crop_bbox[0]:crop_bbox[3], crop_bbox[1]:crop_bbox[4], crop_bbox[2]:crop_bbox[5]]

    print('Cropped mediastinum values: {}'.format(lungs_boundingbox))
    return cropped_volume, crop_bbox