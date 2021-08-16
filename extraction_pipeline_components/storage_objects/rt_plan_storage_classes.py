import logging

import numpy as np

from extraction_pipeline_components.contour_extraction_as_masks import extract_masks_for_each_organs_for_each_slices
from extraction_pipeline_components.utils.search_instance_and_convert_coord_in_pixel import find_instance_in_folder
from extraction_pipeline_components.storage_objects.rt_struct_storage_classes import Structures


class LDRBrachyPlan:
    def __init__(self, rt_plan_uid: str, rt_struct_uid: str, rt_dose_uid: str, rt_plan_date: str, rt_plan_time: float,
                 list_of_sources: list = None, structures: Structures = None):
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

        self.structures = structures
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

        logging.warning("Structures are already built")

    def extract_dosimetry(self):
        raise NotImplementedError

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


class Sources:
    def __init__(self, source_isotope_name, air_kerma_rate, ref_date, ref_time, material, source_type,
                 source_manufacturer, source_diameter, source_lenght, positions, orientations, parent_plan):
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

    def get_seperated_seed_positions(self):
        pass

    def convert_seed_positions_to_pixel(self):
        pass

    def get_actual_source_model(self):
        pass

    def get_source_spectrum(self):
        pass

    def generate_transformation_file_for_sources(self, new_file_path):
        pos = self.positions / 10
        orientation = self.orientations
        print(orientation.shape)
        if orientation.shape[1] == 0:
            orientation = np.zeros((pos.shape[0], pos.shape[1]))

        vocab_file = open(new_file_path, "w")
        print(orientation)
        for i in range(0, pos.shape[0]):
            vocab_file.write(":start transformation: \n")
            vocab_file.write(f"translation = {pos[i, 0]} {pos[i, 1]} {pos[i, 2]} \n")
            vocab_file.write(f"rotation = {orientation[i, 0]} {orientation[i, 1]} {orientation[i, 2]} \n")
            vocab_file.write(":stop transformation:\n\n")


        vocab_file.close()


