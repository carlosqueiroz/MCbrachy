import json
import os
import pydicom
import logging
from typing import List
from itertools import chain
from root import ROOT

contour_vocab_path = os.path.join(ROOT, "preprocessing_pipeline_components", "contour_vocabulary.json")


def verify_if_all_required_contours_are_present(path_to_dicom: str, desired_rois: List[str],
                                                disable_vocabulary_update: bool = False) -> bool:
    """

    :param disable_vocabulary_update:
    :param path_to_dicom:
    :param desired_rois:
    :return:
    """
    open_dicom = pydicom.dcmread(path_to_dicom)
    patient_id = open_dicom.PatientID
    instance_uid = open_dicom.SOPInstanceUID
    contour_vocabulary_file = open(contour_vocab_path, "r")
    contour_vocabulary = json.loads(contour_vocabulary_file.read())
    contour_vocabulary_file.close()

    try:
        if open_dicom.Modality == "RTSTRUCT":
            json_version_dicom = open_dicom.to_json_dict()
            structure_set_roi_sequence = json_version_dicom["30060020"]["Value"]

            for roi in structure_set_roi_sequence:
                roi_name = roi["30060026"]["Value"][0]
                for desired_roi in desired_rois:
                    if roi_name in contour_vocabulary[desired_roi]:
                        desired_rois.remove(desired_roi)
                        break

                    # if roi_name not in vocab, it calls add_expression_to_contour_vocab, refreshes vocab
                    if (roi_name not in chain(*contour_vocabulary.values())) and not disable_vocabulary_update:
                        add_expression_to_contour_vocab(roi_name, contour_vocabulary)
                        contour_vocabulary_file = open(contour_vocab_path, "r")
                        contour_vocabulary = json.loads(contour_vocabulary_file.read())
                        contour_vocabulary_file.close()
                        # and retries looking in the updated vocab
                        for desired_roi_retry in desired_rois:
                            if roi_name in contour_vocabulary[desired_roi_retry]:
                                desired_rois.remove(desired_roi_retry)
                                break

            if len(desired_rois) == 0:
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


def get_input(text):
    return input(text)


def add_expression_to_contour_vocab(dicom_contour: str, contour_vocabulary: dict) -> None:
    """
    Because many words or expression can be used to describe the same structure,
    a dictionary has been created to keep track of the many expressions associated with the same concept.
    (eg. prostate, Prostate, The prostate, etc). This method simply add a new expression in a certain category.
    A category represents a single structure.

    :param dicom_contour: contour found in the dicom that is not in the vocabulary
    :param contour_vocabulary: dict of all the vocabulary
    """
    associated_contour = get_input(f"In which contour site category does {dicom_contour}"
                                        f"go into? (existing categories: {contour_vocabulary.keys()}):")
    if associated_contour in contour_vocabulary.keys():
        contour_vocabulary[associated_contour].append(dicom_contour)

    else:
        is_answer_not_valid = True
        while is_answer_not_valid:
            print(f'Do you really want to create a new category named {associated_contour}')
            answer = get_input("(Yes or No):")
            if answer == "Yes" or answer == "No":
                is_answer_not_valid = False

            if answer == "Yes":
                contour_vocabulary[associated_contour] = [dicom_contour]

            else:
                logging.warning(f"The category has not been created, moving on.")
    vocab_file = open(contour_vocab_path, "w")
    json.dump(contour_vocabulary, vocab_file)
    vocab_file.close()
