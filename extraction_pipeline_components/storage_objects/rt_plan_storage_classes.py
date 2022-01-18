import copy
import logging
import os

import numpy as np
import pydicom

import simulation_files.topas_file_templates.iodine125_select_seed as selectseed
import simulation_files.topas_file_templates.physics as physics

from extraction_pipeline_components.contour_extraction_as_masks import extract_masks_for_each_organs_for_each_slices
from extraction_pipeline_components.utils.search_instance_and_convert_coord_in_pixel import find_instance_in_folder, \
    convert_real_coord_to_pixel_coord
from extraction_pipeline_components.storage_objects.rt_struct_storage_classes import Structures
from extraction_pipeline_components.storage_objects.rt_dose_storage_classes import Dosimetry
from extraction_pipeline_components.dosimetry_extraction import extract_dosimetry
from root import ROOT

default_path_to_3d_index_mapping = os.path.join(ROOT, r"simulation_files", "3d_index_mapping", "3d_index_mapping")
default_input_file_save_path = os.path.join(ROOT, r"simulation_files", "topas_simulation_files",
                                            "simulation_input_file.txt")


class LDRBrachyPlan:
    def __init__(self, rt_plan_uid: str, rt_struct_uid: str, rt_dose_uid: str, rt_plan_date: str, rt_plan_time: float,
                 list_of_sources: list = None, structures: Structures = None, dosimetry: Dosimetry = None):
        """
        This class will be used to store all the information extracted
        from a rt plan dicom. This specific class will only contain the global
        context information. All the sources relative informations will be contained in the
        sources objects stored inside this class

        :param rt_plan_uid: uid of the rt plan associated with this treatment
        :param rt_struct_uid: uid of the rt struct associated with this treatment
        :param rt_dose_uid: uid of the rt dose associated with this treatment
        :param rt_plan_date: date of the plan
        :param rt_plan_time: time of the plan
        :param list_of_sources: list of sources objects
        :param structures: Structure object associated to the same treatment
        """
        self.rt_dose_uid = rt_dose_uid
        self.rt_plan_uid = rt_plan_uid
        if list_of_sources is None:
            list_of_sources = []
        self.rt_struct_uid = rt_struct_uid
        self.rt_plan_date = rt_plan_date
        self.rt_plan_time = rt_plan_time
        if structures is not None:
            self.structures_are_built = True
        else:
            self.structures_are_built = False

        if dosimetry is not None:
            self.dosi_is_built = True
        else:
            self.dosi_is_built = False

        self.structures = structures
        self.dosimetry = dosimetry
        self.list_of_sources = list_of_sources

    def extract_structures(self, study_folder: str) -> None:
        """
        Knowing the study folder and the uid of the rt struct,
        this method will search for the rt struct file. If
        it is found, it will extract all of its information
        and store the associated Structures object into the
        structures attribute. If a structure is already in
        the attributes, this method won't do a thing.

        :param study_folder: path to the folder containing the study
        """
        if not self.structures_are_built:
            rt_struct_path = find_instance_in_folder(self.rt_struct_uid, study_folder)
            if rt_struct_path is None:
                logging.warning(f"RT STRUCT {self.rt_struct_uid} not found. The structures won't be built")
                self.structures = None

            structures = extract_masks_for_each_organs_for_each_slices(rt_struct_path, study_folder)
            self.structures = structures
            self.structures_are_built = True
        else:
            logging.warning("Structures are already built")

    def extract_dosimetry(self, study_folder: str):
        """
        :param study_folder: path to the folder containing the study
        """
        if not self.dosi_is_built:
            rt_dose_path = find_instance_in_folder(self.rt_dose_uid, study_folder)
            if rt_dose_path is None:
                logging.warning(f"RT DOSE {self.rt_dose_uid} not found. The dosimetry won't be built")
                self.dosimetry = None

            dosimetry = extract_dosimetry(rt_dose_path)
            self.dosimetry = dosimetry
            self.dosi_is_built = True

        else:
            logging.warning("Dosimetry is already built")

    def add_sources(self, sources) -> None:
        """
        This method adds one or many sources to the
        list_of_sources.

        :param sources:
        """
        if type(sources) is list:
            self.list_of_sources.extend(sources)

        else:
            self.list_of_sources.append(sources)

    def get_structures(self):
        return self.structures

    def get_dosimetry(self):
        return self.dosimetry

    def segmenting_calcification(self, h: float, r: float, study_folder: str) -> np.ndarray:
        """
        First version of the calcification segmentation algorithm. It is incomplete and will
        most likely be modified in the futere.

        This method first uses cylindrical mask to remove all the sources from the CT. To do so,
        this method will try to optimize the removal of sources pixels by placing a cylinder mask of
        h = height and r = radius at each source position.

        Afterwards, calcifications are segmented by a threshold of 348 HU, this value was selected using
        the Ca (20%) density of 1.4480g/cm3 converted using the CT calibration curves for the test cases.

        :param h:
        :param r:
        :param study_folder:
        :return: The 3d mask associated with the calcification
        """
        if not self.structures_are_built:
            self.extract_structures(study_folder)

        z_y_x_spacing, x_y_z_origin, x_y_rotation_vectors = self.structures.z_y_x_spacing, self.structures.x_y_z_origin, \
                                                            self.structures.x_y_z_rotation_vectors

        pos_in_pixels = convert_real_coord_to_pixel_coord(self.list_of_sources[0].positions.copy(), z_y_x_spacing,
                                                          x_y_z_origin,
                                                          x_y_rotation_vectors)

        image, masks = self.structures.get_specific_mask("prostate", "prostate").get_3d_mask_with_3d_image()
        calcification_mask = (348 < image) * masks

        def optimize_kills_on_number_of_slices(initial_mask: np.ndarray, slice_mask: np.ndarray,
                                               nb_slice_desired: int, theoretical_slice: int):
            """
            This method verifies if the cylinder mask covers a bigger volume of the source if
            we raise or lower the mask of one voxel

            :param initial_mask:
            :param slice_mask:
            :param nb_slice_desired:
            :param theoretical_slice:
            :return:
            """
            stack_of_slices = slice_mask.copy()
            for i in range(0, nb_slice_desired - 1):
                stack_of_slices = np.hstack([stack_of_slices, slice_mask])
            pm = int((nb_slice_desired - 1) / 2)
            assert nb_slice_desired == initial_mask[theoretical_slice - pm: theoretical_slice + pm + 1, :, :].shape[0]
            kills_centerd = initial_mask[theoretical_slice - pm: theoretical_slice + pm + 1, :, :].sum()
            chosen_center = theoretical_slice
            for i in range(-1, 2):
                offset_kills = initial_mask[i + theoretical_slice - pm: i + theoretical_slice + pm + 1, :, :].sum()
                if offset_kills > kills_centerd:
                    chosen_center = theoretical_slice + i
                    kills_centerd = offset_kills

            return chosen_center - pm, chosen_center + pm + 1, kills_centerd

        def optimize_kills_on_y_x_and_z(initial_mask, nb_slice_desired, theoretical_slice, thoeritical_x,
                                        theoretical_y):
            """
            This method verifies if the cylinder mask covers a bigger volume of the source if
            we move it by one voxel in the x and/or the y axis

            :param initial_mask:
            :param nb_slice_desired:
            :param theoretical_slice:
            :param thoeritical_x:
            :param theoretical_y:
            :return:
            """
            d_sqared = ((index_grid[1] - thoeritical_x) * z_y_x_spacing[2]) ** 2 + (
                    (index_grid[0] - theoretical_y) * z_y_x_spacing[1]) ** 2

            min_z, max_z, kills = optimize_kills_on_number_of_slices(initial_mask, d_sqared < 25, nb_slice_desired,
                                                                     theoretical_slice)
            for i in range(-1, 2):
                for j in range(-1, 2):
                    test_d_sqared = ((index_grid[1] - thoeritical_x + i) * z_y_x_spacing[2]) ** 2 + (
                            (index_grid[0] - theoretical_y + j) * z_y_x_spacing[1]) ** 2
                    t_min_z, t_max_z, t_kills = optimize_kills_on_number_of_slices(calcification_mask,
                                                                                   test_d_sqared < r ** 2, 3,
                                                                                   theoretical_slice)
                    if t_kills > kills:
                        min_z, max_z, kills = t_min_z, t_max_z, t_kills
                        d_sqared = test_d_sqared

            return min_z, max_z, d_sqared

        index_grid = np.indices(calcification_mask[0, :, :].shape)
        for i in range(0, len(pos_in_pixels)):
            min_index, max_index, d_sqared = optimize_kills_on_y_x_and_z(calcification_mask, 5, pos_in_pixels[i, 2],
                                                                         pos_in_pixels[i, 0], pos_in_pixels[i, 1])
            calcification_mask[min_index: max_index, :, :] = calcification_mask[min_index:max_index, :, :] * (
                    r ** 2 < d_sqared)

        return calcification_mask.astype(bool)

    def generate_topas_seed_string(self, photon_per_seed: int):
        all_sources_string = ""
        for sources in self.list_of_sources:
            all_sources_string = all_sources_string + sources.generate_sources_topas_string(photon_per_seed) + "\n\n"

        return all_sources_string + physics.LDR_BRACHY_PHYSICS

    def generate_whole_topas_input_file(self, total_particles: int, list_of_desired_structures, output_path,
                                        path_to_save_input_file=default_input_file_save_path,
                                        path_to_save_index=default_path_to_3d_index_mapping, add=""):
        total_seeds = 0
        for sources in self.list_of_sources:
            total_seeds += len(sources.positions)

        photon_per_seed = int(total_particles/total_seeds)
        if self.dosi_is_built and self.structures_are_built:
            full_input_file = self.generate_topas_seed_string(photon_per_seed) + "\n\n"
            full_input_file += self.structures.generate_topas_input_string_and_3d_mapping(list_of_desired_structures,
                                                                                          path_to_save_index) + "\n\n"
            full_input_file += self.dosimetry.generate_topas_scorer(output_path) + "\n\n" + add

            text_file = open(path_to_save_input_file, "w")
            text_file.write(full_input_file)
            text_file.close()

        else:
            logging.warning("Dosimetry or Structures not built")


