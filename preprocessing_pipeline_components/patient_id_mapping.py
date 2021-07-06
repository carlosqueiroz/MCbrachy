import csv
import os
import logging

from typing import Tuple

from root import ROOT

patient_id_mapping_file_path = os.path.join(ROOT, "preprocessing_pipeline_components", "storing_files",
                                            "patientID_mapping.csv")


def map_new_patient_id_with_old_one(new_patient_id: str, old_patient_id: str) -> None:
    """
    This method will simply add a new entry to the mapping csv file.
    This will only be done if the mapping does not already exist or
    does not contradict any other mapping.

    :param new_patient_id: New patient ID
    :param old_patient_id: associated old patient Id
    """
    mapped_new, row_new = is_patient_id_mapped(new_patient_id)
    mapped_old, row_old = is_patient_id_mapped(old_patient_id)
    if (not mapped_old) and (not mapped_new):
        csv_exists = os.path.exists(patient_id_mapping_file_path)
        with open(patient_id_mapping_file_path, 'a', newline="") as csv_file:
            mapping_writer = csv.writer(csv_file, delimiter=";")
            if not csv_exists:
                mapping_writer.writerow(["Original PatientID", "New PatientID"])
            mapping_writer.writerow([old_patient_id, new_patient_id])

    else:
        logging.warning(f"One or both {new_patient_id} and {old_patient_id} are already mapped")


def does_the_specific_mapping_already_exist(new_patient_id: str, old_patient_id: str) -> bool:
    """
    This method verifies if the specific pair already exist within the csv file.

    :param new_patient_id: new patient ID
    :param old_patient_id: associated old ID

    :return: Whether or not the exact pair already exist
    """
    mapped_new, row_new = is_patient_id_mapped(new_patient_id)
    mapped_old, row_old = is_patient_id_mapped(old_patient_id)
    if mapped_old and mapped_new:
        if row_old == row_new:
            return True

        logging.info(f"Both {new_patient_id} and {old_patient_id} are mapped, but not together")
        return False

    logging.info(f"One or both {new_patient_id} and {old_patient_id} are not mapped")
    return False


def get_patient_id_conversion(old_or_new_patient_id: str) -> str or None:
    """
    This method will first verify if the given Id is already
    mapped. If it is, it will simply return the associated Id.
    In a new Id's case, the method will return the associatede
    old one.

    :param old_or_new_patient_id: id to search for
    :return: the associated Id or None
    """
    mapped, row = is_patient_id_mapped(old_or_new_patient_id)
    if mapped:
        with open(patient_id_mapping_file_path) as csv_file:
            csv_reader_list = list(csv.reader(csv_file, delimiter=";"))
            if old_or_new_patient_id == csv_reader_list[row][0]:
                return csv_reader_list[row][1]

            if old_or_new_patient_id == csv_reader_list[row][1]:
                return csv_reader_list[row][0]

            logging.warning(f"Something went wrong while returning the associated PatientId for "
                            f"{old_or_new_patient_id}")
            return None

    logging.warning(f"{old_or_new_patient_id} not in the mapping table")
    return None


def is_patient_id_mapped(old_or_new_patient_id: str) -> Tuple[bool, int]:
    """
    This method verifies whether or not the old or new id given is
    already mapped in the csv file.

    :param old_or_new_patient_id: id to search for
    :return: if found and at which row it is found
    """
    try:
        with open(patient_id_mapping_file_path) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=";")
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    assert row[0] == "Original PatientID"
                    assert row[1] == "New PatientID"
                    line_count += 1
                else:
                    if row[0] == old_or_new_patient_id:
                        logging.info(f"Original PatientID: {old_or_new_patient_id} found at row {line_count}")
                        return True, line_count

                    if row[1] == old_or_new_patient_id:
                        logging.info(f"New PatientID: {old_or_new_patient_id} found at row {line_count}")
                        return True, line_count

                    line_count += 1

            return False, -1

    except (AssertionError, FileNotFoundError):
        logging.warning(f"Error occurred while searching for {old_or_new_patient_id}")
        return False, -1
