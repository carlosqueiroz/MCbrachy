import logging
from typing import Tuple, List

import numpy as np
import pydicom

from extraction_pipeline_components.storage_objects.rt_dose_storage_classes import Dosimetry, DVHistogram


def convert_index_dose_grid_into_dosimetry(dose_index_grid: np.ndarray, dose_grid_scaling: float) -> np.ndarray:
    """
    This method will simply apply the dose grid scaling to the dose indexes.

    :param dose_index_grid:
    :param dose_grid_scaling:

    :return: scaled dose
    """
    scaled_dose = dose_grid_scaling * dose_index_grid

    return scaled_dose


def extract_dosimetry(rt_dose_file_path: str) -> Dosimetry or None:
    """
    this method will extract the dosimetric data stored in
    a rt dose Dicom. Along with the dose grid, all context info and
    dvh are also extracted and stored into Dosimetry and DVHistogram
    objects



    :param rt_dose_file_path: path to the rt dose Dicom file

    :return: Dosimetry object
    """
    open_dicom = pydicom.dcmread(rt_dose_file_path)
    try:
        if open_dicom.Modality == "RTDOSE":
            img_shape_3d, x_y_z_spacing, x_y_z_origin, \
            x_y_z_rotation_vectors = extract_positioning_from_rt_dose(rt_dose_file_path)
            dose_units = open_dicom.DoseUnits
            dose_grid_scaling = float(open_dicom.DoseGridScaling)
            dose_data = convert_index_dose_grid_into_dosimetry(open_dicom.pixel_array, dose_grid_scaling)

            json_version_dicom = open_dicom.to_json_dict()

            # extracting referenced uids of rt dose, rt plan and rt dose
            # ------------------------------------------------------------
            rt_dose_uid = json_version_dicom["00080018"]["Value"][0]
            if "300C0002" in json_version_dicom.keys():
                rt_plan_uid = str(json_version_dicom["300C0002"]["Value"][0]["00081155"]["Value"][0])
            else:
                rt_plan_uid = None

            if "300C0060" in json_version_dicom.keys():
                rt_struct_uid = str(json_version_dicom["300C0060"]["Value"][0]["00081155"]["Value"][0])
            else:
                rt_struct_uid = None
            # ------------------------------------------------------------

            dose = Dosimetry(rt_dose_uid, dose_data, dose_units, x_y_z_origin, x_y_z_rotation_vectors, img_shape_3d,
                             x_y_z_spacing,
                             dose_grid_scaling, rt_plan_uid, rt_struct_uid, [])

            if "30040050" in json_version_dicom.keys():
                all_dvh_dict = extract_dvh(rt_dose_file_path)
                list_of_dvh = []
                for roi_number in all_dvh_dict.keys():
                    list_of_dvh.append(DVHistogram(roi_number, all_dvh_dict[roi_number]["dose_units"],
                                                   all_dvh_dict[roi_number]["dvh_scaling"],
                                                   all_dvh_dict[roi_number]["volume_units"],
                                                   all_dvh_dict[roi_number]["nb_bins"],
                                                   all_dvh_dict[roi_number]["dvh_data"],
                                                   all_dvh_dict[roi_number]["max_dose"],
                                                   all_dvh_dict[roi_number]["min_dose"],
                                                   all_dvh_dict[roi_number]["mean_dose"],
                                                   dose))

                dose.add_dvhistograms(list_of_dvh)

            return dose

        logging.warning(f"")
        return None

    except (KeyError, AttributeError):
        logging.warning(f"")
        return None


def extract_dvh(path_to_rt_dose):
    """
    This method will extract all the information relative
    to the stored dvhs.

    :param path_to_rt_dose: path to the rt dose Dicom file

    :return: dict containing all dvh information
    """
    open_dicom = pydicom.dcmread(path_to_rt_dose)
    json_dicom = open_dicom.to_json_dict()
    try:
        if open_dicom.Modality == "RTDOSE":
            all_dvh = {}
            dvh_sequence = json_dicom["30040050"]["Value"]
            for dvh in dvh_sequence:
                roi_number = int(dvh["30040060"]["Value"][0]["30060084"]["Value"][0])
                all_dvh[roi_number] = {}
                all_dvh[roi_number]["dose_units"] = str(dvh["30040002"]["Value"][0])
                all_dvh[roi_number]["dvh_scaling"] = float(dvh["30040052"]["Value"][0])
                all_dvh[roi_number]["volume_units"] = str(dvh["30040054"]["Value"][0])
                all_dvh[roi_number]["nb_bins"] = int(dvh["30040056"]["Value"][0])
                all_dvh[roi_number]["min_dose"] = float(dvh["30040070"]["Value"][0])
                all_dvh[roi_number]["max_dose"] = float(dvh["30040072"]["Value"][0])
                all_dvh[roi_number]["mean_dose"] = float(dvh["30040074"]["Value"][0])
                all_dvh[roi_number]["dvh_data"] = convert_dvh_data_into_value_table_array(
                    convert_index_dose_grid_into_dosimetry(
                        np.asarray(dvh["30040058"]["Value"],
                                   dtype=np.float32),
                        dvh["30040052"]["Value"][0]), all_dvh[roi_number]["nb_bins"])

            return all_dvh

        logging.warning(f"")
        return {}

    except KeyError:
        logging.warning(f"")
        return {}


def convert_dvh_data_into_value_table_array(value_array: np.array, nb_bins: int) -> np.ndarray:
    """
    This method will convert the dvh array [V1, bin_size D1, V2, bin_size D2]
    into a 2d array
    [[V1, V2, V3, ..].
     [D1, D2, D3, ...]
     [bin_size D1, bin_size D2, bin_size D3, ...]]
     where D1 is set to be the center of the bin

    :param value_array: initial 1d array
    :param nb_bins: number of bins

    :return: the 2d array with the split data
    """
    empty_array = np.zeros((3, nb_bins), dtype=np.float32)
    current_dose = 0
    for i in range(0, nb_bins):
        empty_array[2, i] = value_array[2 * i]
        current_dose += value_array[2 * i] / 2
        empty_array[0, i] = current_dose
        current_dose += value_array[2 * i] / 2
        empty_array[1, i] = value_array[2 * i + 1]

    return empty_array


def extract_positioning_from_rt_dose(path_to_rt_dose: str) -> Tuple[Tuple[int, int, int], Tuple[float, float, float],
                                                                    List[float], List[float]]:
    """
    This method will extract the location and
    orientation of the dose grid in patient coordinates.
    This information will be extracted along with the pixel spacing and the dose grid dimensions.

    :param path_to_rt_dose: path to the rt dose Dicom file

    :return: all the positioning informations
    """
    dicom = pydicom.dcmread(path_to_rt_dose)
    img_shape_3d = int(dicom.NumberOfFrames), int(dicom.Rows), int(dicom.Columns)
    if dicom.SliceThickness is None:
        slice_thickness = -1
    else:
        slice_thickness = dicom.SliceThickness

    x_y_z_spacing = float(dicom.PixelSpacing[0]), float(dicom.PixelSpacing[1]), float(slice_thickness)
    x_y_z_origin = dicom.ImagePositionPatient
    x_y_z_rotation_vectors = dicom.ImageOrientationPatient

    return img_shape_3d, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors
