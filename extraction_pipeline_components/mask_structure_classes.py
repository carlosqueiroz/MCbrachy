import os
import numpy as np
import pydicom
from extraction_pipeline_components.search_instance_and_convert_coord_in_pixel import find_instance_in_folder, \
    generate_3d_image_from_series


class Structures:
    def __init__(self, image_shape, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors, list_of_masks, study_folder):
        self.image_shape = image_shape
        self.x_y_z_spacing = x_y_z_spacing
        self.x_y_z_origin = x_y_z_origin
        self.x_y_z_rotation_vectors = x_y_z_rotation_vectors
        self.list_of_masks = list_of_masks
        self.study_folder = study_folder

    def add_masks(self, mask):
        if type(mask) is list:
            self.list_of_masks.extend(mask)

        else:
            self.list_of_masks.append(mask)

    def get_specific_mask(self, roi_name, observation_label):
        for mask in self.list_of_masks:
            if roi_name == mask.roi_name or observation_label == mask.observaton_label:
                return mask

    def list_roi_names(self):
        list_of_roi_names = []
        for mask in self.list_of_masks:
            list_of_roi_names.append(mask.roi_name)

        return list_of_roi_names

    def list_roi_observation_labels(self):
        list_roi_observation_labels = []
        for mask in self.list_of_masks:
            list_roi_observation_labels.append(mask.observaton_label)

        return list_roi_observation_labels


class Mask:
    def __init__(self, roi_name: str, observation_label: str, parent_structures: Structures, list_mask_slices):
        self.roi_name = roi_name
        self.observaton_label = observation_label
        self.parent_structures = parent_structures
        self.list_mask_slices = list_mask_slices

    def add_slices(self, slices):
        if type(slices) is list:
            self.list_mask_slices.extend(slices)

        else:
            self.list_mask_slices.append(slices)

    def list_slice_numbers(self):
        list_slice_numbers = []
        for mask_slices in self.list_mask_slices:
            list_slice_numbers.append(mask_slices.slice_number)

        return list_slice_numbers

    def get_specific_slice(self, slice_number):
        for slice_mask in self.list_mask_slices:
            if slice_number == slice_mask.slice_number:
                return slice_mask

    def get_3d_mask_with_3d_image(self):
        initial_mask = np.zeros(self.parent_structures.image_shape)
        last_image_uid = 0
        for slices in self.list_mask_slices:
            initial_mask[slices.slice_number, :, :] = slices.mask_array
            last_image_uid = slices.image_uid

        path_to_image = find_instance_in_folder(last_image_uid, self.parent_structures.study_folder)
        series_folder = os.path.dirname(path_to_image)
        image = generate_3d_image_from_series(self.parent_structures.image_shape, series_folder)

        return image, initial_mask


class SliceMask:
    def __init__(self, mask_array: np.ndarray, image_uid: str, slice_number: int, parent_mask: Mask):
        self.image_uid = image_uid
        self.mask_array = mask_array
        self.slice_number = slice_number
        self.parent_mask = parent_mask

    def get_slice_mask_with_image(self):
        image_path = find_instance_in_folder(self.image_uid, self.parent_mask.parent_structures.study_folder)
        image = pydicom.dcmread(image_path).pixel_array

        return image, self.mask_array
