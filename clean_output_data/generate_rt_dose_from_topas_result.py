import numpy as np
from topas2numpy.binned import BinnedResult
from dicom_rt_context_extractor.storage_objects.rt_plan_storage_classes import LDRBrachyPlan
from mcdose2dicom import create_rt_dose_from_scratch
from mcdose2dicom.adapt_rt_dose_to_existing_dicoms import adapt_rt_dose_to_existing_rt_dose_grid,\
    add_reference_in_rt_plan
from clean_output_data.calculate_dose_convertion_factor_topas import \
    calculate_total_dose_conversion_factor_with_know_caracteristics


def genetate_rt_dose_from_topas_result(path_to_bin_file, path_to_original_rt_dose, rt_plan_path,
                                       rt_plan: LDRBrachyPlan, rt_dose_saving_path, updated_rt_plan_saving_path,
                                       dose_comment="", software=""):
    manufacturer = rt_plan.list_of_sources[0].source_manufacturer
    isotope = rt_plan.list_of_sources[0].source_isotope_name
    air_kerma_rate = rt_plan.list_of_sources[0].air_kerma_rate
    half_life = rt_plan.list_of_sources[0].half_life
    if manufacturer == "Nucletron B.V." and isotope == "I-125":
        seed_model = "SelectSeed"
    else:
        raise NotImplementedError

    topas_output = BinnedResult(path_to_bin_file)
    pixel_data = np.flip(topas_output.data["Sum"], axis=0)
    scaling_factor = calculate_total_dose_conversion_factor_with_know_caracteristics(seed_model,
                                                                                     air_kerma_rate,
                                                                                     half_life * 24)
    scaling_factor = scaling_factor / float(rt_plan.list_of_sources[0].positions.shape[0])
    voxel_size = (topas_output.dimensions[0].bin_width * 10, topas_output.dimensions[1].bin_width * 10,
                  topas_output.dimensions[2].bin_width * 10)

    dose_comment += f" Factor from dose/histories to total dose = {scaling_factor}"
    rt_dose = create_rt_dose_from_scratch.RTDoseBuilder(dose_grid_scaling=scaling_factor,
                                                        dose_type="PHYSICAL", dose_comment=dose_comment,
                                                        software=software, dose_units="GY")
    rt_dose.add_dose_grid(pixel_data, voxel_size, False, True)
    rt_dose.build()
    rt_dose.save_rt_dose_to(rt_dose_saving_path)

    adapt_rt_dose_to_existing_rt_dose_grid(rt_dose_saving_path, path_to_original_rt_dose)
    add_reference_in_rt_plan(rt_plan_path, rt_dose_saving_path, updated_rt_plan_saving_path)



