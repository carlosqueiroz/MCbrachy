import numpy as np
import pydicom
from py3ddose.py3ddose import DoseFile
from dicom_rt_context_extractor.storage_objects.rt_plan_storage_classes import LDRBrachyPlan
from mcdose2dicom import create_rt_dose_from_scratch
from mcdose2dicom.adapt_rt_dose_to_existing_dicoms import adapt_rt_dose_to_existing_rt_dose_grid, \
    add_reference_in_rt_plan
from clean_output_data.calculate_dose_convertion_factor_egs import \
    calculate_total_dose_conversion_factor_with_know_caracteristics


def genetate_rt_dose_from_egs_brachy_result(path_to_3ddose, path_to_original_rt_dose, rt_plan_path,
                                            rt_plan: LDRBrachyPlan, rt_dose_saving_path, updated_rt_plan_saving_path,
                                            dose_comment="", software="", position=None):
    if position is None:
        position = [0, 0, 0]
    manufacturer = rt_plan.list_of_sources[0].source_manufacturer
    isotope = rt_plan.list_of_sources[0].source_isotope_name
    air_kerma_rate = rt_plan.list_of_sources[0].air_kerma_rate
    half_life = rt_plan.list_of_sources[0].half_life
    if manufacturer == "Nucletron B.V." and isotope == "I-125":
        seed_model = "SelectSeed"
    else:
        raise NotImplementedError

    egs_output = DoseFile(path_to_3ddose)
    pixel_data = np.flip(egs_output.dose, axis=0)
    scaling_factor = calculate_total_dose_conversion_factor_with_know_caracteristics(seed_model,
                                                                                     air_kerma_rate,
                                                                                     half_life * 24)
    voxel_size = (10 * egs_output.spacing[2][0], 10 * egs_output.spacing[1][0], 10 * egs_output.spacing[0][0])
    dose_comment += f" Factor from dose/histories to total dose = {scaling_factor}"
    rt_dose = create_rt_dose_from_scratch.RTDoseBuilder(dose_grid_scaling=scaling_factor,
                                                        dose_type="PHYSICAL", dose_comment=dose_comment,
                                                        software=software, dose_units="GY")
    rt_dose.add_dose_grid(pixel_data, voxel_size, True, True)
    rt_dose.build()
    rt_dose.save_rt_dose_to(rt_dose_saving_path)

    adapt_rt_dose_to_existing_rt_dose_grid(rt_dose_saving_path, path_to_original_rt_dose)
    add_reference_in_rt_plan(rt_plan_path, rt_dose_saving_path, updated_rt_plan_saving_path)
    rt_dose = pydicom.dcmread(rt_dose_saving_path)
    rt_dose.ImagePositionPatient = f'{position[2]}\\{position[1]}\\{position[0]}'
    rt_dose.save_as(rt_dose_saving_path)