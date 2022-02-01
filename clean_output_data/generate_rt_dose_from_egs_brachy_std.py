import numpy as np
from py3ddose.py3ddose import DoseFile
from dicom_rt_context_extractor.storage_objects.rt_plan_storage_classes import LDRBrachyPlan
from mcdose2dicom import create_rt_dose_from_scratch
from mcdose2dicom.adapt_rt_dose_to_existing_dicoms import adapt_rt_dose_to_existing_rt_dose_grid, \
    add_reference_in_rt_plan
from clean_output_data.calculate_dose_convertion_factor import \
    calculate_total_dose_error_conversion_factor_with_know_caracteristics


def genetate_rt_dose_from_egs_brachy_std(path_to_3ddose, path_to_original_rt_dose, rt_plan_path,
                                    rt_plan: LDRBrachyPlan, rt_dose_saving_path, updated_rt_plan_saving_path,
                                    dose_comment="", software=""):
    manufacturer = rt_plan.list_of_sources[0].source_manufacturer
    isotope = rt_plan.list_of_sources[0].source_isotope_name
    half_life = rt_plan.list_of_sources[0].half_life
    if manufacturer == "Nucletron B.V." and isotope == "I-125":
        seed_model = "SelectSeed"
    else:
        raise NotImplementedError

    egs_output = DoseFile(path_to_3ddose)
    pixel_data = np.flip(egs_output.uncertainty, axis=0)
    scaling_factor = calculate_total_dose_error_conversion_factor_with_know_caracteristics(seed_model, half_life * 24)
    voxel_size = (egs_output.spacing[0][0], egs_output.spacing[1][0], egs_output.spacing[2][0])

    dose_comment += f" Error on factor from dose/histories to total dose = {scaling_factor}"
    rt_dose = create_rt_dose_from_scratch.RTDoseBuilder(dose_type="ERROR", dose_comment=dose_comment,
                                                        software=software, dose_units="GY")
    rt_dose.add_dose_grid(pixel_data, voxel_size, False)
    rt_dose.build()
    rt_dose.save_rt_dose_to(rt_dose_saving_path)

    adapt_rt_dose_to_existing_rt_dose_grid(rt_dose_saving_path, path_to_original_rt_dose)
    add_reference_in_rt_plan(rt_plan_path, rt_dose_saving_path, updated_rt_plan_saving_path)
