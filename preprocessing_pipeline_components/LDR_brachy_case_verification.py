import os
import pydicom
import logging
import json
from root import ROOT
from itertools import chain

source_verification = {"LDR": ["I-125", "Pd-103", "Cs-131"], "HDR": ["Ir-192"]}

vocab_path = os.path.join(ROOT, "preprocessing_pipeline_components", "treatment_site_vocabulary.json")


def verify_if_brachy_treatment_type(path_to_dicom: str, treatment_type: str = "LDR") -> bool:
    """
    This method verifies if the brachytherapy treatment tag
    of the DICOM RT PLAN corresponds to the desired treatment
    type (eg. LDR, HDR, MDR). In any unexpected cases, this method
    will simply return False.

    :param path_to_dicom: path to the DICOM RT PLAN file
    :param treatment_type: HDR, LDR, MDR or PDR
    :return: Whether or not the RT PLAN treatment plan fits the desired treatment plan
    """

    open_dicom = pydicom.dcmread(path_to_dicom)
    patient_id = open_dicom.PatientID
    instance_uid = open_dicom.SOPInstanceUID
    try:
        if open_dicom.Modality == "RTPLAN":
            json_version_dicom = open_dicom.to_json_dict()
            brachy_treatment_type = json_version_dicom["300A0202"]["Value"][0]
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


def verify_if_source_corresponds_to_treatment_type(path_to_dicom: str, treatment_type: str = "LDR"):
    """
    This method verifies if all listed sources in the DICOM RT PLAN correspond to
    the sources used in the desired treatment type. If at least one source doesn't fit what is expected,
    this method will return False. In any unexpected cases, this method
    will simply return False.

    :param path_to_dicom: path to the DICOM RT PLAN file
    :param treatment_type: HDR, LDR, MDR or PDR
    :return: Whether or not all the RT PLAN sources fit the desired treatment plan
    """
    open_dicom = pydicom.dcmread(path_to_dicom)
    patient_id = open_dicom.PatientID
    instance_uid = open_dicom.SOPInstanceUID
    try:
        if open_dicom.Modality == "RTPLAN":
            json_version_dicom = open_dicom.to_json_dict()
            source_sequence = json_version_dicom["300A0210"]["Value"]
            for sources in source_sequence:
                if sources["300A0226"]["Value"][0] not in source_verification[treatment_type]:
                    return False

            return True

        logging.warning(f"Instance {instance_uid} of patient {patient_id} is not a RTPLAN as expected."
                        f"\n The verification of brachy treatment plan automatically returned false")
        return False

    except KeyError:
        logging.warning(f"Something went wrong while searching for brachy treatment relative information for instance"
                        f" {instance_uid} of patient {patient_id}."
                        f"\n The verification of brachy treatment plan automatically returned false")
        return False


def verify_treatment_site(path_to_dicom: str, treatment_site: str, disable_vocabulary_update: bool = False) -> bool:
    """
    This method verifies if the treatement site in the DICOM RT PLAN is in the vocabulary list of desired treatment site.
    If it is not and disable_vocabulary_update is Fasle, the user will be asked if he wants to add the new encountered
    expression in one of the vocab category.

    :param path_to_dicom: path to the DICOM RT PLAN file
    :param treatment_site: treatment site string corresponding to one of the vocabulary keys
    :param disable_vocabulary_update: disable the addition of new encountered values in dictionary
    :return: Whether or not the treatment site in DICOM corresponds to desired treatment site
    """
    open_dicom = pydicom.dcmread(path_to_dicom)
    patient_id = open_dicom.PatientID
    instance_uid = open_dicom.SOPInstanceUID
    try:
        treatment_site_vocabulary_file = open(vocab_path, "r")
        treatment_site_vocabulary = json.loads(treatment_site_vocabulary_file.read())
        treatment_site_vocabulary_file.close()
        if open_dicom.Modality == "RTPLAN":
            json_version_dicom = open_dicom.to_json_dict()
            dicom_treatment_site = json_version_dicom["300A000B"]["Value"][0]
            if dicom_treatment_site in treatment_site_vocabulary[treatment_site]:
                return True

            if (dicom_treatment_site not in chain(*treatment_site_vocabulary.values())) and not disable_vocabulary_update:
                add_expression_to_vocab(dicom_treatment_site, treatment_site_vocabulary)
                treatment_site_vocabulary_file = open(vocab_path, "r")
                treatment_site_vocabulary = json.loads(treatment_site_vocabulary_file.read())
                treatment_site_vocabulary_file.close()

                if dicom_treatment_site in treatment_site_vocabulary[treatment_site]:
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


def get_input(text):
    return input(text)


def add_expression_to_vocab(dicom_treatment_site: str, treatment_site_vocabulary: dict) -> None:
    """
    Because many words or expression can be used to describe the same structure,
    a dictionary has been created to keep track of the many expressions associated with the same concept.
    (eg. prostate, Prostate, The prostate, etc). This method simply add a new expression in a certain category.
    A category represents a single structure.

    :param dicom_treatment_site: treatment site found in the dicom that is not in the vocabulary
    :param treatment_site_vocabulary: dict of all the vocabulary
    """
    associated_treatment_site = get_input(f"In which treatment site category does {dicom_treatment_site}"
                                          f"go into? (existing categories: {treatment_site_vocabulary.keys()}):")
    if associated_treatment_site in treatment_site_vocabulary.keys():
        treatment_site_vocabulary[associated_treatment_site].append(dicom_treatment_site)

    else:
        is_answer_not_valid = True
        while is_answer_not_valid:
            print(f'Do you really want to create a new category named {associated_treatment_site}')
            answer = get_input("(Yes or No):")
            if answer == "Yes" or answer == "No":
                is_answer_not_valid = False

            if answer == "Yes":
                treatment_site_vocabulary[associated_treatment_site] = [dicom_treatment_site]

            else:
                logging.warning(f"The category has not been created, moving on.")
    vocab_file = open(vocab_path, "w")
    json.dump(treatment_site_vocabulary, vocab_file)
    vocab_file.close()

