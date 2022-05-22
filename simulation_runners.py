import os
import subprocess
from shutil import copy


class SimulationRunners:
    def __init__(self, input_file_folder, **kwargs):
        """

        :param input_file_folder:
        :param kwargs: for egs_brachy, kwargs must have nb_treads (int), waiting_time (float) and
                       egs_brachy_home (str)
        """
        self.input_file_folder = input_file_folder
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])

        self.topas = self._launch_topas
        self.egs_brachy = self._launch_egs_brachy

    def _launch_topas(self, output_folder: str) -> str:
        input_file_path = ""
        for file_name in os.listdir(self.input_file_folder):
            if file_name.startswith("input"):
                input_file_path = os.path.join(self.input_file_folder, file_name)
            bash_command = f"topas {input_file_path}"
            simulation = subprocess.run(bash_command.split())

            return output_folder

    def _launch_egs_brachy(self, output_folder: str) -> str:
        nb_treads = self.__getattribute__("nb_treads")
        waiting_time = self.__getattribute__("waiting_time")
        bash_command = fr"""egs-parallel -v -n {nb_treads} -f -d {waiting_time} -c"""
        input_file_path = ""
        input_name = ""
        for file_name in os.listdir(self.input_file_folder):
            if file_name.endswith(".egsinp"):
                input_file_path = os.path.join(self.input_file_folder, file_name)
                input_name = file_name
        copy(input_file_path, os.path.join(self.__getattribute__("egs_brachy_home"), input_name))
        splited_bash = bash_command.split()
        file_name_no_ext = input_name.removesuffix(r".egsinp")
        splited_bash.append(fr"egs_brachy -i {file_name_no_ext}")
        simulation = subprocess.run(splited_bash)
        copy(os.path.join(self.__getattribute__("egs_brachy_home"), f"{file_name_no_ext}.phantom.3ddose"),
             os.path.join(output_folder, f"{file_name_no_ext}.phantom.3ddose"))

        return output_folder

    def launch_simulation(self, code: str, output_folder: str):
        assert code in ["topas", "egs_brachy"]
        self.__getattribute__(code)(output_folder)
