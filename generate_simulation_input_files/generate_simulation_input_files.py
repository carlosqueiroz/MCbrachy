import logging

from egs_brachy_file_generator.LDR_brachy import LDR_physics
from generate_simulation_input_files.generate_geometry import generate_topas_input_string_and_3d_mapping
from dicom_rt_context_extractor.storage_objects.rt_plan_storage_classes import LDRBrachyPlan
from generate_simulation_input_files.generate_scorer import generate_topas_scorer
from generate_simulation_input_files.generate_treatment_plan import generate_topas_seed_string
from generate_simulation_input_files.generate_treatment_plan import generate_egs_brachy_source_definition
from generate_simulation_input_files.generate_geometry import generate_egs_brachy_geo_string_and_phant
from egs_brachy_file_generator.run_context import EGS_BRACHY_RUN_CONTEXT
from generate_simulation_input_files.generate_scorer import generate_egs_brachy_scorer


def generate_whole_topas_input_file(plan: LDRBrachyPlan, total_particles: int, list_of_desired_structures, output_path,
                                    path_to_save_input_file,
                                    path_to_save_index, output_type, add=""):
    total_seeds = 0
    for sources in plan.list_of_sources:
        total_seeds += len(sources.positions)

    photon_per_seed = int(total_particles / total_seeds)
    if plan.dosi_is_built and plan.structures_are_built:
        voxel_size_z, voxel_size_y, voxel_size_x = plan.structures.z_y_x_spacing
        origin = plan.structures.x_y_z_origin
        nb_z, nb_y, nb_x = plan.structures.image_shape
        transx = origin[0] + (nb_x * voxel_size_x - voxel_size_x) / 2
        transy = origin[1] + (nb_y * voxel_size_y - voxel_size_y) / 2
        transz = origin[2] - (nb_z * voxel_size_z - voxel_size_z) / 2

        full_input_file = generate_topas_seed_string(plan, photon_per_seed, (transx, transy, transz)) + "\n\n"
        full_input_file += generate_topas_input_string_and_3d_mapping(plan.structures,
                                                                      list_of_desired_structures,
                                                                      path_to_save_index) + "\n\n"
        full_input_file += generate_topas_scorer(plan.dosimetry, output_path, output_type) + "\n\n" + add

        text_file = open(path_to_save_input_file, "w")
        text_file.write(full_input_file)
        text_file.close()

    else:
        logging.warning("Dosimetry or Structures not built")


def generate_whole_egs_brachy_input_file(plan: LDRBrachyPlan, total_particles: int, list_of_desired_structures,
                                         path_to_transform_file, path_to_save_input_file,
                                         pah_to_egs_folder, egs_phant_file_path, batches=1, chunk=1, add="", crop=False):
    run_context = EGS_BRACHY_RUN_CONTEXT.substitute(nb_photon=total_particles, nb_batch=batches, nb_chunk=chunk,
                                                    egs_brachy_folder=pah_to_egs_folder, accuracy=1)
    sources = plan.list_of_sources[0]
    source_def, source_geo = generate_egs_brachy_source_definition(sources, path_to_transform_file, pah_to_egs_folder)
    geo_def, offsets = generate_egs_brachy_geo_string_and_phant(plan.structures, egs_phant_file_path, list_of_desired_structures,
                                                       source_geo, pah_to_egs_folder, crop=crop)
    physics = LDR_physics.EGS_BRACHY_LDR_PHYSICS.substitute(path_to_egs_folder=pah_to_egs_folder)
    scorer = generate_egs_brachy_scorer(list_of_desired_structures, pah_to_egs_folder)

    text_file = open(path_to_save_input_file, "w")
    text_file.write(run_context + geo_def + source_def + scorer + physics + add)
    text_file.close()

    return offsets
