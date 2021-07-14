from typing import Tuple, List

import numpy as np
import pydicom
import os
import logging


def extract_positionning_informations(path_to_the_frame_reference: str) -> Tuple[Tuple[int, int],
                                                                                 Tuple[float, float, float],
                                                                                 List[float], List[float]]:
    """
    This method allows the extraction of all information relative to the location of the image in
    patient's coordinate. This will be usefull to convert mask patient points into a mask array
    corresponding to each pixel.


    :param path_to_the_frame_reference: Path to the image containing the reference frame's information:
    :return: This method returns the image shape, the xyz spacing, the image origin in patient coordinates
             and the orientation of x and y image axis in patient coordinates
    """
    try:
        dicom = pydicom.dcmread(path_to_the_frame_reference)
        img_shape_2d = dicom.Rows, dicom.Columns
        x_y_z_spacing = float(dicom.PixelSpacing[0]), float(dicom.PixelSpacing[1]), float(dicom.SliceThickness)
        x_y_z_origin = dicom.ImagePositionPatient
        x_y_z_rotation_vectors = dicom.ImageOrientationPatient

    except (AttributeError, TypeError):
        logging.warning(f"The file at {path_to_the_frame_reference} is not an image or has some "
                        f"missing information on the frame of reference")
        img_shape_2d = 0., 0.
        x_y_z_spacing = 0., 0., 0.
        x_y_z_origin = [0., 0., 0.]
        x_y_z_rotation_vectors = [0., 0., 0., 0., 0., 0.]

    return img_shape_2d, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors


def find_instance_in_folder(sop_instance_UID: str, path_to_folder: str) -> str or None:
    """
    This method will look for a specific instance in à specified folder.
    The provided folder can also contain sub-folders that will also
    be explored recursively.

    :param sop_instance_UID: UID of the desired instance
    :param path_to_folder: direct folder of upper lower folder to look into
           in order to find the instance

    :return: the str path of the corresponding instance
    """
    for sub_items in os.listdir(path_to_folder):
        path_to_item = os.path.join(path_to_folder, sub_items)
        if os.path.isdir(path_to_item):
            found_file = find_instance_in_folder(sop_instance_UID, path_to_item)
            if found_file is not None:
                return found_file

        if path_to_item.endswith(".dcm"):
            dicom = pydicom.dcmread(path_to_item)
            if dicom.SOPInstanceUID == sop_instance_UID:
                return path_to_item

    logging.warning(f"Instance {sop_instance_UID} not found in folder {path_to_folder}")
    return None


def convert_real_coord_to_pixel_coord(array_x_y_z_coord: np.ndarray,
                                      x_y_z_spacing: Tuple[float, float, float], x_y_z_origin: List[float],
                                      x_y_rotation_vectors: List[float]) -> np.ndarray:
    """
    This method will convert a 2d array of 3d points from the patient coordinates to the pixel coordinates.

    :param array_x_y_z_coord: the coordinates (a, 3) where a is the number of points
    :param x_y_z_spacing: spacial dimension of a voxel
    :param x_y_z_origin: origin of the image in patient coordinates
    :param x_y_rotation_vectors: image axes in the patient coordinates

    :return: The coordinates in the pixel reference
    """
    try:
        x_spacing, y_spacing, z_spacing = float(x_y_z_spacing[0]), float(x_y_z_spacing[1]), float(x_y_z_spacing[2])
        origin_x, origin_y, origin_z = x_y_z_origin

        z_rot_vector = np.cross(x_y_rotation_vectors[:3], x_y_rotation_vectors[3:6])
        array_x_y_z_coord[:, 0] = np.around((array_x_y_z_coord[:, 0] - origin_x)
                                            * (x_y_rotation_vectors[0] + x_y_rotation_vectors[3] + z_rot_vector[0])
                                            / x_spacing)
        array_x_y_z_coord[:, 1] = np.around((array_x_y_z_coord[:, 1] - origin_y)
                                            * (x_y_rotation_vectors[1] + x_y_rotation_vectors[4] + z_rot_vector[1])
                                            / y_spacing)
        array_x_y_z_coord[:, 2] = - np.around((array_x_y_z_coord[:, 2] - origin_z)
                                              * (x_y_rotation_vectors[2] + x_y_rotation_vectors[5] + z_rot_vector[2])
                                              / z_spacing)
    except (ZeroDivisionError, TypeError):
        logging.error("One of the given information is does not fit template")

    return array_x_y_z_coord.astype(dtype=np.int64)


def convert_pixel_coord_to_real_coord(array_pixel_coord: np.ndarray,
                                      x_y_z_spacing: Tuple[float, float, float], x_y_z_origin: List[float],
                                      x_y_rotation_vectors: List[float]) -> np.ndarray:
    """
    This method will convert a 2d array of 3d points from the patient coordinates to the pixel coordinates.

    :param array_pixel_coord: the coordinates (a, 3) where a is the number of points
    :param x_y_z_spacing: spacial dimension of a voxel
    :param x_y_z_origin: origin of the image in patient coordinates
    :param x_y_rotation_vectors: image axes in the patient coordinates

    :return: The coordinates in the pixel reference
    """
    try:
        x_spacing, y_spacing, z_spacing = float(x_y_z_spacing[0]), float(x_y_z_spacing[1]), float(x_y_z_spacing[2])
        origin_x, origin_y, origin_z = x_y_z_origin

        z_rot_vector = np.cross(x_y_rotation_vectors[:3], x_y_rotation_vectors[3:6])
        array_pixel_coord = array_pixel_coord.astype(dtype=np.float64)
        array_pixel_coord[:, 0] = ((array_pixel_coord[:, 0] * x_spacing)
                                   / (x_y_rotation_vectors[0] + x_y_rotation_vectors[3] + z_rot_vector[0])) + origin_x
        array_pixel_coord[:, 1] = ((array_pixel_coord[:, 1] * y_spacing)
                                   / (x_y_rotation_vectors[1] + x_y_rotation_vectors[4] + z_rot_vector[1])) + origin_y
        array_pixel_coord[:, 2] = - ((array_pixel_coord[:, 2] * z_spacing)
                                     / (x_y_rotation_vectors[2] + x_y_rotation_vectors[5] + z_rot_vector[2])) + origin_z
    except (ZeroDivisionError, TypeError):
        logging.error("One of the given information is does not fit template")

    return array_pixel_coord


def generate_3d_image_from_series(image_shape: Tuple[int, int, int], series_folder: str,
                                  x_y_z_spacing: Tuple[float, float, float], x_y_z_origin: List[float],
                                  x_y_z_rotation_vectors: List[float]) -> np.ndarray:
    """
    This method will create à 3d numpy array from a all the images in a series folder.

    :param image_shape: shape of the desired 3d image
    :param series_folder: folder containing all the images and no other
    :param x_y_z_spacing: spacial dimension of a voxel
    :param x_y_z_origin: origin of the image in patient coordinates
    :param x_y_z_rotation_vectors: image axes in the patient coordinates
    :return:
    """
    initial_array = np.zeros(image_shape)
    for sub_items in os.listdir(series_folder):
        path_to_item = os.path.join(series_folder, sub_items)
        dicom = pydicom.dcmread(path_to_item)
        slice_number = convert_real_coord_to_pixel_coord(np.asarray([dicom.ImagePositionPatient]), x_y_z_spacing,
                                                         x_y_z_origin, x_y_z_rotation_vectors)[0, 2]
        initial_array[slice_number] = dicom.pixel_array

    return initial_array
