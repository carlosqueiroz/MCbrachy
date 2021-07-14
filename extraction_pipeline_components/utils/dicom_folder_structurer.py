import os
import shutil

import pydicom


def restructure_dicom_folder(path_containing_all_dicoms: str, path_to_the_new_patient_folder: str) -> None:
    """

    :param path_containing_all_dicoms:
    :param path_to_the_new_patient_folder:
    :return:
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
