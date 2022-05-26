import logging
import os
from datetime import datetime
import pydicom
import numpy as np
from dicom_rt_context_extractor.utils.search_instance_and_convert_coord_in_pixel import find_modality_in_folder
from dicom_sr_builder.content_sequence_generator import TEXT_generator, CodeSequence_generator
from dicom_sr_builder.sr_builder import SRBuilder
from mcdose2dicom import create_rt_dose_from_scratch, adapt_rt_dose_to_existing_dicoms
from mcdose2dicom.adding_dvh import generate_and_add_all_dvh_to_dicom
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

    def _generate_sr(self, output_path, sr_item_list, path_to_ref, purpose_seq, file_name):
        content_sequence_items = []
        for content_sequence in sr_item_list:
            content_sequence_items.append(content_sequence.BuildDictionary())

        whole_content_sequence = {"ValueType": "CONTAINER",
                                  "ConceptNameCodeSequence": {"CodeValue": "100",
                                                              "CodingSchemeDesignator": "CUSTOM",
                                                              "CodeMeaning": "MC simulation parameters"},
                                  "ContinuityOfContent": "SEPERATE",
                                  "Value": content_sequence_items}

        sr_builder = SRBuilder(path_to_ref, purpose_seq)
        sr_builder.add_content_sequence(whole_content_sequence)
        sr_builder.build()
        sr_path = os.path.join(output_path, f"SR_{file_name}.dcm")
        sr_builder.save_sr_to(sr_path)

    def _3ddose_to_dicom(self, input_folder, output_path,
                         dicom_folder, image_position=None, image_orientation_patient=None,
                         to_dose_factor=1.0, sr_item_list=None, log_file=None):
        if image_position is None:
            image_position = [0, 0, 0]
        if image_orientation_patient is None:
            image_orientation_patient = [1, 0, 0, 0, 1, 0]

        output_3ddose_path = ""
        output_3ddose_file_name = ""
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".3ddose"):
                output_3ddose_path = os.path.join(input_folder, file_name)
                output_3ddose_file_name = file_name.replace(".3ddose", "")

        completed = False
        try:
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
            software = ""
            if hasattr(self, "software"):
                software = self.__getattribute__("software")
            bits_allocated = 16
            if hasattr(self, "bits_allocated"):
                bits_allocated = self.__getattribute__("bits_allocated")
            patient_orientation = ""
            if hasattr(self, "patient_orientation"):
                patient_orientation = self.__getattribute__("patient_orientation")
            dose_summation_type = "PLAN"
            if hasattr(self, "dose_summation_type"):
                dose_summation_type = self.__getattribute__("dose_summation_type")

            image_position = fr"{image_position[0]}\{image_position[1]}\{image_position[2]}"
            image_orientation_patient = fr"{image_orientation_patient[0]}\{image_orientation_patient[1]}\
                                       {image_orientation_patient[2]}\{image_orientation_patient[3]}\
                                       {image_orientation_patient[4]}\{image_orientation_patient[5]}"
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

            storing = self._store_in_dicom(output_path, dicom_folder, rt_dose, rt_dose_error,
                                           output_3ddose_file_name, to_dose_factor)
            complete = True
        except Exception as e:
            logging.error(e)

        finally:
            if completed:
                purpose = {"CodeValue": "6000", "CodingSchemeDesignator": "CUSTOM",
                           "CodeMeaning": "Method of acquisition"}
                file_name = output_3ddose_file_name
            else:
                now = datetime.now()
                purpose = {"CodeValue": "5000",
                           "CodingSchemeDesignator": "CUSTOM",
                           "CodeMeaning": "Attempted MC simulation"}
                file_name = f"{now.strftime('%Y%m%d')}_{now.strftime('%H%M%S')}"

            if hasattr(self, "generate_sr"):
                if self.generate_sr:
                    with open(log_file, 'r') as file:
                        logs_as_text = file.read()
                        print(logs_as_text)
                    sr_item_list.append(TEXT_generator("HAS ACQ CONTEXT", logs_as_text,
                                                       CodeSequence_generator("1000", "CUSTOM", "Logs")))
                    rt_plan_path = find_modality_in_folder("RTPLAN", dicom_folder)

                    self._generate_sr(output_path, sr_item_list, rt_plan_path, purpose,
                                      file_name)
            storing = output_path

        return storing

    def _binary_to_dicom(self, input_folder, output_path,
                         dicom_folder, image_position=None, image_orientation_patient=None,
                         to_dose_factor=1.0, sr_item_list=None):
        output_bin_path = ""
        output_bin_file_name = ""
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".bin"):
                output_bin_path = os.path.join(input_folder, file_name)
                output_bin_file_name = file_name.replace(".bin", "")
        try:
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
            software = ""
            if hasattr(self, "software"):
                software = self.__getattribute__("software")
            bits_allocated = 16
            if hasattr(self, "bits_allocated"):
                bits_allocated = self.__getattribute__("bits_allocated")
            patient_orientation = ""
            if hasattr(self, "patient_orientation"):
                patient_orientation = self.__getattribute__("patient_orientation")
            dose_summation_type = "PLAN"
            if hasattr(self, "dose_summation_type"):
                dose_summation_type = self.__getattribute__("dose_summation_type")

            image_position = fr"{image_position[0]}\{image_position[1]}\{image_position[2]}"
            image_orientation_patient = fr"{image_orientation_patient[0]}\{image_orientation_patient[1]}\
                                                   {image_orientation_patient[2]}\{image_orientation_patient[3]}\
                                                   {image_orientation_patient[4]}\{image_orientation_patient[5]}"
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

            storing = self._store_in_dicom(output_path, dicom_folder, rt_dose, rt_dose_error,
                                           output_bin_file_name, to_dose_factor)
            if hasattr(self, "generate_sr"):
                if self.generate_sr:
                    if hasattr(self, "generate_sr"):
                        if self.generate_sr:
                            rt_plan_path = find_modality_in_folder("RTPLAN", dicom_folder)
                            now = datetime.now()
                            self._generate_sr(output_path, sr_item_list, rt_plan_path, {"CodeValue": "5000",
                                                                                        "CodingSchemeDesignator": "CUSTOM",
                                                                                        "CodeMeaning": "Attempted MC "
                                                                                                       "simulation"},
                                              f"{now.strftime('%Y%m%d')}_{now.strftime('%H%M%S')}")
                    storing = output_path

        finally:
            if hasattr(self, "generate_sr"):
                if self.generate_sr:
                    rt_plan_path = find_modality_in_folder("RTPLAN", dicom_folder)
                    now = datetime.now()
                    self._generate_sr(output_path, sr_item_list, rt_plan_path, {"CodeValue": "5000",
                                                                                "CodingSchemeDesignator": "CUSTOM",
                                                                                "CodeMeaning": "Attempted MC simulation"},
                                      f"{now.strftime('%Y%m%d')}_{now.strftime('%H%M%S')}")
            storing = output_path

            return storing

    def _store_in_dicom(self, output_path, dicom_folder, dose: RTDoseBuilder, std: RTDoseBuilder, file_naming,
                        to_dose):
        path_to_rt_plan = find_modality_in_folder("RTPLAN", dicom_folder)
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

        error_saving_path = os.path.join(output_path, "error_" + file_naming + ".dcm")
        std.save_rt_dose_to(error_saving_path)
        adapt_rt_dose_to_existing_dicoms.adapt_rt_dose_to_existing_rt_plan(error_saving_path,
                                                                           path_to_rt_plan)

        path_updated_plan = os.path.join(output_path, "updated_plan_" + file_naming + ".dcm")
        adapt_rt_dose_to_existing_dicoms.add_reference_in_rt_plan(path_to_rt_plan, dose_saving_path,
                                                                  path_updated_plan)
        adapt_rt_dose_to_existing_dicoms.add_reference_in_rt_plan(path_updated_plan, error_saving_path)

        if hasattr(self, "generate_dvh"):
            if self.__getattribute__("generate_dvh"):
                self._generate_dvh(dose_saving_path, dicom_folder, to_dose)

        return output_path

    def clean_output(self, initial_file_type: str, input_folder, output_path,
                     dicom_folder, image_position=None, image_orientation_patient=None,
                     to_dose_factor=1.0, sr_item_list=None, log_file=None):
        assert initial_file_type in ["a3ddose", "binary"]
        if image_position is None:
            image_position = [0, 0, 0]
        if image_orientation_patient is None:
            image_orientation_patient = [1, 0, 0, 0, 1, 0]

        return self.__getattribute__(initial_file_type)(input_folder, output_path, dicom_folder, image_position,
                                                        image_orientation_patient, to_dose_factor, sr_item_list,
                                                        log_file)

    def _generate_dvh(self, dose_saving_path, dicom_folder, to_dose_factor):
        if hasattr(self, "use_updated_rt_struct"):
            if self.__getattribute__("use_updated_rt_struct"):
                dicom_folder = os.path.dirname(dose_saving_path)
        rt_struct_path = find_modality_in_folder("RTSTRUCT", dicom_folder)
        dvh_comment = "Generated from dycompyler-core "
        if hasattr(self, "dvh_comment"):
            dvh_comment += self.__getattribute__("dvh_comment")
        prescription_dose = 0
        if hasattr(self, "prescription_dose"):
            prescription_dose = self.__getattribute__("prescription_dose")
        dvh_normalization_point = [0, 0, 0]
        if hasattr(self, "dvh_normalization_point"):
            dvh_normalization_point = self.__getattribute__("dvh_normalization_point")
        dvh_interpolation_segments = 1
        if hasattr(self, "dvh_interpolation_segments"):
            dvh_interpolation_segments = self.__getattribute__("dvh_interpolation_segments")
        dvh_callback = None
        if hasattr(self, "dvh_callback"):
            dvh_callback = self.__getattribute__("dvh_callback")
        dvh_calculate_full_volume = False
        if hasattr(self, "dvh_calculate_full_volume"):
            dvh_calculate_full_volume = self.__getattribute__("dvh_calculate_full_volume")
        dvh_use_structure_extents = False
        if hasattr(self, "dvh_use_structure_extents"):
            dvh_use_structure_extents = self.__getattribute__("dvh_use_structure_extents")
        dvh_dose_limit = None
        if hasattr(self, "dvh_dose_limit"):
            dvh_use_structure_extents = self.__getattribute__("dvh_dose_limit")

        open_rt_dose = pydicom.dcmread(dose_saving_path)

        pixel_spacing = open_rt_dose.PixelSpacing
        generate_and_add_all_dvh_to_dicom(dose_saving_path, rt_struct_path, dvh_comment=dvh_comment,
                                          dose_scaling_factor=to_dose_factor,
                                          dose_type="PHYSICAL",
                                          contribution_type="INCLUDE",
                                          prescription_dose=prescription_dose,
                                          dvh_normalization_point=dvh_normalization_point,
                                          saving_path=None,
                                          limit=dvh_dose_limit,
                                          calculate_full_volume=dvh_calculate_full_volume,
                                          use_structure_extents=dvh_use_structure_extents,
                                          interpolation_resolution=(pixel_spacing[0] / dvh_interpolation_segments,
                                                                    pixel_spacing[1] / dvh_interpolation_segments),
                                          interpolation_segments_between_planes=dvh_interpolation_segments,
                                          thickness=None,
                                          callback=dvh_callback)
