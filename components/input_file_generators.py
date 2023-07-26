import os
from typing import Tuple

from egs_brachy_file_generator.generate_permanent_implant_brachy_input import generate_whole_egs_brachy_input_file
from egs_brachy_file_generator.generate_permanent_implant_tg43_brachy_input import \
    generate_whole_egs_brachy_tg43_input_file
from topas_file_generator.generate_topas_input_from_dicom_extractor import generate_whole_topas_input_file, \
    generate_whole_tg43_permanent_implant_topas_input_file

from root import ROOT


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
        self.topas_permanent_tg43_implant_brachy = self._genrerate_topas_permanent_tg43_implant_brachy_input_files
        self.egs_brachy_permanent_implant_brachy = self._genrerate_egs_brachy_permanent_implant_brachy_input_files
        self.egs_brachy_permanent_tg43_implant_brachy = self._genrerate_egs_brachy_permanent_implant_tg43_brachy_input_files
        self.topas_hdr_brachy = self._genrerate_topas_hdr_brachy_input_files
        self.topas_ldr_brachy = self._genrerate_topas_ldr_brachy_input_files
        self.egs_brachy_ldr_brachy = self._genrerate_egs_brachy_ldr_brachy_input_files

    def reset_custom_grid(self, custom_grid):
        self.__setattr__("custom_dose_grid", custom_grid)

    def _genrerate_topas_permanent_tg43_implant_brachy_input_files(self, plan, output_folder: str):
        total_particles = self.__getattribute__("total_particles")
        frequence_of_print = f"i:Ts/ShowHistoryCountAtInterval = {int(total_particles // 100)}"
        path_to_save_input_file = os.path.join(output_folder, f"input_{plan.patient}_{plan.study}.txt")
        muen_path = os.path.join(ROOT, "simulation_files", "Muen.dat")
        output_path = os.path.join(output_folder, f"dose_{plan.patient}_{plan.study}")
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
            code_version = "3.9"
        if hasattr(self, "topas_output_type"):
            topas_output_type = self.__getattribute__("topas_output_type")
        else:
            topas_output_type = "binary"
        if hasattr(self, "custom_dose_grid"):
            custom_dose_grid = self.__getattribute__("custom_dose_grid")
        else:
            custom_dose_grid = None
        meta_data_dict, all_sr_sequence = generate_whole_tg43_permanent_implant_topas_input_file(plan, int(total_particles),
                                                                                output_path,
                                                                                path_to_save_input_file,
                                                                                topas_output_type,
                                                                                muen_path,
                                                                                add=frequence_of_print + add,
                                                                                custom_dose_grid=custom_dose_grid,
                                                                                generate_sr=generate_sr,
                                                                                code_version=code_version)

        return output_folder, meta_data_dict, all_sr_sequence

    def _genrerate_topas_permanent_implant_brachy_input_files(self, plan, output_folder: str):
        total_particles = self.__getattribute__("total_particles")
        frequence_of_print = f"i:Ts/ShowHistoryCountAtInterval = {int(total_particles // 100)}\n"
        list_of_desired_structures = self.__getattribute__("list_of_desired_structures")
        material_attribution_dict = self.__getattribute__("material_attribution_dict")
        path_to_save_input_file = os.path.join(output_folder, f"input_{plan.patient}_{plan.study}.txt")
        path_to_save_3d_index = os.path.join(output_folder, f"index_3d_{plan.patient}_{plan.study}.bin")
        muen_path = os.path.join(ROOT, "simulation_files", "Muen.dat")
        output_path = os.path.join(output_folder, f"dose_{plan.patient}_{plan.study}")
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
            code_version = "3.9"
        if hasattr(self, "topas_output_type"):
            topas_output_type = self.__getattribute__("topas_output_type")
        else:
            topas_output_type = "binary"
        if hasattr(self, "custom_dose_grid"):
            custom_dose_grid = self.__getattribute__("custom_dose_grid")
        else:
            custom_dose_grid = None
        meta_data_dict, all_sr_sequence = generate_whole_topas_input_file(plan, int(total_particles),
                                                         list_of_desired_structures,
                                                         material_attribution_dict,
                                                         output_path,
                                                         path_to_save_input_file,
                                                         path_to_save_3d_index,
                                                         topas_output_type,
                                                         muen_path,
                                                         add=frequence_of_print + add,
                                                         crop=crop, custom_dose_grid=custom_dose_grid,
                                                                          code_version=code_version)

        return output_folder, meta_data_dict, all_sr_sequence

    def _genrerate_egs_brachy_permanent_implant_brachy_input_files(self, plan, output_folder: str) -> Tuple:
        total_particles = self.__getattribute__("total_particles")
        list_of_desired_structures = self.__getattribute__("list_of_desired_structures")
        material_attribution_dict = self.__getattribute__("material_attribution_dict")
        path_to_transform_file = os.path.join(output_folder,
                                              f"transformation_file_{plan.patient}_{plan.study}".replace(" ", "_"))
        path_to_save_input_file = os.path.join(output_folder,
                                               f"input_{plan.patient}_{plan.study}.egsinp".replace(" ", "_"))
        egs_brachy_home = self.__getattribute__("egs_brachy_home")
        egs_phant_file_path = os.path.join(output_folder,
                                           f"egs_phant_{plan.patient}_{plan.study}.egsphant".replace(" ", "_"))
        if hasattr(self, "ct_calibration_curve"):
            ct_calibration_curve = self.ct_calibration_curve
        else:
            ct_calibration_curve = None
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
        if hasattr(self, "run_mode"):
            run_mode = self.__getattribute__("run_mode")
        else:
            run_mode = "normal"

        meta_data_dict, all_sr_sequence = generate_whole_egs_brachy_input_file(plan, total_particles,
                                                                               list_of_desired_structures,
                                                                               material_attribution_dict,
                                                                               path_to_transform_file,
                                                                               path_to_save_input_file,
                                                                               egs_brachy_home, egs_phant_file_path,
                                                                               run_mode, batches, chunk, add,
                                                                               generate_sr, crop, ct_calibration_curve,
                                                                               code_version)

        return output_folder, meta_data_dict, all_sr_sequence

    def _genrerate_egs_brachy_permanent_implant_tg43_brachy_input_files(self, plan, output_folder: str) -> Tuple:
        total_particles = self.__getattribute__("total_particles")
        path_to_transform_file = os.path.join(output_folder,
                                              f"transformation_file_{plan.patient}_{plan.study}".replace(" ", "_"))
        path_to_save_input_file = os.path.join(output_folder,
                                               f"input_{plan.patient}_{plan.study}.egsinp".replace(" ", "_"))
        egs_brachy_home = self.__getattribute__("egs_brachy_home")
        egs_phant_file_path = os.path.join(output_folder,
                                           f"egs_phant_{plan.patient}_{plan.study}.egsphant".replace(" ", "_"))
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
                                                                                    generate_sr, code_version, True)

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
                             "egs_brachy_permanent_tg43_implant_brachy", "topas_permanent_tg43_implant_brachy"]
        return self.__getattribute__(generator)(plan, output_path)
