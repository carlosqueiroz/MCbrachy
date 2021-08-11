import os
import pydicom
import logging
from preprocessing_pipeline_components import contour_verification, anonymization, calcification_verification,\
    data_tracker, LDR_brachy_case_verification
from extraction_pipeline_components.utils.dicom_folder_structurer import restructure_dicom_folder, destructure_folder

logging.basicConfig(format='%(asctime)s [%(levelname)s, %(module)s.%(funcName)s]: %(message)s',
                    level=logging.INFO)

DICOM_PATH = r"D:\ARCHIVES_OCP"
random_str = ""
ANONYMIZED_SELECTED_DATA = ""
ANONYMIZED_SELECTED_DATA_WITH_CALCIFICATION = r"C:\Users\Admin\Desktop\Anonymized_patient"


total_count = 0
for patient_folder in os.listdir(DICOM_PATH):
    LDR_post = False
    patient_folder_path = os.path.join(DICOM_PATH, patient_folder)
    if os.listdir(patient_folder_path)[0].startswith("CT"):
        LDR_post = True

    if not LDR_post:
        continue
    print(patient_folder)
    restructure_dicom_folder(patient_folder_path, patient_folder_path)
    for study_folder in os.listdir(patient_folder_path):
        study_folder_path = os.path.join(patient_folder_path, study_folder)
        post_implant = False
        for series_folder in os.listdir(study_folder_path):
            series_folder_path = os.path.join(study_folder_path, series_folder)
            dicoms_path = os.listdir(series_folder_path)[0]
            if dicoms_path.startswith("CT"):
                post_implant = True

        if not post_implant:
            continue
        stop_looking_in_study = False
        rt_plan_ok = False
        rt_struct_ok = False
        for series_folder in os.listdir(study_folder_path):
            series_folder_path = os.path.join(study_folder_path, series_folder)
            dicoms_path = os.path.join(series_folder_path, os.listdir(series_folder_path)[0])
            if data_tracker.dicom_has_already_been_looked_into(dicoms_path, random_str):
                continue
            open_dicom = pydicom.dcmread(dicoms_path)
            if open_dicom.Modality == "RTPLAN" and not rt_plan_ok:  # verify if  not rt_plan_ok good choice
                data_tracker.add_instance_uid_to_anonymized_uids_met(dicoms_path, random_str,  with_anonymization=True) # set to true
                if not LDR_brachy_case_verification.verify_if_brachy_treatment_type(dicoms_path, "LDR"):
                    stop_looking_in_study = True
                    break
                if not LDR_brachy_case_verification.verify_treatment_site(dicoms_path, "prostate"):
                    stop_looking_in_study = True
                    break

                rt_plan_ok = True

            if open_dicom.Modality == "RTSTRUCT" and not rt_struct_ok:  # verify if  not rt_plan_ok good choice
                data_tracker.add_instance_uid_to_anonymized_uids_met(dicoms_path, random_str,  with_anonymization=True) # set to true
                if not contour_verification.verify_if_all_required_contours_are_present(dicoms_path, ["vessie", "prostate", "rectum", "uretre", "Bladder Neck"]):
                    stop_looking_in_study = True
                    break

                rt_struct_ok = True

            if rt_plan_ok and rt_struct_ok:
                break

        if stop_looking_in_study:
            continue

        if rt_plan_ok and rt_struct_ok:
            if calcification_verification.is_there_prostate_calcification_in_study(study_folder_path):
                anonymization.anonymize_whole_study(study_folder_path, ANONYMIZED_SELECTED_DATA_WITH_CALCIFICATION,
                                                    f'patient{total_count}')
                total_count += 1

    destructure_folder(patient_folder_path)

print(total_count)







