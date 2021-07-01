import logging
import os
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pydicom
from PIL import Image, ImageDraw
from extraction_pipeline_components.search_instance_and_convert_coord_in_pixel import convert_real_coord_to_pixel_coord, \
    extract_positionning_informations, find_instance_in_folder


def extract_masks_for_each_organs_for_each_slices(rt_struct_file_path, study_folder):
    open_dicom = pydicom.dcmread(rt_struct_file_path)
    try:
        if open_dicom.Modality == "RTSTRUCT":
            first_image_uid = open_dicom.ReferencedFrameOfReferenceSequence[0][0x3006,
                                                                               0x0012][0][0x3006,
                                                                                          0x0014][0][0x3006,
                                                                                                     0x0016][0][0x0008,
                                                                                                                0x1155].value

            path_to_reference_frame = find_instance_in_folder(first_image_uid, study_folder)
            img_shape, x_y_z_spacing, \
            x_y_z_origin, x_y_z_rotation_vectors = extract_positionning_informations(path_to_reference_frame)

            json_version_dicom = open_dicom.to_json_dict()
            contours_context_dict = extract_contour_context_info(json_version_dicom)
            contours_and_image_dict = extract_contour_mask_and_image(json_version_dicom, img_shape, x_y_z_spacing,
                                   x_y_z_origin, x_y_z_rotation_vectors, study_folder)

            for contours in contours_context_dict.keys():
                contours_context_dict[contours].update(contours_and_image_dict[contours])

            return contours_context_dict

        logging.warning(f"")
        return {}

    except KeyError:
        logging.warning(f"")
        return {}


def extract_contour_context_info(json_dict_of_dicom_rt_struct):
    structure_sequence = json_dict_of_dicom_rt_struct["30060020"]["Value"]
    roi_name_dict = {}
    for roi in structure_sequence:
        roi_name_dict[roi["30060022"]["Value"][0]] = {"ROIName": roi["30060026"]["Value"][0]}

    observation_sequence = json_dict_of_dicom_rt_struct["30060080"]["Value"]
    observation_label = {}
    for roi in observation_sequence:
        observation_label[roi["30060084"]["Value"][0]] = {"ROIObservationLabel":  roi["30060085"]["Value"][0]}

    for roi in roi_name_dict.keys():
        roi_name_dict[roi].update(observation_label[roi])

    return roi_name_dict


def extract_contour_mask_and_image(json_dict_of_dicom_rt_struct, img_shape, x_y_z_spacing,
                                   x_y_z_origin, x_y_z_rotation_vectors, study_folder):
    roi_contour_sequence = json_dict_of_dicom_rt_struct["30060039"]["Value"]
    roi_contours_dict = {}
    for roi in roi_contour_sequence:
        roi_number = roi["30060084"]["Value"][0]
        slices_dict = {}
        for slice in roi["30060040"]["Value"]:
            contour_data = np.asarray(slice["30060050"]["Value"], dtype=np.float64)
            data_array = contour_data.reshape((contour_data.shape[0] // 3, 3))
            slice_z = data_array[0, 2]
            pixel_tuples = convert_real_coordinates_into_pixel_tuple_coordinates(data_array, x_y_z_spacing,
                                                                                 x_y_z_origin, x_y_z_rotation_vectors)
            mask = produce_mask_from_contour_coord(pixel_tuples, img_shape)
            image_uid = slice["30060016"]["Value"][0]["00081155"]["Value"][0]
            image_path = find_instance_in_folder(image_uid, study_folder)
            image = pydicom.dcmread(image_path).pixel_array
            slices_dict[slice_z] = {"mask": mask, "image": image}

        roi_contours_dict[roi_number] = slices_dict
    return roi_contours_dict


def convert_real_coordinates_into_pixel_tuple_coordinates(array_x_y_z_coord: np.ndarray,
                                                          x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors):
    pixel_coodinates = convert_real_coord_to_pixel_coord(array_x_y_z_coord, x_y_z_spacing, x_y_z_origin,
                                                         x_y_z_rotation_vectors)
    pixel_coords = [(x, y) for x, y, _ in pixel_coodinates]

    return pixel_coords


def produce_mask_from_contour_coord(coord: list, img_shape):
    img = Image.new(mode='L', size=img_shape, color=0)
    ImageDraw.Draw(img).polygon(xy=coord, outline=0, fill=1)
    mask = np.array(img).astype(bool)

    return mask


path = r"E:\DICOMS\VS-SEG-001\09-04-1994-Avanto RoutineImage Guidance-88886\94436\1-1.dcm"
dict_im = extract_masks_for_each_organs_for_each_slices(path, r"E:\DICOMS\VS-SEG-001\09-04-1994-Avanto RoutineImage Guidance-88886")

for roi in dict_im.keys():
    slices = list(dict_im[roi].keys())
    mask = dict_im[roi][slices[4]]['mask']
    image = dict_im[roi][slices[4]]['image']
    plt.imshow(image)
    plt.imshow(mask, alpha=0.5)
    plt.show()