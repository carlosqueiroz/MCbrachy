import logging

import numpy as np
import pydicom


from extraction_pipeline_components.storage_objects.rt_dose_storage_classes import Dosimetry, DVHistogram


def convert_index_dose_grid_into_dosimetry(dose_index_grid, dose_grid_scaling):
    """

    :param dose_index_grid:
    :param dose_grid_scaling:
    :return:
    """
    scaled_dose = dose_grid_scaling * dose_index_grid

    return scaled_dose


def extract_dosimetry(rt_dose_file_path):
    """

    :param rt_dose_file_path:
    :return:
    """
    open_dicom = pydicom.dcmread(rt_dose_file_path)
    try:
        if open_dicom.Modality == "RTDOSE":
            img_shape_3d, x_y_z_spacing, x_y_z_origin, \
            x_y_z_rotation_vectors = extract_positioning_from_rt_dose(rt_dose_file_path)
            dose_units = open_dicom.DoseUnits
            dose_grid_scaling = float(open_dicom.DoseGridScaling)
            dose_data = convert_index_dose_grid_into_dosimetry(open_dicom.pixel_array, dose_grid_scaling)

            rt_plan_uid = open_dicom.ReferencedRTPlanSequence[0].ReferencedSOPInstanceUID
            rt_struct_uid = open_dicom.ReferencedStructureSetSequence[0].ReferencedSOPInstanceUID

            dose = Dosimetry(dose_data, dose_units, x_y_z_origin, x_y_z_rotation_vectors, img_shape_3d, x_y_z_spacing,
                             dose_grid_scaling, rt_plan_uid, rt_struct_uid, [])

            if open_dicom.DVHSequence is not None:
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


def extract_dvh(rt_dose_file_path):
    """

    :param rt_dose_file_path:
    :return:
    """
    open_dicom = pydicom.dcmread(rt_dose_file_path)
    json_dicom = open_dicom.to_json_dict()
    try:
        if open_dicom.Modality == "RTDOSE":
            all_dvh = {}
            dvh_sequence = json_dicom["30040050"]["Value"]
            for dvh in dvh_sequence:
                roi_number = int(dvh["30040060"]["Value"][0]["30060084"]["Value"][0])
                all_dvh[roi_number] = {}
                all_dvh[roi_number]["dose_units"] = dvh["30040002"]["Value"][0]
                all_dvh[roi_number]["dvh_scaling"] = float(dvh["30040052"]["Value"][0])
                all_dvh[roi_number]["volume_units"] = dvh["30040054"]["Value"][0]
                all_dvh[roi_number]["nb_bins"] = int(dvh["30040056"]["Value"][0])
                all_dvh[roi_number]["min_dose"] = float(dvh["30040070"]["Value"][0])
                all_dvh[roi_number]["max_dose"] = float(dvh["30040072"]["Value"][0])
                all_dvh[roi_number]["mean_dose"] = float(dvh["30040074"]["Value"][0])
                all_dvh[roi_number]["dvh_data"] = convert_index_dose_grid_into_dosimetry(
                    np.asarray(dvh["30040058"]["Value"],
                               dtype=np.float32),
                    dvh["30040052"]["Value"][0])

            return all_dvh

        logging.warning(f"")
        return {}

    except KeyError:
        logging.warning(f"")
        return {}


def extract_slice_thickness_from_rt_plan(rt_plan_uid):
    return 1


def extract_positioning_from_rt_dose(path_to_rt_dose):
    """
    
    :param path_to_rt_dose:
    :return:
    """
    dicom = pydicom.dcmread(path_to_rt_dose)
    img_shape_3d = int(dicom.NumberOfFrames), int(dicom.Rows), int(dicom.Columns)
    if dicom.SliceThickness is None:
        slice_thickness = extract_slice_thickness_from_rt_plan(dicom.ReferencedRTPlanSequence[0].ReferencedSOPInstanceUID)
    else:
        slice_thickness = dicom.SliceThickness

    x_y_z_spacing = float(dicom.PixelSpacing[0]), float(dicom.PixelSpacing[1]), float(slice_thickness)
    x_y_z_origin = dicom.ImagePositionPatient
    x_y_z_rotation_vectors = dicom.ImageOrientationPatient

    return img_shape_3d, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors


path = r"E:\manifest-1549495779734\HNSCC-3DCT-RT\HN_P001\10-22-2009-RTHEADNECK Adult-72945\41.000000-Eclipse " \
       r"Doses-09094\1-1.dcm"

er = extract_dosimetry(path)
print(len(er.list_of_dvh))
