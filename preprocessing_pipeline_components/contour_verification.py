import pydicom
import logging

from typing import List


def verify_if_all_required_contours_are_present(path_to_dicom: str, desired_rois: List[str]) -> bool:
    """

    :param path_to_dicom:
    :param desired_rois:
    :return:
    """
    open_dicom = pydicom.dcmread(path_to_dicom)
    patient_id = open_dicom.PatientID
    instance_uid = open_dicom.SOPInstanceUID
    try:
        if open_dicom.Modality == "RTSTRUCT":
            json_version_dicom = open_dicom.to_json_dict()
            structure_set_roi_sequence = json_version_dicom["30060020"]

            all_roi_names = []
            for roi in structure_set_roi_sequence:
                roi_name = roi["30060026"]
                all_roi_names.append(roi_name)

            if all_roi_names in desired_rois:  # change desired_rois for all possible values
                # associated with same organs or structures
                return True

            return False

        logging.warning(f"Instance {instance_uid} of patient {patient_id} is not a RTSTRUC as expected."
                        f"\n The verification of contours automatically returned false")
        return False

    except KeyError:
        logging.warning(f"Something went wrong while searching for contours for instance"
                        f" {instance_uid} of patient {patient_id}."
                        f"\n The verification of contours automatically returned false")
        return False





