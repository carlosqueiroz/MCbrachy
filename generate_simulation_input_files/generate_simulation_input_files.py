import logging
from dicom_rt_context_extractor.storage_objects.rt_plan_storage_classes import LDRBrachyPlan
from generate_simulation_input_files.generate_geometry import generate_topas_input_string_and_3d_mapping
from generate_simulation_input_files.generate_scorer import generate_topas_scorer
from generate_simulation_input_files.generate_treatment_plan import generate_topas_seed_string


def generate_whole_topas_input_file(plan: LDRBrachyPlan, total_particles: int, list_of_desired_structures, output_path,
                                    path_to_save_input_file,
                                    path_to_save_index, output_type, add=""):
    total_seeds = 0
    for sources in plan.list_of_sources:
        total_seeds += len(sources.positions)

    photon_per_seed = int(total_particles / total_seeds)
    if plan.dosi_is_built and plan.structures_are_built:
        full_input_file = generate_topas_seed_string(plan, photon_per_seed) + "\n\n"
        full_input_file += generate_topas_input_string_and_3d_mapping(plan.structures,
                                                                      list_of_desired_structures,
                                                                      path_to_save_index) + "\n\n"
        full_input_file += generate_topas_scorer(plan.dosimetry, output_path, output_type) + "\n\n" + add

        text_file = open(path_to_save_input_file, "w")
        text_file.write(full_input_file)
        text_file.close()

    else:
        logging.warning("Dosimetry or Structures not built")
