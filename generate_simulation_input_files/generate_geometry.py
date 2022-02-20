import gzip
import ntpath
import os
from typing import Tuple, Union, Any
import numpy as np
from topas_file_generator.LDR_brachy.LDR_physics import LDR_BRACHY_PHYSICS
from egs_brachy_file_generator.geometries import from_egs_phant
from generate_simulation_input_files.material_attribution import EGS_BRACHY_MATERIAL_CONVERTER
from egs_brachy_file_generator.materials.materials import EGS_BRACHY_DENSITIES
from generate_simulation_input_files.material_attribution import TOPAS_MATERIAL_CONVERTER
from topas_file_generator.additional_materials.material_definition_table import MATERIAL_DEFINITION_TABLE
from topas_file_generator.geometries.tg186_patient import TG186_PATIENT
from dicom_rt_context_extractor.storage_objects.rt_struct_storage_classes import Structures


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

    new_index_3d_array = np.flip(new_index_3d_array, axis=0)
    if save_to_file:
        new_index_3d_array.astype(np.int16).tofile(path_to_save_to)

    return new_index_3d_array


def generate_topas_input_string_and_3d_mapping(structures: Structures, list_of_desired_structures,
                                               path_to_save_to):
    voxel_size_z, voxel_size_y, voxel_size_x = structures.z_y_x_spacing
    nb_z, nb_y, nb_x = structures.image_shape
    directory = os.path.dirname(path_to_save_to)
    file_name = ntpath.basename(path_to_save_to)
    transx = (nb_x * voxel_size_x - voxel_size_x) / 2
    transy = (nb_y * voxel_size_y - voxel_size_y) / 2
    transz = - (nb_z * voxel_size_z - voxel_size_z) / 2

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

    smaller_voxel_size = min([voxel_size_x, voxel_size_y, voxel_size_z])
    material_and_physics = material_definition + LDR_BRACHY_PHYSICS.substitute(
        smaller_voxel_size=smaller_voxel_size) + "\n\n "

    return material_and_physics + TG186_PATIENT.substitute(input_directory=directory, input_file_name=file_name,
                                                           transx=transx,
                                                           transy=transy, transz=transz, rotx="0.", roty="0.",
                                                           rotz="0.",
                                                           nb_of_columns=nb_x, nb_of_rows=nb_y, nb_of_slices=nb_z,
                                                           voxel_size_x=voxel_size_x, voxel_size_z=voxel_size_z,
                                                           voxel_size_y=voxel_size_y,
                                                           tag_numbers=tag_numbers, material_names=material_names,
                                                           hlx=nb_x * voxel_size_x, hly=nb_y * voxel_size_y,
                                                           hlz=nb_z * voxel_size_z)


def generate_egs_phant_file_from_structures(structures: Structures, new_file_path: str, density_dict: dict,
                                            crop=False, crop_margin=20, sym=False):
    """
    This method will produce a egs_phant file from all the contour specified in the density_dict.

    The keys of the density_dict must be from 1 to the number of contours desired. The integer key will specify
    which contour must be underneath the others.

    Each integer keys must be associated to dict with three keys:
        structure: the roi name of the associated mask
        density: the density of the material
        name_in_egs: the name that will be written in the egs_phant file

    :param sym:
    :param crop_margin:
    :param crop:
    :param structures:
    :param new_file_path:
    :param density_dict:
    """

    number_of_structures = len(density_dict.keys())
    if crop:
        list_of_mask_names = []
        for i in range(2, number_of_structures + 1):
            list_of_mask_names.append(density_dict[i]["structure"])

        mask_dict, offsetz, offsety, offsetx = crop_phantom_to_structures(structures, list_of_mask_names,
                                                                          crop_margin, sym)
        image_shape = mask_dict[list_of_mask_names[0]].shape
        print("cropped:",image_shape)

    else:
        image_shape = structures.image_shape
        _, mask_dict = structures.get_3d_image_with_all_masks()
        offsetz, offsety, offsetx = 0, 0, 0

    density_tensor = np.ones((image_shape[0], image_shape[1], image_shape[2])) * 0.998
    struct_tensor = np.ones((image_shape[0], image_shape[1], image_shape[2]))
    for i in range(2, number_of_structures + 1):
        current_struct = density_dict[i]["structure"]
        current_index = i
        current_density = density_dict[i]["density"]
        density_tensor = np.ma.array(density_tensor, mask=np.flip(mask_dict[current_struct], axis=0)).filled(
            current_density)
        struct_tensor = np.ma.array(struct_tensor, mask=np.flip(mask_dict[current_struct], axis=0)).filled(
            current_index)

    x_bounds, y_bounds, z_bounds = _generate_x_y_and_z_list_of_voxel_boundaries(structures, image_shape, [offsetz,
                                                                                                          offsety,
                                                                                                          offsetx])
    _make_egs_phant(image_shape, new_file_path, density_dict, x_bounds / 10, y_bounds / 10, z_bounds / 10,
                    struct_tensor,
                    density_tensor)

    return offsetz, offsety, offsetx


