import pydicom
from dicom_rt_context_extractor.storage_objects.rt_plan_storage_classes import LDRBrachyPlan
from clean_output_data.generate_rt_dose_from_egs_brachy_result import genetate_rt_dose_from_egs_brachy_result
from clean_output_data.generate_rt_dose_from_egs_brachy_std import genetate_rt_dose_from_egs_brachy_std


def clean_egs_brachy_output(path_to_3ddose, path_to_original_rt_dose, rt_plan_path,
                            rt_plan: LDRBrachyPlan, rt_dose_saving_path, rt_dose_error_saving_path,
                            updated_rt_plan_saving_path, dose_comment="", std_comments="", software="",
                            series_description="", position=None):
    genetate_rt_dose_from_egs_brachy_result(path_to_3ddose, path_to_original_rt_dose, rt_plan_path, rt_plan,
                                            rt_dose_saving_path, updated_rt_plan_saving_path, dose_comment,
                                            software, position)
    genetate_rt_dose_from_egs_brachy_std(path_to_3ddose, path_to_original_rt_dose, updated_rt_plan_saving_path, rt_plan,
                                         rt_dose_error_saving_path, updated_rt_plan_saving_path, std_comments,
                                         software, position)
    dose = pydicom.dcmread(rt_dose_saving_path)
    std = pydicom.dcmread(rt_dose_error_saving_path)
    dose.SeriesDescription = series_description
    std.SeriesDescription = series_description
    std.SeriesInstanceUID = dose.SeriesInstanceUID
    std.SeriesNumber = dose.SeriesNumber
    std.InstanceNumber = dose.InstanceNumber + 1

    dose.save_as(rt_dose_saving_path)
    std.save_as(rt_dose_error_saving_path)
