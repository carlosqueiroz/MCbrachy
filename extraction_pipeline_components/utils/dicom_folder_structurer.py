import os
import shutil

import pydicom


def restructure_dicom_folder(path_containing_all_dicoms: str, path_to_the_new_patient_folder: str) -> None:
    """
    This method takes a folder containing all DICOMs related to a single patient and restructure it in order
    to follow the patient-study-series-instance hierarchy. In other words patient folder will contain study folders
    that will have series folders inside. Finally, the series will contain the DICOM files representing the instances.

    :param path_containing_all_dicoms:
    :param path_to_the_new_patient_folder:
    """
    study_dict = {}
    series_dict = {}

    it_study = 1
    it_series = 1
    for files in os.listdir(path_containing_all_dicoms):
        file_path = os.path.join(path_containing_all_dicoms, files)
        dicom = pydicom.dcmread(file_path)
        study_uid = str(dicom.StudyInstanceUID)
        series_uid = str(dicom.SeriesInstanceUID)

        if study_uid not in study_dict.keys():
            study_dict[study_uid] = it_study
            os.makedirs(os.path.join(path_to_the_new_patient_folder, f"study{study_dict[study_uid]}"))
            it_study += 1

        if series_uid not in series_dict.keys():
            series_dict[series_uid] = it_series
            os.makedirs(os.path.join(path_to_the_new_patient_folder, f"study{study_dict[study_uid]}",
                                     f"series{series_dict[series_uid]}"))
            it_series += 1

        shutil.move(file_path, os.path.join(path_to_the_new_patient_folder, f"study{study_dict[study_uid]}",
                                            f"series{series_dict[series_uid]}"))


def destructure_folder(path_of_the_patient_folder: str) -> None:
    """
    This method takes a patient folder structured to follow the patient-study-series-instance hierarchy and places
    all instances at the higher level. This method does exactly the opposite of restructure_dicom_folder.

    :param path_of_the_patient_folder:
    """
    for study_folder in os.listdir(path_of_the_patient_folder):
        study_folder_path = os.path.join(path_of_the_patient_folder, study_folder)
        for series_folder in os.listdir(study_folder_path):
            series_folder_path = os.path.join(study_folder_path, series_folder)
            for dicoms in os.listdir(series_folder_path):
                dicom_path = os.path.join(series_folder_path, dicoms)
                shutil.move(dicom_path, path_of_the_patient_folder)
            if len(os.listdir(series_folder_path)) != 0:
                raise ValueError
            shutil.rmtree(series_folder_path)  # If so, delete it

        if len(os.listdir(study_folder_path)) != 0:
            raise ValueError
        shutil.rmtree(study_folder_path)
