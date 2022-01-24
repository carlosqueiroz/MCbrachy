import ntpath
import os
from typing import Tuple, Union, Any

import numpy as np
from generate_simulation_input_files.material_attribution import TOPAS_MATERIAL_CONVERTER
from topas_file_generator.additional_materials.material_definition_table import MATERIAL_DEFINITION_TABLE
from topas_file_generator.geometries.tg186_patient import TG186_PATIENT
from extraction_pipeline_components.storage_objects.rt_struct_storage_classes import Structures


def generate_3d_index_mapping_for_structures(structures: Structures, list_of_desired_structures, path_to_save_to,
                                             save_to_file=False,
                                             ):
    """

    :param structures:
    :param save_to_file:
    :param path_to_save_to:
    :param list_of_desired_structures:
    :return:
    """
    slices, rows, columns = structures.image_shape
    new_index_3d_array = np.zeros([slices, rows, columns])
    it = 1
    for organs in list_of_desired_structures:
        organ_mask = structures.get_specific_mask(organs, organs)
        binary_mask = organ_mask.get_3d_mask()
        new_index_3d_array = np.ma.array(new_index_3d_array, mask=binary_mask).filled(it)
        it += 1

    if save_to_file:
        new_index_3d_array.astype(np.int16).tofile(path_to_save_to)

    return new_index_3d_array


def generate_topas_input_string_and_3d_mapping(structures: Structures, list_of_desired_structures,
                                               path_to_save_to):
    voxel_size_z, voxel_size_y, voxel_size_x = structures.z_y_x_spacing
    nb_z, nb_y, nb_x = structures.image_shape
    directory = os.path.dirname(path_to_save_to)
    file_name = ntpath.basename(path_to_save_to)
    originx = structures.x_y_z_origin[0]
    originy = structures.x_y_z_origin[1]
    originz = structures.x_y_z_origin[2]
    transx = originx - (nb_x * voxel_size_x - voxel_size_x) / 2
    transy = originy - (nb_y * voxel_size_y - voxel_size_y) / 2
    transz = -originz - (nb_z * voxel_size_z - voxel_size_z) / 2

    tag_numbers = f"{len(list_of_desired_structures) + 1} 0"
    material_names = f"""{len(list_of_desired_structures) + 1} "TG186Water" """

    it = 1
    added_material = ["TG186Water"]
    for organs in list_of_desired_structures:
        material_name = TOPAS_MATERIAL_CONVERTER[organs]
        if material_name not in added_material:
            added_material.append(material_name)

        tag_numbers = tag_numbers + f" {it}"
        it += 1
        material_names = material_names + f""""{material_name}" """

    header = """
                # ====================================================== #
                #                      Materials                         #
                # ====================================================== #
            """
    material_definition = header + "\n\n"
    for material in added_material:
        if material in MATERIAL_DEFINITION_TABLE.keys():
            material_definition = material_definition + MATERIAL_DEFINITION_TABLE[material] + "\n\n"

    generate_3d_index_mapping_for_structures(structures, list_of_desired_structures, save_to_file=True,
                                             path_to_save_to=path_to_save_to)

    return material_definition + TG186_PATIENT.substitute(input_directory=directory, input_file_name=file_name,
                                                          transx=transx,
                                                          transy=transy, tranz=transz, rotx="0.", roty="0.",
                                                          rotz="0.",
                                                          nb_of_columns=nb_x, nb_of_rows=nb_y, nb_of_slices=nb_z,
                                                          voxel_size_x=voxel_size_x, voxel_size_z=voxel_size_x,
                                                          voxel_size_y=voxel_size_y,
                                                          tag_numbers=tag_numbers, material_names=material_names,
                                                          parent="World")


def generate_egs_phant_file_from_structures(structures: Structures, new_file_path: str, density_dict: dict) -> None:
    """
    This method will produce a egs_phant file from all the contour specified in the density_dict.

    The keys of the density_dict must be from 1 to the number of contours desired. The integer key will specify
    which contour must be underneath the others.

    Each integer keys must be associated to dict with three keys:
        structure: the roi name of the associated mask
        density: the density of the material
        name_in_egs: the name that will be written in the egs_phant file

    :param structures:
    :param new_file_path:
    :param density_dict:
    """

    number_of_structures = len(density_dict.keys())
    image_shape = structures.image_shape
    _, mask_dict = structures.get_3d_image_with_all_masks()
    density_tensor = np.ones((image_shape[0], image_shape[1], image_shape[2]))
    struct_tensor = np.ones((image_shape[0], image_shape[1], image_shape[2]))
    for i in range(2, number_of_structures + 1):
        current_struct = density_dict[i]["structure"]
        current_index = i
        current_density = density_dict[i]["density"]
        density_tensor = np.ma.array(density_tensor, mask=np.flip(mask_dict[current_struct], axis=0)).filled(
            current_density)
        struct_tensor = np.ma.array(struct_tensor, mask=np.flip(mask_dict[current_struct], axis=0)).filled(
            current_index)

    x_bounds, y_bounds, z_bounds = _generate_x_y_and_z_list_of_voxel_boundaries(structures)
    _make_egs_phant(structures, new_file_path, density_dict, x_bounds / 10, y_bounds / 10, z_bounds / 10, struct_tensor,
                    density_tensor)


