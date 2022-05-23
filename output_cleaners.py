import os
import numpy as np
from mcdose2dicom import create_rt_dose_from_scratch, adapt_rt_dose_to_existing_dicoms, adding_dvh
from mcdose2dicom.create_rt_dose_from_scratch import RTDoseBuilder
from py3ddose.py3ddose import DoseFile
from topas2numpy import BinnedResult


class OutputCleaners:
    def __init__(self, **kwargs):
        """

        :param input_file_folder:
        :param kwargs: dose_comments (str)
                       software (str)
                       grid_position (str)
                       grid_orientation (str)
                       to_dose_factor (float)
                       "series_description" (str)
        """
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])

        self.a3ddose = self._3ddose_to_dicom
        self.binary = self._binary_to_dicom

    def _3ddose_to_dicom(self, input_folder, output_path, path_to_rt_plan):
        output_3ddose_path = ""
        output_3ddose_file_name = ""
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".3ddose"):
                output_3ddose_path = os.path.join(input_folder, file_name)
                output_3ddose_file_name = file_name.replace(".3ddose", "")

        open_3ddose = DoseFile(output_3ddose_path, load_uncertainty=True)
        dose_data = np.flip(open_3ddose.dose, axis=0)
        std_data = np.flip(open_3ddose.uncertainty, axis=0)
        factor_from_cm_to_mm = 10
        voxel_size = (factor_from_cm_to_mm * open_3ddose.spacing[2][0],
                      factor_from_cm_to_mm * open_3ddose.spacing[1][0],
                      factor_from_cm_to_mm * open_3ddose.spacing[0][0])
        dose_comment = ""
        if hasattr(self, "dose_comment"):
            dose_comment = self.__getattribute__("dose_comment")
        to_dose_factor = 1.0
        if hasattr(self, "dose_comment"):
            to_dose_factor = self.__getattribute__("to_dose_factor")
        software = ""
        if hasattr(self, "software"):
            software = self.__getattribute__("software")
        image_position = r'0\0\0'
        if hasattr(self, "image_position"):
            image_position = self.__getattribute__("image_position")
        image_orientation_patient = r'1\0\0\0\1\0'
        if hasattr(self, "image_orientation_patient"):
            image_orientation_patient = self.__getattribute__("image_orientation_patient")
        bits_allocated = 16
        if hasattr(self, "bits_allocated"):
            bits_allocated = self.__getattribute__("bits_allocated")
        patient_orientation = ""
        if hasattr(self, "patient_orientation"):
            patient_orientation = self.__getattribute__("patient_orientation")
        dose_summation_type = "PLAN"
        if hasattr(self, "dose_summation_type"):
            dose_summation_type = self.__getattribute__("dose_summation_type")

        dose_comment += f" Factor from dose/histories to total dose = {to_dose_factor}"
        rt_dose = create_rt_dose_from_scratch.RTDoseBuilder(dose_grid_scaling=to_dose_factor,
                                                            dose_type="PHYSICAL", dose_comment=dose_comment,
                                                            software=software, dose_units="GY",
                                                            bits_allocated=bits_allocated,
                                                            dose_summation_type=dose_summation_type,
                                                            image_orientation_patient=image_orientation_patient,
                                                            image_position_patient=image_position,
                                                            patient_orientation=patient_orientation)
        rt_dose.add_dose_grid(dose_data, voxel_size, True, True)
        rt_dose.build()

        rt_dose_error = create_rt_dose_from_scratch.RTDoseBuilder(dose_grid_scaling=to_dose_factor,
                                                                  dose_type="ERROR", dose_comment=dose_comment,
                                                                  software=software, dose_units="GY",
                                                                  bits_allocated=bits_allocated,
                                                                  dose_summation_type=dose_summation_type,
                                                                  image_orientation_patient=image_orientation_patient,
                                                                  image_position_patient=image_position,
                                                                  patient_orientation=patient_orientation)
        rt_dose_error.add_dose_grid(std_data, voxel_size, True, True)
        rt_dose_error.build()

        storing = self._store_in_dicom(output_path, path_to_rt_plan, rt_dose, rt_dose_error, output_3ddose_file_name)

        return storing

    def _binary_to_dicom(self, input_folder, output_path, path_to_rt_plan):
        output_bin_path = ""
        output_bin_file_name = ""
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".bin"):
                output_bin_path = os.path.join(input_folder, file_name)
                output_bin_file_name = file_name.replace(".bin", "")

        open_bin = BinnedResult(output_bin_path)
        dose_data = np.flip(open_bin.data["Sum"], axis=0)
        std_data = np.flip(open_bin.data['Standard_Deviation'], axis=0)
        factor_from_cm_to_mm = 10
        voxel_size = (open_bin.dimensions[0].bin_width * factor_from_cm_to_mm,
                      open_bin.dimensions[1].bin_width * factor_from_cm_to_mm,
                      open_bin.dimensions[2].bin_width * factor_from_cm_to_mm)
        dose_comment = ""
        if hasattr(self, "dose_comment"):
            dose_comment = self.__getattribute__("dose_comment")
        to_dose_factor = 1.0
        if hasattr(self, "to_dose_factor"):
            to_dose_factor = self.__getattribute__("to_dose_factor")
        software = ""
        if hasattr(self, "software"):
            software = self.__getattribute__("software")
        image_position = r'0\0\0'
        if hasattr(self, "image_position"):
            image_position = self.__getattribute__("image_position")
        image_orientation_patient = r'1\0\0\0\1\0'
        if hasattr(self, "image_orientation_patient"):
            image_orientation_patient = self.__getattribute__("image_orientation_patient")
        bits_allocated = 16
        if hasattr(self, "bits_allocated"):
            bits_allocated = self.__getattribute__("bits_allocated")
        patient_orientation = ""
        if hasattr(self, "patient_orientation"):
            patient_orientation = self.__getattribute__("patient_orientation")
        dose_summation_type = "PLAN"
        if hasattr(self, "dose_summation_type"):
            dose_summation_type = self.__getattribute__("dose_summation_type")

        dose_comment += f" Factor from dose/histories to total dose = {to_dose_factor}"
        rt_dose = create_rt_dose_from_scratch.RTDoseBuilder(dose_grid_scaling=to_dose_factor,
                                                            dose_type="PHYSICAL", dose_comment=dose_comment,
                                                            software=software, dose_units="GY",
                                                            bits_allocated=bits_allocated,
                                                            dose_summation_type=dose_summation_type,
                                                            image_orientation_patient=image_orientation_patient,
                                                            image_position_patient=image_position,
                                                            patient_orientation=patient_orientation)
        rt_dose.add_dose_grid(dose_data, voxel_size, True, True)
        rt_dose.build()

        rt_dose_error = create_rt_dose_from_scratch.RTDoseBuilder(dose_grid_scaling=to_dose_factor,
                                                                  dose_type="ERROR", dose_comment=dose_comment,
                                                                  software=software, dose_units="GY",
                                                                  bits_allocated=bits_allocated,
                                                                  dose_summation_type=dose_summation_type,
                                                                  image_orientation_patient=image_orientation_patient,
                                                                  image_position_patient=image_position,
                                                                  patient_orientation=patient_orientation)
        rt_dose_error.add_dose_grid(std_data, voxel_size, True, True)
        rt_dose_error.build()

        storing = self._store_in_dicom(output_path, path_to_rt_plan, rt_dose, rt_dose_error, output_bin_file_name)

        return storing

    def _store_in_dicom(self, output_path, path_to_rt_plan, dose: RTDoseBuilder, std: RTDoseBuilder, file_naming):
        if hasattr(self, "series_description"):
            dose.rt_dose.SeriesDescription = self.__getattribute__("series_description")
        std.rt_dose.SeriesDescription = dose.rt_dose.SeriesDescription
        std.rt_dose.SeriesInstanceUID = dose.rt_dose.SeriesInstanceUID
        std.rt_dose.SeriesNumber = dose.rt_dose.SeriesNumber
        std.rt_dose.InstanceNumber = dose.rt_dose.InstanceNumber + 1

        dose_saving_path = os.path.join(output_path, "dose_" + file_naming + ".dcm")
        dose.save_rt_dose_to(dose_saving_path)
        adapt_rt_dose_to_existing_dicoms.adapt_rt_dose_to_existing_rt_plan(dose_saving_path,
                                                                           path_to_rt_plan)

        # TODO generate dvh
        if hasattr(self, "generate_dvh"):
            if self.__getattribute__("generate_dvh"):
                pass

        error_saving_path = os.path.join(output_path, "error_" + file_naming + ".dcm")
        std.save_rt_dose_to(error_saving_path)
        adapt_rt_dose_to_existing_dicoms.adapt_rt_dose_to_existing_rt_plan(error_saving_path,
                                                                           path_to_rt_plan)

        path_updated_plan = os.path.join(output_path, "updated_plan_" + file_naming + ".dcm")
        adapt_rt_dose_to_existing_dicoms.add_reference_in_rt_plan(path_to_rt_plan, dose_saving_path,
                                                                  path_updated_plan)
        adapt_rt_dose_to_existing_dicoms.add_reference_in_rt_plan(path_updated_plan, error_saving_path)

        return output_path

    def clean_output(self, initial_file_type: str, input_folder, output_path, path_to_rt_plan):
        assert initial_file_type in ["a3ddose", "binary"]
        return self.__getattribute__(initial_file_type)(input_folder, output_path, path_to_rt_plan)