def crop_phantom_to_structures(structures: Structures, list_of_mask_names, crop_margin=20, sym=False):
    _, mask_dict = structures.get_3d_image_with_all_masks()

    image_shape = structures.image_shape
    spacing_z = structures.z_y_x_spacing[0]
    spacing_y = structures.z_y_x_spacing[1]
    spacing_x = structures.z_y_x_spacing[2]
    total_mask = np.zeros((image_shape[0], image_shape[1], image_shape[2]))
    for mask_name in list_of_mask_names:
        total_mask += mask_dict[mask_name]

    true_points = np.argwhere(total_mask)
    min_z = true_points[:, 0].min() - int(crop_margin / spacing_z)
    if min_z < 0:
        min_z = 0
    max_z = true_points[:, 0].max() + int(crop_margin / spacing_z)
    if max_z >= image_shape[0] - 1:
        max_z = image_shape[0] - 2
    min_y = true_points[:, 1].min() - int(crop_margin / spacing_y)
    if min_y < 0:
        min_y = 0
    max_y = true_points[:, 1].max() + int(crop_margin / spacing_y)
    if max_y >= image_shape[1] - 1:
        max_y = image_shape[1] - 2
    min_x = true_points[:, 2].min() - int(crop_margin / spacing_x)
    if min_x < 0:
        min_x = 0
    max_x = true_points[:, 2].max() + int(crop_margin / spacing_y)
    if max_x >= image_shape[2] - 1:
        max_x = image_shape[2] - 2

    if sym:
        i_min = max(min_z, image_shape[0] - max_z)
        j_min = max(min_y, image_shape[1] - max_y)
        k_min = max(min_x, image_shape[2] - max_x)
        i_max = max(-min_z, max_z - image_shape[0])
        j_max = max(-min_y, max_y - image_shape[1])
        k_max = max(-min_x, max_x - image_shape[2])
    else:
        i_min = min_z
        j_min = min_y
        k_min = min_x
        i_max = max_z - image_shape[0]
        j_max = max_y - image_shape[1]
        k_max = max_x - image_shape[2]

    offset_z = -(i_min - 1) * spacing_z
    offset_y = (j_min - 1) * spacing_y
    offset_x = (k_min - 1) * spacing_x

    cropped_masks = {}
    for mask_name in list_of_mask_names:
        cropped_masks[mask_name] = mask_dict[mask_name][i_min: i_max + 1, j_min: j_max + 1, k_min: k_max + 1]

    return cropped_masks, offset_z, offset_y, offset_x


def _make_egs_phant(image_shape, new_file_path: str, density_dict: dict, x_bounds: list, y_bounds: list,
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
    vocab_file = open(new_file_path, "a+")

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

    g_zip = gzip.open(f'{new_file_path}.gz', 'wb')
    g_zip.writelines(vocab_file)
    g_zip.close()
    vocab_file.close()
    input_phant = open(new_file_path, 'rb')
    s = input_phant.read()
    input_phant.close()

    output = gzip.GzipFile(f"{new_file_path}.gz", 'wb')
    output.write(s)
    output.close()


def _generate_x_y_and_z_list_of_voxel_boundaries(structures: Structures, image_shape, all_offsets) -> Tuple[
    Union[float, Any],
    Union[float, Any],
    Union[float, Any]]:
    """
    This methods generates the upper and lower bounds of every voxels in x y and z axis.
    Reference point is the patient coordinates and values are in mm

    :return: the three list of voxel bounds in x y and z.
    """
    spacing_z = structures.z_y_x_spacing[0]
    spacing_y = structures.z_y_x_spacing[1]
    spacing_x = structures.z_y_x_spacing[2]
    origin_x = structures.x_y_z_origin[0] + all_offsets[2] - spacing_x / 2
    origin_y = structures.x_y_z_origin[1] + all_offsets[1] - spacing_y / 2
    origin_z = structures.x_y_z_origin[2] + all_offsets[0] - spacing_z / 2

    nb_z, nb_y, nb_x = image_shape
    x_bounds = (np.arange(0, nb_x + 1) * spacing_x) + origin_x
    y_bounds = (np.arange(0, nb_y + 1) * spacing_y) + origin_y
    z_bounds = -(np.arange(nb_z, -1, -1) * spacing_z) + origin_z

    return x_bounds, y_bounds, z_bounds


def generate_egs_brachy_geo_string_and_phant(structures: Structures, new_file_path: str, list_of_structures: list,
                                             source_geo: str, egs_folder_path, crop=False):
    density_dict = {1: {"name_in_egs": "WATER_0.998", "structure": "body", "density": 0.998}}
    it = 2
    for struct in list_of_structures:
        density_dict[it] = {"name_in_egs": EGS_BRACHY_MATERIAL_CONVERTER[struct],
                            "structure": struct,
                            "density": EGS_BRACHY_DENSITIES[EGS_BRACHY_MATERIAL_CONVERTER[struct]]}
        it += 1

    offsets = generate_egs_phant_file_from_structures(structures, new_file_path, density_dict, crop=crop)

    return from_egs_phant.EGS_BRACHY_GEO_FROM_PHANT.substitute(egs_phant_compress_path=new_file_path + ".gz",
                                                               path_to_egs_folder=egs_folder_path,
                                                               source_geo=source_geo), offsets
