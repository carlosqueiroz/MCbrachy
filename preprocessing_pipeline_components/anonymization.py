import os
import pydicom
import logging
from dicom_anonymiseur.anonymization import anonymize_dataset
from dicom_anonymiseur.util import hash_value


def anonymize_single_DICOM(dicom_file_path: str, anonymized_directory: str, new_patient_id: str = None,
                           random_str: str = 'patient', series_folder: str = "series",
                           instance_number: int = 0) -> None:
    """
    This method...


    :param instance_number:
    :param series_folder:
    :param dicom_file_path: path and name of the dicom file to anonymize.
    :param anonymized_directory: directory where anonymized DICOMs will be sent.
    :param new_patient_id: Ne patient Id for the anonymized DICOMs
    :param random_str: string that will be added to the real UIDs in order to generate untraceable new UIDs
    :return:
    """

    loaded_dicom = pydicom.dcmread(dicom_file_path)
    patient_id = loaded_dicom.PatientID
    series_number = loaded_dicom.SeriesNumber
    instance_uid = loaded_dicom.SOPInstanceUID
    logging.info(f"Anonymizing instance {instance_uid} of patient {patient_id}")
    loaded_dicom.remove_private_tags()
    anonymized_dicom = anonymize_dataset(loaded_dicom, random_str)
    anonymized_dicom.PatientID = new_patient_id
    anonymized_dicom.InstitutionName = hash_value(patient_id[:5])  # uses the institution part of the patient ID

    path_of_anonymized_dicom = os.path.join(anonymized_directory, new_patient_id, series_folder)
    if not os.path.exists(path_of_anonymized_dicom):
        os.makedirs(path_of_anonymized_dicom)

    anonymized_location = os.path.join(path_of_anonymized_dicom, f'{anonymized_dicom.Modality}{instance_number}.dcm')
    pydicom.dcmwrite(anonymized_location, anonymized_dicom)
    logging.info(f"Anonymized instance stored at {anonymized_location}")

