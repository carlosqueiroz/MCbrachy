import os
from root import ROOT
from typing import Tuple, List, Dict, Union, Any
import ntpath
import numpy as np
import pydicom
from simulation_files.topas_file_templates.medium_definition import TG186_PATIENT
from rt_utils import RTStructBuilder
from extraction_pipeline_components.storage_objects.storing_files.topas_material_conversion import *

from extraction_pipeline_components.utils.search_instance_and_convert_coord_in_pixel import find_instance_in_folder, \
    generate_3d_image_from_series, find_modality_in_folder

default_path_to_3d_index_mapping = os.path.join(ROOT, r"simulation_files", "3d_index_mapping", "3d_index_mapping")


class SliceMask:
    def __init__(self, mask_array: np.ndarray, image_uid: str, slice_number: int, parent_mask):
        """
        This object represents a single image slice with a single mask array.

        :param mask_array: 2d array
        :param image_uid: uid of the associated image
        :param slice_number: the slice number in the 3d pixel coordinates
        :param parent_mask: mask containing all the slice associated with the same contour
        """
        self.image_uid = image_uid
        self.mask_array = mask_array
        self.slice_number = slice_number
        self.parent_mask = parent_mask

    def get_slice_mask_with_image(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        This method will search for the image associated to the
        mask. This image should be located somewhere in the study_folder
        of the parent structure.

        :return: the 2D image associated with the 2d mask
        """
        image_path = find_instance_in_folder(self.image_uid, self.parent_mask.parent_structures.study_folder)
        image = pydicom.dcmread(image_path).pixel_array

        return image, self.mask_array


class Mask:
    def __init__(self, roi_name: str, observation_label: str, parent_structures, list_mask_slices):
        """
        This class represents a full contour made of multiple slices.

        :param roi_name: roi name corresponding to the contour
        :param observation_label: observation label given to the contour
        :param parent_structures: the parent structure object containing the frame of reference info.
        :param list_mask_slices: list of the SliceMask objects
        """
        self.roi_name = roi_name
        self.observation_label = observation_label
        self.parent_structures = parent_structures
        self.list_mask_slices = list_mask_slices

    def add_slices(self, slices) -> None:
        """
        This method adds one or many SliceMasks to the
        mask list_mask_slices.

        :param slices: SliceMask object or list of SliceMask objects
        :return: None
        """
        if type(slices) is list:
            self.list_mask_slices.extend(slices)

        else:
            self.list_mask_slices.append(slices)

    def list_slice_numbers(self) -> List[int]:
        """
        This method simply returns a list of all the
        possible values of slice number
        :return: list of slice numbers contained in the mask
        """
        list_slice_numbers = []
        for mask_slices in self.list_mask_slices:
            list_slice_numbers.append(mask_slices.slice_number)

        return list_slice_numbers

    def get_specific_slice(self, slice_number):
        """
        This method will simply return the corresponding Slice
        for the given slice number. This method returns None when not found

        :param slice_number: the desired slice number
        :return: None or SliceMask
        """
        for slice_mask in self.list_mask_slices:
            if slice_number == slice_mask.slice_number:
                return slice_mask

    def get_3d_mask_with_3d_image(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        This method will fuse all the slices into one 3d mask with one 3d image.


        :return: the 3d image and the 3d mask array
        """
        initial_mask = np.zeros(self.parent_structures.image_shape)
        last_image_uid = 0
        for slices in self.list_mask_slices:
            initial_mask[slices.slice_number, :, :] = slices.mask_array
            last_image_uid = slices.image_uid

        path_to_image = find_instance_in_folder(last_image_uid, self.parent_structures.study_folder)
        series_folder = os.path.dirname(path_to_image)
        image = generate_3d_image_from_series(self.parent_structures.image_shape, series_folder,
                                              self.parent_structures.z_y_x_spacing, self.parent_structures.x_y_z_origin,
                                              self.parent_structures.x_y_z_rotation_vectors)

        return image, initial_mask

    def get_3d_mask(self) -> np.ndarray:
        """
        This method will fuse all the slices into one 3d mask with one 3d image.


        :return: the 3d image and the 3d mask array
        """
        initial_mask = np.zeros(self.parent_structures.image_shape)
        for slices in self.list_mask_slices:
            initial_mask[slices.slice_number, :, :] = slices.mask_array

        return initial_mask


class Structures:
    def __init__(self, rt_struct_uid: str, image_shape: Tuple[int, int, int],
                 z_y_x_spacing: Tuple[float, float, float], x_y_z_origin: List[float],
                 x_y_z_rotation_vectors: List[float], list_of_masks, study_folder: str):
        """
        This object represents all the contours associated to a 3d image.

        :param image_shape: shape of the 3d image
        :param z_y_x_spacing: spacial dimension of a voxel
        :param x_y_z_origin: origin of the image in patient coordinates
        :param x_y_z_rotation_vectors: image axes in the patient coordinates
        :param list_of_masks: list of Mask object associated to each contour
        :param study_folder: the path to the folder containing the study
        """
        self.rt_struct_uid = rt_struct_uid
        self.image_shape = image_shape
        self.z_y_x_spacing = z_y_x_spacing
        self.x_y_z_origin = x_y_z_origin
        self.x_y_z_rotation_vectors = x_y_z_rotation_vectors
        self.list_of_masks = list_of_masks
        self.study_folder = study_folder

    def add_masks(self, mask) -> None:
        """
        This method adds one or many Masks to the
        mask list_of_masks.

        :param mask: Mask object or list of Mask objects
        :return: None
        """
        if type(mask) is list:
            self.list_of_masks.extend(mask)

        else:
            self.list_of_masks.append(mask)

    def get_specific_mask(self, roi_name: str, observation_label: str):
        """
        This method will simply return the corresponding Mask
        for the given roi_name or observation_label. In order to return a mask,
        at least one mask should have a matching roi_name or observation_label.
        This method returns None when not found
        :param roi_name: roi name corresponding to the contour
        :param observation_label: observation label given to the conto
        :return: Mask
        """
        for mask in self.list_of_masks:
            if roi_name == mask.roi_name or observation_label == mask.observation_label:
                return mask

    def list_roi_names(self) -> List[str]:
        """
        This method simply return all the possible values of
        roi names contained in all the masks

        :return: list of all the roi names of each mask
        """
        list_of_roi_names = []
        for mask in self.list_of_masks:
            list_of_roi_names.append(mask.roi_name)

        return list_of_roi_names

    def list_roi_observation_labels(self) -> List[str]:
        """
        This method simply return all the possible values of
        observation labels contained in all the masks

        :return: list of all the observation labels of each mask
        """
        list_roi_observation_labels = []
        for mask in self.list_of_masks:
            list_roi_observation_labels.append(mask.observation_label)

        return list_roi_observation_labels

    def get_3d_image_with_all_masks(self) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """
        This method will build the 3d mask arrays of every mask
        and produce the associated 3d image.

        :return: the image and the dict containing all the masks
        """
        last_image_uid = 0
        mask_dict = {}
        for mask in self.list_of_masks:
            initial_mask = np.zeros(self.image_shape)

            for slices in mask.list_mask_slices:
                initial_mask[slices.slice_number - 1, :, :] = slices.mask_array
                last_image_uid = slices.image_uid

            mask_dict[mask.roi_name] = initial_mask

        path_to_image = find_instance_in_folder(last_image_uid, self.study_folder)
        series_folder = os.path.dirname(path_to_image)
        image = generate_3d_image_from_series(self.image_shape, series_folder,
                                              self.z_y_x_spacing, self.x_y_z_origin,
                                              self.x_y_z_rotation_vectors)

        return image, mask_dict

    def generate_egs_phant_file_from_structures(self, new_file_path: str, density_dict: dict) -> None:
        """
        This method will produce a egs_phant file from all the contour specified in the density_dict.

        The keys of the density_dict must be from 1 to the number of contours desired. The integer key will specify
        which contour must be underneath the others.

        Each integer keys must be associated to dict with three keys:
            structure: the roi name of the associated mask
            density: the density of the material
            name_in_egs: the name that will be written in the egs_phant file

        :param new_file_path:
        :param density_dict:
        """

        number_of_structures = len(density_dict.keys())
        image_shape = self.image_shape
        _, mask_dict = self.get_3d_image_with_all_masks()
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

        x_bounds, y_bounds, z_bounds = self.generate_x_y_and_z_list_of_voxel_boundaries()
        self.make_egs_phant(new_file_path, density_dict, x_bounds / 10, y_bounds / 10, z_bounds / 10, struct_tensor,
                            density_tensor)

    def make_egs_phant(self, new_file_path: str, density_dict: dict, x_bounds: list, y_bounds: list, z_bounds: list,
                       struct_tensor: np.ndarray, density_tensor: np.ndarray) -> None:
        """
        This method simply writes the egs_phant file from the structures' informations.

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
        image_shape = self.image_shape
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

    def generate_x_y_and_z_list_of_voxel_boundaries(self) -> Tuple[Union[float, Any], Union[float, Any], float]:
        """
        This methods generates the upper and lower bounds of every voxels in x y and z axis.
        Reference point is the patient coordinates and values are in mm

        :return: the three list of voxel bounds in x y and z.
        """
        spacing_z = self.z_y_x_spacing[2]
        spacing_y = self.z_y_x_spacing[1]
        spacing_x = self.z_y_x_spacing[0]
        origin_x = self.x_y_z_origin[0] - spacing_x / 2
        origin_y = self.x_y_z_origin[1] - spacing_y / 2
        origin_z = self.x_y_z_origin[2] - spacing_z / 2

        nb_z, nb_y, nb_x = self.image_shape
        x_bounds = (np.arange(0, nb_x + 1) * spacing_x) + origin_x
        y_bounds = (np.arange(0, nb_y + 1) * spacing_y) + origin_y
        z_bounds = -(np.arange(nb_z, -1, -1) * spacing_z) + origin_z

        return x_bounds, y_bounds, z_bounds

    def add_mask_from_3d_array(self, mask_3d: np.ndarray, roi_name: str, observation_label: str,
                               segmentation_method: int, add_to_original_rt_struct_file=False) -> None:
        """
        This method allows to add a contour which was not originally in the DICOM.
        To do so, this method takes the 3d mask array (which has to be the same dimension as the corresponding 3d image),
        the roi name and the observation label to generate a new Mask object that will be added to the list_of_masks

        :param segmentation_method: 2 = manual, 1= semi-automatic, 0=automatic
        :param add_to_original_rt_struct_file:
        :param mask_3d: 3d array with the 3d image size
        :param roi_name:
        :param observation_label:
        """
        path_to_dicom = find_instance_in_folder(self.rt_struct_uid, self.study_folder)
        json_dicom = pydicom.dcmread(path_to_dicom).to_json_dict()
        uid_dict = self.rebuild_image_references_dict(json_dicom)
        new_mask = Mask(roi_name, observation_label, self, [])
        for i in range(0, len(mask_3d)):
            new_mask.add_slices(SliceMask(mask_3d[i, :, :], uid_dict[i + 1], i, new_mask))

        self.add_masks(new_mask)

        if add_to_original_rt_struct_file:
            path_to_rt_struct = find_instance_in_folder(self.rt_struct_uid, self.study_folder)
            path_to_a_ct_file = find_modality_in_folder("CT", self.study_folder)
            path_to_ct_folder = os.path.dirname(path_to_a_ct_file)
            rtstruct = RTStructBuilder.create_from(
                dicom_series_path=path_to_ct_folder,
                rt_struct_path=path_to_rt_struct)
            rtstruct.add_roi(
                mask=np.swapaxes(np.swapaxes(np.flip(mask_3d, 0), 1, 2), 0, 2),
                name=roi_name,
                description=observation_label,
                roi_generation_algorithm=segmentation_method
            )

            rtstruct.save(path_to_rt_struct)

    def generate_3d_index_mapping_for_structures(self, list_of_desired_structures, save_to_file=False,
                                                 path_to_save_to=default_path_to_3d_index_mapping):
        """

        :param save_to_file:
        :param path_to_save_to:
        :param list_of_desired_structures:
        :return:
        """
        slices, rows, columns = self.image_shape
        new_index_3d_array = np.zeros([slices, rows, columns])
        it = 1
        for organs in list_of_desired_structures:
            organ_mask = self.get_specific_mask(organs, organs)
            binary_mask = organ_mask.get_3d_mask()
            new_index_3d_array = np.ma.array(new_index_3d_array, mask=binary_mask).filled(it)
            it += 1

        if save_to_file:
            new_index_3d_array.astype(np.int16).tofile(path_to_save_to)

        return new_index_3d_array

    def generate_topas_input_string_and_3d_mapping(self, list_of_desired_structures,
                                                   path_to_save_to=default_path_to_3d_index_mapping):
        voxel_size_z, voxel_size_y, voxel_size_x = self.z_y_x_spacing
        nb_z, nb_y, nb_x = self.image_shape
        directory = os.path.dirname(path_to_save_to)
        file_name = ntpath.basename(path_to_save_to)
        originx = self.x_y_z_origin[0]
        originy = self.x_y_z_origin[1]
        originz = self.x_y_z_origin[2]
        transx = originx - (nb_x * voxel_size_x - voxel_size_x) / 2
        transy = originy - (nb_y * voxel_size_y - voxel_size_y) / 2
        transz = -originz - (nb_z * voxel_size_z - voxel_size_z) / 2

        tag_numbers = f"{len(list_of_desired_structures) + 1} 0"
        material_names = f"""{len(list_of_desired_structures) + 1} "TG186Water" """

        it = 1
        added_material = ["TG186Water"]
        for organs in list_of_desired_structures:
            material_name = MATERIAL_CONVERTER[organs]
            if material_name not in added_material:
                added_material.append(material_name)

            tag_numbers = tag_numbers + f" {it}"
            it +=1
            material_names = material_names + f""""{material_name}" """

        material_definition = HEADER + "\n\n"
        for material in added_material:
            if material in MATERIAL_DEFINITION_TABLE.keys():
                material_definition = material_definition + MATERIAL_DEFINITION_TABLE[material] + "\n\n"

        self.generate_3d_index_mapping_for_structures(list_of_desired_structures, save_to_file=True,
                                                      path_to_save_to=path_to_save_to)

        return material_definition + TG186_PATIENT.substitute(input_directory=directory, input_file_name=file_name,
                                                              transx=transx,
                                                              transy=transy, tranz=transz, rotx="0.", roty="0.",
                                                              rotz="0.",
                                                              nb_of_columns=nb_x, nb_of_rows=nb_y, nb_of_slices=nb_z,
                                                              voxel_size_x=voxel_size_x, voxel_size_z=voxel_size_x,
                                                              voxel_size_y=voxel_size_y,
                                                              tag_numbers=tag_numbers, material_names=material_names)

    @staticmethod
    def rebuild_image_references_dict(open_dicom_as_json: dict) -> dict:
        """
        This method will build a dictionary associating each slice to an
        image uid. This dictionary will be used when associating contours
        slices with its image.
        :param open_dicom_as_json: rt_struct dicom as json
        :return: the dictionary having slice number as key and uid as value
        """
        all_images_uids = \
            open_dicom_as_json["30060010"]["Value"][0]["30060012"]["Value"][0]["30060014"]["Value"][0]["30060016"][
                "Value"]

        ref_images_dict = {}
        if "00081160" not in all_images_uids[0].keys():
            it = 1
            for elements in all_images_uids:
                ref_images_dict[it] = str(elements["00081155"]["Value"][0])
                it += 1

        else:
            for elements in all_images_uids:
                it = int(elements["00081160"]["Value"][0])
                ref_images_dict[it] = str(elements["00081155"]["Value"][0])

        return ref_images_dict
