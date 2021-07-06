import logging

from extraction_pipeline_components.contour_extraction_as_masks import extract_masks_for_each_organs_for_each_slices
from extraction_pipeline_components.utils.search_instance_and_convert_coord_in_pixel import find_instance_in_folder
from extraction_pipeline_components.storage_objects.rt_struct_storage_classes import Structures


class LDRBrachyPlan:
    def __init__(self, rt_struct_uid, rt_plan_date, rt_plan_time, list_of_sources=None, structures: Structures = None):
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

    def extract_structures(self, study_folder):
        if not self.structures_are_built:
            rt_struct_path = find_instance_in_folder(self.rt_struct_uid, study_folder)
            if rt_struct_path is None:
                logging.warning(f"RT STRUCT {self.rt_struct_uid} not found. The structures won't be built")
                self.structures = None

            structures = extract_masks_for_each_organs_for_each_slices(rt_struct_path, study_folder)
            self.structures = structures
            self.structures_are_built = True

        logging.warning("Structures are already built")

    def add_sources(self, sources) -> None:
        """
        This method adds one or many Masks to the
        mask list_of_masks.

        :param mask: Mask object or list of Mask objects
        :return: None
        """
        if type(sources) is list:
            self.list_of_sources.extend(sources)

        else:
            self.list_of_sources.append(sources)

    def get_structures(self):
        return self.structures


class Sources:
    def __init__(self, source_isotope_name, air_kerma_rate, ref_date, ref_time, material, positions, orientations,
                 parent_plan):
        self.source_isotope_name = source_isotope_name
        self.air_kerma_rate = air_kerma_rate
        self.ref_date = ref_date
        self.ref_time = ref_time
        self.material = material
        self.parent_plan = parent_plan

