import os
import pydicom
import logging
import json
from dicom_anonymiseur.anonymization import anonymize_dataset
from root import ROOT

anonymized_uids_met_path = os.path.join(ROOT, "preprocessing_pipeline_components", "anonymized_uids_met.json")


def dicom_has_already_been_looked_into(dicom_file_path: str, random_str_used_in_anonymization: str == "") -> bool:
    """

    :param dicom_file_path:
    :param random_str_used_in_anonymization:
    :return:
    """
    loaded_dicom = pydicom.dcmread(dicom_file_path)
    instance_uid = loaded_dicom.SOPInstanceUID
    anonymized_uids_met_file = open(anonymized_uids_met_path, "r")
    anonymized_uids_met_list = json.loads(anonymized_uids_met_file.read())
    anonymized_uids_met_file.close()
    if instance_uid in anonymized_uids_met_list:
        logging.warning(f"DICOM with UID: {instance_uid} has already been anonymized. Pls do not anonymize it again"
                        f"to avoid duplicates")
        return True

    anonymized_dicom = anonymize_dataset(loaded_dicom, random_str_used_in_anonymization)
    if anonymized_dicom.SOPInstanceUID in anonymized_uids_met_list:
        return True

    return False


def add_instance_uid_to_anonymized_uids_met(dicom_file_path: str, random_str: str = "",
                                            with_anonymization: bool = True) -> None:
    """

    :param dicom_file_path:
    :param random_str:
    :param with_anonymization:
    :return:
    """

    loaded_dicom = pydicom.dcmread(dicom_file_path)
    instance_uid = loaded_dicom.SOPInstanceUID
    if dicom_has_already_been_looked_into(dicom_file_path, random_str):
        logging.warning(f"DICOM with UID: {instance_uid} already added to anonymized_uids_met. Please ensure there"
                        f"are no duplicates")

    else:
        if with_anonymization:
            anonymize_dicom = anonymize_dataset(loaded_dicom, random_str)
            instance_uid = anonymize_dicom.SOPInstanceUID
        anonymized_uids_met_file = open(anonymized_uids_met_path, "r")
        anonymized_uids_met_list = json.loads(anonymized_uids_met_file.read())
        anonymized_uids_met_file.close()
        anonymized_uids_met_list.append(instance_uid)
        anonymized_uids_met_file = open(anonymized_uids_met_path, "w")
        json.dump(anonymized_uids_met_list, anonymized_uids_met_file)
        anonymized_uids_met_file.close()


