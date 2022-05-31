import os
from typing import Tuple

from egs_brachy_file_generator.generate_permanent_implant_brachy_input import generate_whole_egs_brachy_input_file
from egs_brachy_file_generator.generate_permanent_implant_tg43_brachy_input import \
    generate_whole_egs_brachy_tg43_input_file


class InputFileGenerators:
    def __init__(self, **kwargs):
        """

        :param input_file_folder:
        :param kwargs: for egs_brachy, kwargs must have nb_treads (int), waiting_time (float) and
                       egs_brachy_home (str)
        """
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])

        self.topas_permanent_implant_brachy = self._genrerate_topas_permanent_implant_brachy_input_files
        self.egs_brachy_permanent_implant_brachy = self._genrerate_egs_brachy_permanent_implant_brachy_input_files
        self.egs_brachy_permanent_tg43_implant_brachy = self._genrerate_egs_brachy_permanent_implant_tg43_brachy_input_files
        self.topas_hdr_brachy = self._genrerate_topas_hdr_brachy_input_files
        self.topas_ldr_brachy = self._genrerate_topas_ldr_brachy_input_files
        self.egs_brachy_ldr_brachy = self._genrerate_egs_brachy_ldr_brachy_input_files

    def _genrerate_topas_permanent_implant_brachy_input_files(self, plan, output_folder: str):
        pass

    def _genrerate_egs_brachy_permanent_implant_brachy_input_files(self, plan, output_folder: str) -> Tuple:
        total_particles = self.__getattribute__("total_particles")
        list_of_desired_structures = self.__getattribute__("list_of_desired_structures")
        material_attribution_dict = self.__getattribute__("material_attribution_dict")
        path_to_transform_file = os.path.join(output_folder, f"transformation_file_{plan.patient}_{plan.study}")
        path_to_save_input_file = os.path.join(output_folder, f"input_{plan.patient}_{plan.study}.egsinp")
        egs_brachy_home = self.__getattribute__("egs_brachy_home")
        egs_phant_file_path = os.path.join(output_folder, f"egs_phant_{plan.patient}_{plan.study}.egsphant")
        if hasattr(self, "batches"):
            batches = self.__getattribute__("batches")
        else:
            batches = 1
        if hasattr(self, "chunk"):
            chunk = self.__getattribute__("chunk")
        else:
            chunk = 1
        if hasattr(self, "add"):
            add = self.__getattribute__("add")
        else:
            add = ""
        if hasattr(self, "generate_sr"):
            generate_sr = self.__getattribute__("generate_sr")
        else:
            generate_sr = False
        if hasattr(self, "crop"):
            crop = self.__getattribute__("crop")
        else:
            crop = False
        if hasattr(self, "code_version"):
            code_version = self.__getattribute__("code_version")
        else:
            code_version = ""

        meta_data_dict, all_sr_sequence = generate_whole_egs_brachy_input_file(plan, total_particles,
                                                                               list_of_desired_structures,
                                                                               material_attribution_dict,
                                                                               path_to_transform_file,
                                                                               path_to_save_input_file,
                                                                               egs_brachy_home, egs_phant_file_path,
                                                                               batches, chunk, add,
                                                                               generate_sr, crop, code_version)

        return output_folder, meta_data_dict, all_sr_sequence

    def _genrerate_egs_brachy_permanent_implant_tg43_brachy_input_files(self, plan, output_folder: str) -> Tuple:
        total_particles = self.__getattribute__("total_particles")
        path_to_transform_file = os.path.join(output_folder, f"transformation_file_{plan.patient}_{plan.study}")
        path_to_save_input_file = os.path.join(output_folder, f"input_{plan.patient}_{plan.study}.egsinp")
        egs_brachy_home = self.__getattribute__("egs_brachy_home")
        egs_phant_file_path = os.path.join(output_folder, f"egs_phant_{plan.patient}_{plan.study}.egsphant")
        if hasattr(self, "batches"):
            batches = self.__getattribute__("batches")
        else:
            batches = 1
        if hasattr(self, "chunk"):
            chunk = self.__getattribute__("chunk")
        else:
            chunk = 1
        if hasattr(self, "add"):
            add = self.__getattribute__("add")
        else:
            add = ""
        if hasattr(self, "generate_sr"):
            generate_sr = self.__getattribute__("generate_sr")
        else:
            generate_sr = False
        if hasattr(self, "expand_tg45_phantom"):
            expand_tg45_phantom = self.__getattribute__("expand_tg45_phantom")
        else:
            expand_tg45_phantom = 20
        if hasattr(self, "code_version"):
            code_version = self.__getattribute__("code_version")
        else:
            code_version = ""

        meta_data_dict, all_sr_sequence = generate_whole_egs_brachy_tg43_input_file(plan, total_particles,
                                                                                    path_to_transform_file,
                                                                                    path_to_save_input_file,
                                                                                    egs_brachy_home,
                                                                                    egs_phant_file_path,
                                                                                    batches, chunk, add,
                                                                                    expand_tg45_phantom,
                                                                                    generate_sr, code_version)

        return output_folder, meta_data_dict, all_sr_sequence

    def _genrerate_topas_hdr_brachy_input_files(self, plan, output_folder: str) -> str:
        pass

    def _genrerate_topas_ldr_brachy_input_files(self, plan, output_folder: str) -> str:
        pass

    def _genrerate_egs_brachy_ldr_brachy_input_files(self, plan, output_folder: str):
        pass

    def _produce_associated_SR(self):
        pass

    def generate_input_files(self, generator: str, plan, output_path):
        assert generator in ["topas_permanent_implant_brachy", "egs_brachy_permanent_implant_brachy",
                             "topas_hdr_brachy", "topas_ldr_brachy", "egs_brachy_ldr_brachy",
                             "egs_brachy_permanent_tg43_implant_brachy"]
        return self.__getattribute__(generator)(plan, output_path)