def _make_egs_phant(structures: Structures, new_file_path: str, density_dict: dict, x_bounds: list, y_bounds: list,
                    z_bounds: list,
                    struct_tensor: np.ndarray, density_tensor: np.ndarray) -> None:
    """
    This method simply writes the egs_phant file from the structures' informations.

    :param structures:
    :param new_file_path:
    :param density_dict:
    :param x_bounds:
    :param y_bounds:
    :param z_bounds:
    :param struct_tensor:
    :param density_tensor:
    :return:
    """
    number_of_structures = len(density_dict.keys())
    image_shape = structures.image_shape
    vocab_file = open(new_file_path, "w")

    vocab_file.write(f"{number_of_structures}\n")
    for i in range(1, len(density_dict.keys()) + 1):
        struc = density_dict[i]["name_in_egs"]
        vocab_file.write(f"{struc}\n")

    vocab_file.write(fr"  ")
    for i in range(0, len(density_dict.keys()) - 1):
        vocab_file.write(fr"0.25       ")
    vocab_file.write(f"0.25\n")
    vocab_file.write(f"  {image_shape[2]}  {image_shape[1]}  {image_shape[0]}\n")

    for i in range(0, len(x_bounds) // 3):
        vocab_file.write(
            f"   {x_bounds[3 * i]}          {x_bounds[3 * i + 1]}          {x_bounds[3 * i + 2]}       \n")
    if len(x_bounds) % 3 == 1:
        vocab_file.write(f"   {x_bounds[-1]}          \n")
    if len(x_bounds) % 3 == 2:
        vocab_file.write(f"   {x_bounds[-2]}          {x_bounds[-1]}          \n")

    for i in range(0, len(y_bounds) // 3):
        vocab_file.write(
            f"   {y_bounds[3 * i]}          {y_bounds[3 * i + 1]}          {y_bounds[3 * i + 2]}       \n")

    if len(y_bounds) % 3 == 1:
        vocab_file.write(f"   {y_bounds[-1]}          \n")
    if len(y_bounds) % 3 == 2:
        vocab_file.write(f"   {y_bounds[-2]}          {y_bounds[-1]}          \n")

    for i in range(0, len(z_bounds) // 3):
        vocab_file.write(
            f"   {z_bounds[3 * i]}          {z_bounds[3 * i + 1]}          {z_bounds[3 * i + 2]}       \n")

    if len(z_bounds) % 3 == 1:
        vocab_file.write(f"   {z_bounds[-1]}          \n")
    if len(z_bounds) % 3 == 2:
        vocab_file.write(f"   {z_bounds[-2]}          {z_bounds[-1]}          \n")

    for z_slice in range(0, image_shape[0]):
        np.savetxt(vocab_file, struct_tensor[z_slice, :, :], delimiter="", newline="\n", fmt="%u")
    vocab_file.write(f"\n")
    vocab_file.write(f"\n")

    flat_density = density_tensor.flatten()
    for i in range(0, len(flat_density) // 3):
        vocab_file.write(
            f"  {flat_density[3 * i]}         {flat_density[3 * i + 1]}         {flat_density[3 * i + 2]}       \n")
    if len(y_bounds) % 3 == 1:
        vocab_file.write(f"  {flat_density[-1]}        \n")
    if len(y_bounds) % 3 == 2:
        vocab_file.write(f"  {flat_density[-2]}         {flat_density[-1]}        \n")

    vocab_file.close()


def _generate_x_y_and_z_list_of_voxel_boundaries(structures: Structures) -> Tuple[Union[float, Any], Union[float, Any],
                                                                                  Union[float, Any]]:
    """
    This methods generates the upper and lower bounds of every voxels in x y and z axis.
    Reference point is the patient coordinates and values are in mm

    :return: the three list of voxel bounds in x y and z.
    """
    spacing_z = structures.z_y_x_spacing[2]
    spacing_y = structures.z_y_x_spacing[1]
    spacing_x = structures.z_y_x_spacing[0]
    origin_x = structures.x_y_z_origin[0] - spacing_x / 2
    origin_y = structures.x_y_z_origin[1] - spacing_y / 2
    origin_z = structures.x_y_z_origin[2] - spacing_z / 2

    nb_z, nb_y, nb_x = structures.image_shape
    x_bounds = (np.arange(0, nb_x + 1) * spacing_x) + origin_x
    y_bounds = (np.arange(0, nb_y + 1) * spacing_y) + origin_y
    z_bounds = -(np.arange(nb_z, -1, -1) * spacing_z) + origin_z

    return x_bounds, y_bounds, z_bounds
