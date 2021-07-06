import os
import pydicom
import logging
import preprocessing_pipeline_components.patient_id_mapping as pat_id
from dicom_anonymiseur.anonymization import anonymize_dataset
from dicom_anonymiseur.util import hash_value


def anonymize_single_DICOM(dicom_file_path: str, anonymized_directory: str, new_patient_id: str = 'patient',
                           random_str: str = "", anonymized_study_folder: str = "study",
                           anonymized_series_folder: str = "series", anonymized_instance_number: int = 0) -> None:
    """
    This method uses dicom_anonymiseur anonymization method. Simply said, it removes and replace all
    tags included in the Attribute Confidentiality Profile (DICOM PS 3.15: Appendix E). In UID's cases,
    the anonymization method replaces the old UID by a grpm UID. This method will also verify if the new patient
    id corresponds to the mapped patient Id inside the DICOM.

    :param anonymized_study_folder: desired name for the study folder name
    :param anonymized_instance_number: desired instance number
    :param anonymized_series_folder: desired name for the series folder name
    :param dicom_file_path: path and name of the dicom file to anonymize.
    :param anonymized_directory: directory where anonymized DICOMs will be sent.
    :param new_patient_id: New patient Id for the anonymized DICOMs (it will also be the name of the patient folder)
    :param random_str: string that will be added to the real UIDs in order to generate untraceable new UIDs
    """

    loaded_dicom = pydicom.dcmread(dicom_file_path)
    patient_id = loaded_dicom.PatientID
    if pat_id.is_patient_id_mapped(patient_id)[0]:
        new_patient_id = pat_id.get_patient_id_conversion(patient_id)
        logging.warning(f"New patient ID changed to {new_patient_id} for {patient_id} because the patient ID was "
                        f"already mapped")

    if pat_id.is_patient_id_mapped(new_patient_id)[0]:
        assert pat_id.does_the_specific_mapping_already_exist(new_patient_id, patient_id)

    instance_uid = loaded_dicom.SOPInstanceUID
    logging.info(f"Anonymizing instance {instance_uid} of patient {patient_id}")
    loaded_dicom.remove_private_tags()
    anonymized_dicom = anonymize_dataset(loaded_dicom, random_str)
    anonymized_dicom.PatientID = new_patient_id
    pat_id.map_new_patient_id_with_old_one(new_patient_id, patient_id)

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
    This method simply iterates on all the DICOMS contained in the series folder.

    :param anonymized_study_folder: desired name for the study folder name
    :param anonymized_series_folder: desired name for the series folder name
    :param series_folder: path to the target series folder
    :param anonymized_directory: directory where anonymized DICOMs will be sent.
    :param new_patient_id: New patient Id for the anonymized DICOMs (it will also be the name of the patient folder)
    :param random_str: string that will be added to the real UIDs in order to generate untraceable new UID
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
    This method simply iterates on all series folder contained in the study

    :param anonymized_study_folder: desired name for the study folder name
    :param study_folder: path to the target study folder
    :param anonymized_directory: directory where anonymized DICOMs will be sent.
    :param new_patient_id: New patient Id for the anonymized DICOMs (it will also be the name of the patient folder)
    :param random_str: string that will be added to the real UIDs in order to generate untraceable new UID
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
    This method simply iterates on all the study folder contained in the patient folder

    :param patient_folder: path to the target study folder
    :param anonymized_directory: directory where anonymized DICOMs will be sent.
    :param new_patient_id: New patient Id for the anonymized DICOMs (it will also be the name of the patient folder)
    :param random_str: string that will be added to the real UIDs in order to generate untraceable new UID
    """
    i = 0
    for folders in os.listdir(patient_folder):
        study_folder = os.path.join(patient_folder, folders)
        anonymize_whole_study(study_folder, anonymized_directory, new_patient_id, random_str, f"study{i}")
        i += 1
