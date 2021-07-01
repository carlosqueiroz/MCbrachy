import numpy as np
import pydicom
import os
import logging


def extract_positionning_informations(path_to_the_frame_reference):
    dicom = pydicom.dcmread(path_to_the_frame_reference)
    img_arr = dicom.pixel_array
    img_shape = img_arr.shape
    x_y_z_spacing = dicom.PixelSpacing[0], dicom.PixelSpacing[1], dicom.SliceThickness
    x_y_z_origin = dicom.ImagePositionPatient
    x_y_z_rotation_vectors = dicom.ImageOrientationPatient

    return img_shape, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors


def find_frame_of_reference_in_folder(frame_of_reference_UID, path_to_folder):
    for sub_items in os.listdir(path_to_folder):
        path_to_item = os.path.join(path_to_folder, sub_items)
        if os.path.isdir(path_to_item):
            found_file = find_frame_of_reference_in_folder(frame_of_reference_UID, path_to_item)
            if found_file is not None:
                return found_file

        if path_to_item.endswith(".dcm"):
            try:
                dicom = pydicom.dcmread(path_to_item)
                if dicom.FrameOfReferenceUID == frame_of_reference_UID:
                    return path_to_item

            except AttributeError:
                logging.info(f"No FrameOfReferenceUID in file {path_to_item}")

    return None


def find_instance_in_folder(sop_instance_UID, path_to_folder):
    for sub_items in os.listdir(path_to_folder):
        path_to_item = os.path.join(path_to_folder, sub_items)
        if os.path.isdir(path_to_item):
            found_file = find_instance_in_folder(sop_instance_UID, path_to_item)
            if found_file is not None:
                return found_file

        if path_to_item.endswith(".dcm"):
            try:
                dicom = pydicom.dcmread(path_to_item)
                if dicom.SOPInstanceUID == sop_instance_UID:
                    return path_to_item

            except AttributeError:
                logging.info(f"No FrameOfReferenceUID in file {path_to_item}")

    return None


def convert_real_coord_to_pixel_coord(array_x_y_z_coord: np.ndarray,
                                      x_y_z_spacing, x_y_z_origin, x_y_rotation_vectors):
    x_spacing, y_spacing, z_spacing = float(x_y_z_spacing[0]), float(x_y_z_spacing[1]), float(x_y_z_spacing[2])
    origin_x, origin_y, origin_z = x_y_z_origin
    z_rot_vector = np.cross(x_y_rotation_vectors[:3], x_y_rotation_vectors[3:6])
    array_x_y_z_coord[:, 0] = np.ceil((array_x_y_z_coord[:, 0] - origin_x)
                                      * (x_y_rotation_vectors[0] + x_y_rotation_vectors[3] + z_rot_vector[0])
                                      / x_spacing)
    array_x_y_z_coord[:, 1] = np.ceil((array_x_y_z_coord[:, 1] - origin_y)
                                      * (x_y_rotation_vectors[1] + x_y_rotation_vectors[4] + z_rot_vector[1])
                                      / y_spacing)
    array_x_y_z_coord[:, 2] = np.ceil((array_x_y_z_coord[:, 2] - origin_z)
                                      * (x_y_rotation_vectors[2] + x_y_rotation_vectors[5] + z_rot_vector[2])
                                      / z_spacing)

    return array_x_y_z_coord


def convert_pixel_coord_to_real_coord(array_pixel_coord: np.ndarray,
                                      x_y_z_spacing, x_y_z_origin, x_y_rotation_vectors):
    x_spacing, y_spacing, z_spacing = float(x_y_z_spacing[0]), float(x_y_z_spacing[1]), float(x_y_z_spacing[2])
    origin_x, origin_y, origin_z = x_y_z_origin
    z_rot_vector = np.cross(x_y_rotation_vectors[:3], x_y_rotation_vectors[3:6])
    array_pixel_coord[:, 0] = ((array_pixel_coord[:, 0] * x_spacing)
                               / (x_y_rotation_vectors[0] + x_y_rotation_vectors[3] + z_rot_vector[0])) + origin_x
    array_pixel_coord[:, 1] = ((array_pixel_coord[:, 1] * y_spacing)
                               / (x_y_rotation_vectors[1] + x_y_rotation_vectors[4] + z_rot_vector[1])) + origin_y
    array_pixel_coord[:, 2] = ((array_pixel_coord[:, 2] * x_spacing)
                               / (x_y_rotation_vectors[2] + x_y_rotation_vectors[5] + z_rot_vector[2])) + origin_z

    return array_pixel_coord
