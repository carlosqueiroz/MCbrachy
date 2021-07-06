import logging
from typing import List, Tuple

from extraction_pipeline_components.mask_structure_classes import Structures, Mask, SliceMask
import numpy as np
import pydicom
from PIL import Image, ImageDraw

from extraction_pipeline_components.search_instance_and_convert_coord_in_pixel import convert_real_coord_to_pixel_coord, \
    extract_positionning_informations, find_instance_in_folder


def extract_masks_for_each_organs_for_each_slices(rt_struct_file_path: str, study_folder: str) -> Structures or None:
    """
    This method will extract all information relative to the contours stored in the dicom rt struct.
    In order to keep all the information organized, a Structure object will be created along with
    all the Mask and SliceMask objects required to contain all the information

    :param rt_struct_file_path: path to the RTSTRUCT Diocm containing the desired rois
    :param study_folder: path to the folder containing the whole study

    :return: a Structure object containing all contours
    """
    open_dicom = pydicom.dcmread(rt_struct_file_path)
    try:
        if open_dicom.Modality == "RTSTRUCT":
            all_images_uids = open_dicom.ReferencedFrameOfReferenceSequence[0][0x3006,
                                                                               0x0012][0][0x3006,
                                                                                          0x0014][0][0x3006,
                                                                                                     0x0016]

            first_image_uid = all_images_uids[0][0x0008, 0x1155].value
            path_to_reference_frame = find_instance_in_folder(first_image_uid, study_folder)
            img_shape_2d, x_y_z_spacing, \
            x_y_z_origin, x_y_z_rotation_vectors = extract_positionning_informations(path_to_reference_frame)
            img_shape = len(all_images_uids.value), img_shape_2d[0], img_shape_2d[1]

            structure = Structures(img_shape, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors, list_of_masks=[],
                                   study_folder=study_folder)
            json_version_dicom = open_dicom.to_json_dict()
            contours_context_dict = extract_contour_context_info(json_version_dicom)
            contours_and_image_dict = extract_contour_mask_and_image(json_version_dicom, img_shape, x_y_z_spacing,
                                                                     x_y_z_origin, x_y_z_rotation_vectors)

            list_of_masks = []
            for contours in contours_and_image_dict.keys():
                roi_name = contours_context_dict[contours]['ROIName']
                roi_observation_label = contours_context_dict[contours]['ROIObservationLabel']
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

        logging.warning(f"")
        return None

    except KeyError:
        logging.warning(f"")
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
            roi_name_dict[roi["30060022"]["Value"][0]] = {"ROIName": roi["30060026"]["Value"][0]}
        except KeyError:
            roi_name_dict[roi["30060022"]["Value"][0]] = {"ROIName": ""}

    observation_sequence = json_dict_of_dicom_rt_struct["30060080"]["Value"]
    observation_label = {}
    for roi in observation_sequence:
        try:
            observation_label[roi["30060084"]["Value"][0]] = {"ROIObservationLabel": roi["30060085"]["Value"][0]}
        except KeyError:
            observation_label[roi["30060084"]["Value"][0]] = {"ROIObservationLabel": ""}

    for roi in roi_name_dict.keys():
        roi_name_dict[roi].update(observation_label[roi])

    return roi_name_dict


def extract_contour_mask_and_image(json_dict_of_dicom_rt_struct: dict, img_shape: Tuple[int, int, int],
                                   x_y_z_spacing: Tuple[float, float, float], x_y_z_origin: List[float],
                                   x_y_z_rotation_vectors: List[float]) -> dict:
    """
    This method will use the rt struct json dict to extrac all of the masks and
    associated image uid. The output of this method will be in pixel coordinates.

    :param json_dict_of_dicom_rt_struct: json_dit associated to the original Dicom
    :param img_shape: shape of the 3d image
    :param x_y_z_spacing: spacial dimension of a voxel
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
                contour_data = np.asarray(slices["30060050"]["Value"], dtype=np.float64)
                data_array = contour_data.reshape((contour_data.shape[0] // 3, 3))
                slice_z = convert_real_coord_to_pixel_coord(np.asarray([data_array[0]]), x_y_z_spacing,
                                                            x_y_z_origin, x_y_z_rotation_vectors)[0, 2]

                pixel_tuples = convert_real_coordinates_into_pixel_tuple_coordinates(data_array, x_y_z_spacing,
                                                                                     x_y_z_origin,
                                                                                     x_y_z_rotation_vectors)
                mask = produce_mask_from_contour_coord(pixel_tuples, (img_shape[1], img_shape[2]))
                image_uid = slices["30060016"]["Value"][0]["00081155"]["Value"][0]
                image = image_uid
                slices_dict[slice_z] = {"mask": mask, "image_uid": image}

            roi_contours_dict[roi_number] = slices_dict
        except KeyError:
            logging.warning(f"The roi {roi_number} does not have any images associated or something went wrong")

    return roi_contours_dict


def convert_real_coordinates_into_pixel_tuple_coordinates(array_x_y_z_coord: np.ndarray,
                                                          x_y_z_spacing, x_y_z_origin,
                                                          x_y_z_rotation_vectors) -> List[Tuple[int, int]]:
    """
    This method will convert the array of patient coordinates into
    a list of tuple pixel coordinates. Please note, that the z values
    are ignored because this method is simply used before the produce_mask_from_contour_coord.

    :param array_x_y_z_coord: the array containing all the x y z coordinates
    :param x_y_z_spacing: spacial dimension of a voxel
    :param x_y_z_origin: origin of the image in patient coordinates
    :param x_y_z_rotation_vectors: image axes in the patient coordinates

    :return: the list of the tuples associated to each contour point
    """
    pixel_coodinates = convert_real_coord_to_pixel_coord(array_x_y_z_coord, x_y_z_spacing, x_y_z_origin,
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