class Sources:
    def __init__(self, source_isotope_name, air_kerma_rate, ref_date, ref_time, material, source_type,
                 source_manufacturer, source_diameter, source_lenght, positions, orientations, parent_plan):
        """

        :param source_isotope_name:
        :param air_kerma_rate:
        :param ref_date:
        :param ref_time:
        :param material:
        :param source_type:
        :param source_manufacturer:
        :param source_diameter:
        :param source_lenght:
        :param positions:
        :param orientations:
        :param parent_plan:
        """
        self.source_isotope_name = source_isotope_name
        self.air_kerma_rate = air_kerma_rate
        self.ref_date = ref_date
        self.ref_time = ref_time
        self.material = material
        self.source_type = source_type
        self.source_manufacturer = source_manufacturer
        self.parent_plan = parent_plan
        self.source_diameter = source_diameter
        self.source_lenght = source_lenght
        self.positions = positions
        self.orientations = orientations

    def generate_transformation_file_for_sources(self, new_file_path: str) -> None:
        """
        This method generates egs_brachy transformation file from
        the sources positions.

        :param new_file_path:
        :return:
        """
        pos = self.positions / 10
        orientation = self.orientations
        if orientation.shape[1] == 0:
            orientation = np.zeros((pos.shape[0], pos.shape[1]))

        vocab_file = open(new_file_path, "w")
        for i in range(0, pos.shape[0]):
            vocab_file.write(":start transformation: \n")
            vocab_file.write(f"translation = {pos[i, 0]} {pos[i, 1]} {pos[i, 2]} \n")
            vocab_file.write(f"rotation = {orientation[i, 0]} {orientation[i, 1]} {orientation[i, 2]} \n")
            vocab_file.write(":stop transformation:\n\n")

        vocab_file.close()

    def generate_sources_topas_string(self, photon_per_seed):
        """

        :param photon_per_seed:
        :return:
        """
        if self.source_manufacturer == "Nucletron B.V." and self.source_isotope_name == "I-125":
            sources_topas_string = selectseed.HEADER + "\n\n" + selectseed.MATERIALS
            for index in range(self.positions.shape[0]):
                sources_topas_string += "\n\n" + selectseed.SEEDS.substitute(index=index,
                                                                             photon_per_seed=photon_per_seed,
                                                                             position_x=self.positions[index][0],
                                                                             position_y=self.positions[index][1],
                                                                             position_z=self.positions[index][2])

            return sources_topas_string

        else:
            raise NotImplementedError










