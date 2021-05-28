import os
import pydicom
import logging
from dicom_anonymiseur.anonymization import anonymize_dataset
from dicom_anonymiseur.util import hash_value


def anonymize_single_DICOM(dicom_file_path: str, anonymized_directory: str, new_patient_id: str = 'patient',
                           random_str: str = "", anonymized_study_folder: str = "study",
                           anonymized_series_folder: str = "series", anonymized_instance_number: int = 0) -> None:
    """
    This method...


    :param anonymized_study_folder:
    :param anonymized_instance_number:
    :param anonymized_series_folder:
    :param dicom_file_path: path and name of the dicom file to anonymize.
    :param anonymized_directory: directory where anonymized DICOMs will be sent.
    :param new_patient_id: Ne patient Id for the anonymized DICOMs
    :param random_str: string that will be added to the real UIDs in order to generate untraceable new UIDs
    :return:
    """

    loaded_dicom = pydicom.dcmread(dicom_file_path)
    patient_id = loaded_dicom.PatientID
    instance_uid = loaded_dicom.SOPInstanceUID
    logging.info(f"Anonymizing instance {instance_uid} of patient {patient_id}")
    loaded_dicom.remove_private_tags()
    anonymized_dicom = anonymize_dataset(loaded_dicom, random_str)
    anonymized_dicom.PatientID = new_patient_id
    anonymized_dicom.InstitutionName = hash_value(patient_id[:5])  # uses the institution part of the patient ID

    path_of_anonymized_dicom = os.path.join(anonymized_directory, new_patient_id, anonymized_study_folder,
                                            anonymized_series_folder)
    if not os.path.exists(path_of_anonymized_dicom):
        os.makedirs(path_of_anonymized_dicom)

    anonymized_location = os.path.join(path_of_anonymized_dicom,
                                       f'{anonymized_dicom.Modality}{anonymized_instance_number}.dcm')
    pydicom.dcmwrite(anonymized_location, anonymized_dicom)
    logging.info(f"Anonymized instance stored at {anonymized_location}")


def anonymize_whole_series(series_folder: str, anonymized_directory: str, new_patient_id: str = 'patient',
                           random_str: str = "", anonymized_study_folder: str = "study",
                           anonymized_series_folder: str = "series") -> None:
    """
    This method...


    :param series_folder:
    :param anonymized_study_folder:
    :param anonymized_series_folder:
    :param anonymized_directory: directory where anonymized DICOMs will be sent.
    :param new_patient_id: Ne patient Id for the anonymized DICOMs
    :param random_str: string that will be added to the real UIDs in order to generate untraceable new UIDs
    :return:
    """
    i = 0
    for files in os.listdir(series_folder):
        path_to_dicom = os.path.join(series_folder, files)
        anonymize_single_DICOM(path_to_dicom, anonymized_directory, new_patient_id, random_str, anonymized_study_folder,
                               anonymized_series_folder, i)
        i += 1


def anonymize_whole_study(study_folder: str, anonymized_directory: str, new_patient_id: str = 'patient',
                          random_str: str = "", anonymized_study_folder: str = "study") -> None:
    """
    This method...


    :param study_folder:
    :param anonymized_study_folder:
    :param anonymized_directory: directory where anonymized DICOMs will be sent.
    :param new_patient_id: Ne patient Id for the anonymized DICOMs
    :param random_str: string that will be added to the real UIDs in order to generate untraceable new UIDs
    :return:
    """
    i = 0
    for folders in os.listdir(study_folder):
        series_folder = os.path.join(study_folder, folders)
        anonymize_whole_series(series_folder, anonymized_directory, new_patient_id, random_str, anonymized_study_folder,
                               f"series{i}")
        i += 1


def anonymize_whole_patient(patient_folder: str, anonymized_directory: str, new_patient_id: str = 'patient',
                            random_str: str = "") -> None:
    """
    This method...


    :param patient_folder:
    :param anonymized_directory: directory where anonymized DICOMs will be sent.
    :param new_patient_id: Ne patient Id for the anonymized DICOMs
    :param random_str: string that will be added to the real UIDs in order to generate untraceable new UIDs
    :return:
    """
    i = 0
    for folders in os.listdir(patient_folder):
        study_folder = os.path.join(patient_folder, folders)
        anonymize_whole_study(study_folder, anonymized_directory, new_patient_id, random_str, f"study{i}")
        i += 1
