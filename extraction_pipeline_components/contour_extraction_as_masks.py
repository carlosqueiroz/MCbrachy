import json
import logging
import os
from itertools import chain
from typing import List, Tuple

from extraction_pipeline_components.storage_objects.rt_struct_storage_classes import Structures, Mask, SliceMask
import numpy as np
import pydicom
from PIL import Image, ImageDraw

from extraction_pipeline_components.utils.search_instance_and_convert_coord_in_pixel import \
    convert_real_coord_to_pixel_coord, \
    extract_positionning_informations, find_instance_in_folder
from root import ROOT

contour_vocab_path = os.path.join(ROOT, "extraction_pipeline_components", "storage_objects", "storing_files",
                                  "contour_vocabulary.json")


def get_key_from_value(dict, val):
    for key, value in dict.items():
        if val in value:
            return key


def extract_masks_for_each_organs_for_each_slices(rt_struct_file_path: str, study_folder: str) -> Structures or None:
    """
    This method will extract all information relative to the contours stored in the dicom rt struct.
    In order to keep all the information organized, a Structure object will be created along with
    all the Mask and SliceMask objects required to contain all the information

    :param rt_struct_file_path: path to the RTSTRUCT Dicom containing the desired rois
    :param study_folder: path to the folder containing the whole study

    :return: a Structure object containing all contours
    """
    open_dicom = pydicom.dcmread(rt_struct_file_path)
    try:
        if open_dicom.Modality == "RTSTRUCT":
            rt_struct_uid = str(open_dicom.SOPInstanceUID)
            image_ref_dict = build_image_references_dict(open_dicom.to_json_dict())
            path_to_reference_frame = find_instance_in_folder(image_ref_dict[1], study_folder)

            if path_to_reference_frame is None:
                raise TypeError

            img_shape_2d, z_y_x_spacing, \
            x_y_z_origin, x_y_z_rotation_vectors = extract_positionning_informations(path_to_reference_frame)
            img_shape = len(image_ref_dict.keys()), img_shape_2d[0], img_shape_2d[1]

            structure = Structures(rt_struct_uid, img_shape, z_y_x_spacing, x_y_z_origin, x_y_z_rotation_vectors,
                                   list_of_masks=[], study_folder=study_folder)
            json_version_dicom = open_dicom.to_json_dict()
            contours_context_dict = extract_contour_context_info(json_version_dicom)
            contours_and_image_dict = extract_contour_mask_and_image(json_version_dicom, img_shape, z_y_x_spacing,
                                                                     x_y_z_origin, x_y_z_rotation_vectors,
                                                                     image_ref_dict)
            list_of_masks = []
            for contours in contours_and_image_dict.keys():
                roi_name = contours_context_dict[contours]['ROIName']
                roi_observation_label = contours_context_dict[contours]['ROIObservationLabel']
                contour_vocabulary_file = open(contour_vocab_path, "r")
                contour_vocabulary = json.loads(contour_vocabulary_file.read())
                contour_vocabulary_file.close()
                if roi_name in chain(*contour_vocabulary.values()):
                    roi_name = get_key_from_value(contour_vocabulary, roi_name)
                if roi_observation_label in chain(*contour_vocabulary.values()):
                    roi_observation_label = get_key_from_value(contour_vocabulary, roi_observation_label)

                mask = Mask(roi_name, roi_observation_label, structure, list_mask_slices=[])
                list_of_slices = []
                for slices in contours_and_image_dict[contours].keys():
                    list_of_slices.append(SliceMask(contours_and_image_dict[contours][slices]['mask'],
                                                    contours_and_image_dict[contours][slices]['image_uid'],
                                                    slices, mask))
                mask.add_slices(list_of_slices)
                list_of_masks.append(mask)

            structure.add_masks(list_of_masks)

            return structure

        logging.warning(f"{rt_struct_file_path} is not a RTSTRUCT as expected")
        return None

    except (KeyError, TypeError):
        logging.warning(f"Something went wrong while extracting the contours")
        return None


def extract_contour_context_info(json_dict_of_dicom_rt_struct: dict) -> dict:
    """
    This method will extract the roi name and the obseration label of every contour

    :param json_dict_of_dicom_rt_struct: json_dit associated to the original Dicom

    :return: a dictionary containing both roi name and observation label for each contour
    """
    structure_sequence = json_dict_of_dicom_rt_struct["30060020"]["Value"]
    roi_name_dict = {}
    for roi in structure_sequence:
        try:
            roi_name_dict[roi["30060022"]["Value"][0]] = {"ROIName": str(roi["30060026"]["Value"][0])}
        except KeyError:
            roi_name_dict[roi["30060022"]["Value"][0]] = {"ROIName": ""}

    observation_sequence = json_dict_of_dicom_rt_struct["30060080"]["Value"]
    observation_label = {}
    for roi in observation_sequence:
        try:
            if "30060085" in roi.keys():
                observation_label[roi["30060084"]["Value"][0]] = {
                    "ROIObservationLabel": str(roi["30060085"]["Value"][0])}
            else:
                observation_label[roi["30060084"]["Value"][0]] = {
                    "ROIObservationLabel": str(roi["30060088"]["Value"][0])}

        except KeyError:
            observation_label[roi["30060084"]["Value"][0]] = {"ROIObservationLabel": ""}

    for roi in roi_name_dict.keys():
        roi_name_dict[roi].update(observation_label[roi])

    return roi_name_dict


