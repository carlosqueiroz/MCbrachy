import os
from typing import Tuple, List, Dict

import numpy as np
import pydicom
from pydicom.uid import UID
from extraction_pipeline_components.search_instance_and_convert_coord_in_pixel import find_instance_in_folder, \
    generate_3d_image_from_series


class Structures:
    def __init__(self, image_shape: Tuple[int, int, int],
                 x_y_z_spacing: Tuple[float, float, float], x_y_z_origin: List[float],
                 x_y_z_rotation_vectors: List[float], list_of_masks, study_folder:str):
        """
        This object represents all the contours associated to a 3d image.

        :param image_shape: shape of the 3d image
        :param x_y_z_spacing: spacial dimension of a voxel
        :param x_y_z_origin: origin of the image in patient coordinates
        :param x_y_z_rotation_vectors: image axes in the patient coordinates
        :param list_of_masks: list of Mask object associated to each contour
        :param study_folder: the path to the folder containing the study
        """
        self.image_shape = image_shape
        self.x_y_z_spacing = x_y_z_spacing
        self.x_y_z_origin = x_y_z_origin
        self.x_y_z_rotation_vectors = x_y_z_rotation_vectors
        self.list_of_masks = list_of_masks
        self.study_folder = study_folder

    def add_masks(self, mask) -> None:
        """
        This method adds one or many Masks to the
        mask list_of_masks.

        :param mask: Mask object or list of Mask objects
        :return: None
        """
        if type(mask) is list:
            self.list_of_masks.extend(mask)

        else:
            self.list_of_masks.append(mask)

    def get_specific_mask(self, roi_name: str, observation_label: str):
        """
        This method will simply return the corresponding Mask
        for the given roi_name or observation_label. In order to return a mask,
        at least one mask should have a matching roi_name or observation_label.
        This method returns None when not found
        :param roi_name: roi name corresponding to the contour
        :param observation_label: observation label given to the conto
        :return: Mask
        """
        for mask in self.list_of_masks:
            if roi_name == mask.roi_name or observation_label == mask.observation_label:
                return mask

    def list_roi_names(self) -> List[str]:
        """
        This method simply return all the possible values of
        roi names contained in all the masks

        :return: list of all the roi names of each mask
        """
        list_of_roi_names = []
        for mask in self.list_of_masks:
            list_of_roi_names.append(mask.roi_name)

        return list_of_roi_names

    def list_roi_observation_labels(self) -> List[str]:
        """
        This method simply return all the possible values of
        observation labels contained in all the masks

        :return: list of all the observation labels of each mask
        """
        list_roi_observation_labels = []
        for mask in self.list_of_masks:
            list_roi_observation_labels.append(mask.observation_label)

        return list_roi_observation_labels

    def get_3d_image_with_all_masks(self) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """
        This method will build the 3d mask arrays of every mask
        and produce the associated 3d image.

        :return: the image and the dict containing all the masks
        """
        last_image_uid = 0
        mask_dict = {}
        for mask in self.list_of_masks:
            initial_mask = np.zeros(self.image_shape)

            for slices in mask.list_mask_slices:
                initial_mask[slices.slice_number, :, :] = slices.mask_array
                last_image_uid = slices.image_uid

            mask_dict[mask.roi_name] = initial_mask

        path_to_image = find_instance_in_folder(last_image_uid, self.study_folder)
        series_folder = os.path.dirname(path_to_image)
        image = generate_3d_image_from_series(self.image_shape, series_folder,
                                              self.x_y_z_spacing, self.x_y_z_origin,
                                              self.x_y_z_rotation_vectors)

        return image, mask_dict


class Mask:
    def __init__(self, roi_name: str, observation_label: str, parent_structures: Structures, list_mask_slices):
        """
        This class represents a full contour made of multiple slices.

        :param roi_name: roi name corresponding to the contour
        :param observation_label: observation label given to the contour
        :param parent_structures: the parent structure object containing the frame of reference info.
        :param list_mask_slices: list of the SliceMask objects
        """
        self.roi_name = roi_name
        self.observation_label = observation_label
        self.parent_structures = parent_structures
        self.list_mask_slices = list_mask_slices

    def add_slices(self, slices) -> None:
        """
        This method adds one or many SliceMasks to the
        mask list_mask_slices.

        :param slices: SliceMask object or list of SliceMask objects
        :return: None
        """
        if type(slices) is list:
            self.list_mask_slices.extend(slices)

        else:
            self.list_mask_slices.append(slices)

    def list_slice_numbers(self) -> List[int]:
        """
        This method simply returns a list of all the
        possible values of slice number
        :return: list of slice numbers contained in the mask
        """
        list_slice_numbers = []
        for mask_slices in self.list_mask_slices:
            list_slice_numbers.append(mask_slices.slice_number)

        return list_slice_numbers

    def get_specific_slice(self, slice_number):
        """
        This method will simply return the corresponding Slice
        for the given slice number. This method returns None when not found

        :param slice_number: the desired slice number
        :return: None or SliceMask
        """
        for slice_mask in self.list_mask_slices:
            if slice_number == slice_mask.slice_number:
                return slice_mask

    def get_3d_mask_with_3d_image(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        This method will fuse all the slices into one 3d mask with one 3d image.


        :return: the 3d image and the 3d mask array
        """
        initial_mask = np.zeros(self.parent_structures.image_shape)
        last_image_uid = 0
        for slices in self.list_mask_slices:
            initial_mask[slices.slice_number, :, :] = slices.mask_array
            last_image_uid = slices.image_uid

        path_to_image = find_instance_in_folder(last_image_uid, self.parent_structures.study_folder)
        series_folder = os.path.dirname(path_to_image)
        image = generate_3d_image_from_series(self.parent_structures.image_shape, series_folder,
                                              self.parent_structures.x_y_z_spacing, self.parent_structures.x_y_z_origin,
                                              self.parent_structures.x_y_z_rotation_vectors)

        return image, initial_mask


class SliceMask:
    def __init__(self, mask_array: np.ndarray, image_uid: UID, slice_number: int, parent_mask: Mask):
        """
        This object represents a single image slice with a single mask array.

        :param mask_array: 2d array
        :param image_uid: uid of the associated image
        :param slice_number: the slice number in the 3d pixel coordinates
        :param parent_mask: mask containing all the slice associated with the same contour
        """
        self.image_uid = image_uid
        self.mask_array = mask_array
        self.slice_number = slice_number
        self.parent_mask = parent_mask

    def get_slice_mask_with_image(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        This method will search for the image associated to the
        mask. This image should be located somewhere in the study_folder
        of the parent structure.

        :return: the 2D image associated with the 2d mask
        """
        image_path = find_instance_in_folder(self.image_uid, self.parent_mask.parent_structures.study_folder)
        image = pydicom.dcmread(image_path).pixel_array

        return image, self.mask_array
