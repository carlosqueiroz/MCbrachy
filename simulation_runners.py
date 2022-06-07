import logging
import os
import subprocess
from shutil import copy


class SimulationRunners:
    def __init__(self, **kwargs):
        """

        :param input_file_folder:
        :param kwargs: for egs_brachy, kwargs must have nb_treads (int), waiting_time (float) and
                       egs_brachy_home (str)
        """
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])

        self.topas = self._launch_topas
        self.egs_brachy = self._launch_egs_brachy

    def _launch_topas(self, input_folder: str, output_folder: str) -> str:
        input_file_path = ""
        for file_name in os.listdir(input_folder):
            if file_name.startswith("input"):
                input_file_path = os.path.join(input_folder, file_name)

        if hasattr(self, "nb_treads"):
            with open(input_file_path, 'a') as file:
                file.write(f"\ni:Ts/NumberOfThreads = {self.__getattribute__('nb_treads')}")
        bash_command = f"topas {input_file_path}"
        simulation = subprocess.run(bash_command.split(), capture_output=True, shell=True, executable='/bin/bash')
        self._log_subprocess_output(simulation.stdout)
        self._log_subprocess_output(simulation.stderr)

        return output_folder

    def _log_subprocess_output(self, pipe):
        for line in pipe.decode("utf-8").split("\n"):
            logging.info('got line from subprocess: %r', line)

    def _launch_egs_brachy(self, input_folder: str, output_folder: str) -> str:
        nb_treads = self.__getattribute__("nb_treads")
        waiting_time = self.__getattribute__("waiting_time")
        bash_command = fr"""egs-parallel -v -n {nb_treads} -f -d {waiting_time} -c"""
        input_file_path = ""
        input_name = ""
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".egsinp"):
                input_file_path = os.path.join(input_folder, file_name)
                input_name = file_name
        copy(input_file_path, os.path.join(self.__getattribute__("egs_brachy_home"), input_name))
        splited_bash = bash_command.split()
        file_name_no_ext = input_name.replace(".egsinp", "")
        splited_bash.append(fr"egs_brachy -i {file_name_no_ext}")
        simulation = subprocess.run(splited_bash, capture_output=True)
        self._log_subprocess_output(simulation.stdout)
        self._log_subprocess_output(simulation.stderr)
        copy(os.path.join(self.__getattribute__("egs_brachy_home"), f"{file_name_no_ext}.phantom.3ddose"),
             os.path.join(output_folder, f"{file_name_no_ext}.phantom.3ddose"))

        return output_folder

    def launch_simulation(self, code: str, input_folder: str, output_folder: str):
        assert code in ["topas", "egs_brachy"]
        return self.__getattribute__(code)(input_folder, output_folder)
