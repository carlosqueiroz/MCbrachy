import numpy as np
from dicom_rt_context_extractor.storage_objects.rt_plan_storage_classes import Sources, LDRBrachyPlan
from topas_file_generator.LDR_brachy.seed_templates import iodine125_select_seed
from egs_brachy_file_generator.LDR_brachy.seed_templates import iodine125_select_seed


def generate_topas_seed_string(plan: LDRBrachyPlan, photon_per_seed: int, struct_center_coords):
    all_sources_string = ""
    for sources in plan.list_of_sources:
        all_sources_string = all_sources_string + generate_sources_topas_string(sources,
                                                                                photon_per_seed,
                                                                                struct_center_coords) + "\n\n"

    return all_sources_string


def generate_sources_topas_string(source: Sources, photon_per_seed, struct_center_coords):
    """

    :param struct_center_coords:
    :param source:
    :param photon_per_seed:
    :return:
    """
    if source.source_manufacturer == "Nucletron B.V." and source.source_isotope_name == "I-125":
        sources_topas_string = iodine125_select_seed.HEADER + "\n\n" + iodine125_select_seed.MATERIALS
        for index in range(source.positions.shape[0]):
            sources_topas_string += "\n\n" + iodine125_select_seed.SEEDS.substitute(index=index,
                                                                                    photon_per_seed=photon_per_seed,
                                                                                    position_x=source.positions[index][
                                                                                                   0] -
                                                                                               struct_center_coords[0],
                                                                                    position_y=source.positions[index][
                                                                                                   1] -
                                                                                               struct_center_coords[1],
                                                                                    position_z=source.positions[index][
                                                                                                   2] -
                                                                                               struct_center_coords[2])

        return sources_topas_string

    else:
        raise NotImplementedError


def generate_egs_brachy_source_definition(source: Sources, new_file_path: str, path_to_egs_folder):
    manufacturer = source.source_manufacturer
    isotope = source.source_isotope_name
    generate_transformation_file_for_sources(source, new_file_path)
    if manufacturer == "Nucletron B.V." and isotope == "I-125":
        source_def = iodine125_select_seed.EGS_BRACHY_SOURCE_DEF.substitute(path_to_egs_folder=path_to_egs_folder,
                                                                            transfomation_file_path=new_file_path)
        source_geo = iodine125_select_seed.EGS_BRACHY_SOURCE_GEO.substitute(path_to_egs_folder=path_to_egs_folder,
                                                                            transfomation_file_path=new_file_path)

    else:
        raise NotImplementedError

    return source_def, source_geo


def generate_transformation_file_for_sources(source: Sources, new_file_path: str) -> None:
    """
    This method generates egs_brachy transformation file from
    the sources positions.

    :param source:
    :param new_file_path:
    :return:
    """
    pos = source.positions / 10
    orientation = source.orientations
    if orientation.shape[1] == 0:
        orientation = np.zeros((pos.shape[0], pos.shape[1]))

    vocab_file = open(new_file_path, "w")
    for i in range(0, pos.shape[0]):
        vocab_file.write(":start transformation: \n")
        vocab_file.write(f"translation = {pos[i, 0]} {pos[i, 1]} {pos[i, 2]} \n")
        vocab_file.write(f"rotation = {orientation[i, 0]} {orientation[i, 1]} {orientation[i, 2]} \n")
        vocab_file.write(":stop transformation:\n\n")

    vocab_file.close()
