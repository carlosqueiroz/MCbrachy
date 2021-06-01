import pydicom
import logging


def verify_if_brachy_treatment_type(path_to_dicom: str, treatment_type: str = "LDR",
                                    thorough_verification: bool = False) -> bool:
    """

    :param path_to_dicom:
    :param treatment_type:
    :param thorough_verification:
    :return:
    """

    open_dicom = pydicom.dcmread(path_to_dicom)
    patient_id = open_dicom.PatientID
    instance_uid = open_dicom.SOPInstanceUID
    try:
        if open_dicom.Modality == "RTPLAN":
            json_version_dicom = open_dicom.to_json_dict()
            brachy_treatment_type = json_version_dicom["300A0202"]["Value"][0]
            if thorough_verification and brachy_treatment_type == treatment_type:
                if source_verification():
                    return True
                return False

            if brachy_treatment_type == treatment_type:
                return True

            return False

        logging.warning(f"Instance {instance_uid} of patient {patient_id} is not a RTPLAN as expected."
                        f"\n The verification of brachy treatment plan automatically returned false")
        return False

    except KeyError:
        logging.warning(f"Something went wrong while searching for brachy treatment relative information for instance"
                        f" {instance_uid} of patient {patient_id}."
                        f"\n The verification of brachy treatment plan automatically returned false")
        return False


def source_verification():
    return False