def extract_contour_mask_and_image(json_dict_of_dicom_rt_struct: dict, img_shape: Tuple[int, int, int],
                                   z_y_x_spacing: Tuple[float, float, float], x_y_z_origin: List[float],
                                   x_y_z_rotation_vectors: List[float], ref_images_dict) -> dict:
    """
    This method will use the rt struct json dict to extrac all of the masks and
    associated image uid. The output of this method will be in pixel coordinates.

    :param ref_images_dict: dictionary of all the images uids
    :param json_dict_of_dicom_rt_struct: json_dit associated to the original Dicom
    :param img_shape: shape of the 3d image
    :param z_y_x_spacing: spacial dimension of a voxel
    :param x_y_z_origin: origin of the image in patient coordinates
    :param x_y_z_rotation_vectors: image axes in the patient coordinates

    :return:a dictionary containing both mask and image uid for each contour
    """

    roi_contour_sequence = json_dict_of_dicom_rt_struct["30060039"]["Value"]
    roi_contours_dict = {}
    for roi in roi_contour_sequence:
        roi_number = roi["30060084"]["Value"][0]
        slices_dict = {}
        try:
            for slices in roi["30060040"]["Value"]:
                if int(slices["30060046"]["Value"][0]) < 3:
                    continue
                contour_data = np.asarray(slices["30060050"]["Value"], dtype=np.float64)
                data_array = contour_data.reshape((contour_data.shape[0] // 3, 3))
                slice_z = convert_real_coord_to_pixel_coord(np.asarray([data_array[0]]), z_y_x_spacing,
                                                            x_y_z_origin, x_y_z_rotation_vectors)[0, 2]

                pixel_tuples = convert_real_coordinates_into_pixel_tuple_coordinates(data_array, z_y_x_spacing,
                                                                                     x_y_z_origin,
                                                                                     x_y_z_rotation_vectors)
                mask = produce_mask_from_contour_coord(pixel_tuples, (img_shape[1], img_shape[2]))

                if "30060016" in slices.keys():
                    image_uid = slices["30060016"]["Value"][0]["00081155"]["Value"][0]

                else:
                    image_uid = ref_images_dict[slice_z]

                image = image_uid
                if slice_z in slices_dict.keys():
                    added_mask = slices_dict[slice_z]["mask"].astype(int) + mask.astype(int)
                    mask_with_holes = np.ma.masked_where(added_mask == 1, added_mask).mask
                    slices_dict[slice_z]["mask"] = mask_with_holes
                else:
                    slices_dict[slice_z] = {"mask": mask, "image_uid": image}

            roi_contours_dict[roi_number] = slices_dict

        except KeyError:
            logging.warning(f"The roi {roi_number} does not have any images associated or something went wrong")

    return roi_contours_dict


def convert_real_coordinates_into_pixel_tuple_coordinates(array_x_y_z_coord: np.ndarray,
                                                          z_y_x_spacing, x_y_z_origin,
                                                          x_y_z_rotation_vectors) -> List[Tuple[int, int]]:
    """
    This method will convert the array of patient coordinates into
    a list of tuple pixel coordinates. Please note, that the z values
    are ignored because this method is simply used before the produce_mask_from_contour_coord.

    :param array_x_y_z_coord: the array containing all the x y z coordinates
    :param z_y_x_spacing: spacial dimension of a voxel
    :param x_y_z_origin: origin of the image in patient coordinates
    :param x_y_z_rotation_vectors: image axes in the patient coordinates

    :return: the list of the tuples associated to each contour point
    """
    pixel_coodinates = convert_real_coord_to_pixel_coord(array_x_y_z_coord, z_y_x_spacing, x_y_z_origin,
                                                         x_y_z_rotation_vectors)
    pixel_coords = [(x, y) for x, y, _ in pixel_coodinates]

    return pixel_coords


def produce_mask_from_contour_coord(coord: List[Tuple[int, int]], img_shape: Tuple[int, int]) -> np.ndarray:
    """
    This method creates an array mask from the contour coordinates

    :param coord: the list of all the coutour point coordinates
    :param img_shape: shape of the corresponding 2d image

    :return: the np.ndarray mask
    """
    img = Image.new(mode='L', size=img_shape, color=0)
    ImageDraw.Draw(img).polygon(xy=coord, outline=0, fill=1)
    mask = np.array(img).astype(bool)

    return mask


def build_image_references_dict(open_dicom_as_json: dict) -> dict:
    """
    This method will build a dictionary associating each slice to an
    image uid. This dictionary will be used when associating contours
    slices with its image.
    :param open_dicom_as_json: rt_struct dicom as json
    :return: the dictionary having slice number as key and uid as value
    """
    all_images_uids = \
    open_dicom_as_json["30060010"]["Value"][0]["30060012"]["Value"][0]["30060014"]["Value"][0]["30060016"]["Value"]

    ref_images_dict = {}
    if "00081160" not in all_images_uids[0].keys():
        it = 1
        for elements in all_images_uids:
            ref_images_dict[it] = str(elements["00081155"]["Value"][0])
            it += 1

    else:
        for elements in all_images_uids:
            it = int(elements["00081160"]["Value"][0])
            ref_images_dict[it] = str(elements["00081155"]["Value"][0])

    return ref_images_dict
