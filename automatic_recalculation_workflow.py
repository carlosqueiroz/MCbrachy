# Copyright (C) 2023 Samuel Ouellet and Luc Beaulieu

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


import logging.config
import os
import sys
import numpy as np
from dicom_rt_context_extractor.utils.dicom_folder_structurer import restructure_dicom_folder, destructure_folder
from components.simulation_runners import SimulationRunners
from components.output_cleaners import OutputCleaners
from components.input_file_generators import InputFileGenerators
from components.extractors import DicomExtractors

TOPAS_MATERIAL_CONVERTER = {"prostate": "TG186Prostate",
                            "vessie": "TG186MeanMaleSoftTissue",
                            "rectum": "ICRPRectum",
                            "uretre": "TG186MeanMaleSoftTissue",
                            "Bladder Neck": "TG186MeanMaleSoftTissue",
                            "prostate_calcification": "CALCIFICATION_ICRU46"}

EGS_BRACHY_MATERIAL_CONVERTER = {"prostate": "PROSTATE_WW86",
                                 "vessie": "URINARY_BLADDER_EMPTY",
                                 "rectum": "AIR_TG43",
                                 "uretre": "URETHRA_WW86",
                                 "Bladder Neck": "URINARY_BLADDER_EMPTY",
                                 "prostate_calcification": "CALCIFICATION_ICRU46"}
# EGS_BRACHY_MATERIAL_CONVERTER = {"prostate": "WATER_1.000",
#                                  "vessie": "WATER_1.000",
#                                  "rectum": "WATER_1.000",
#                                  "uretre": "WATER_1.000",
#                                  "Bladder Neck": "WATER_1.000",
#                                  "prostate_calcification": "WATER_1.000"}

# ["prostate", "vessie", "rectum", "uretre", "prostate_calcification"]
if __name__ == "__main__":
    ORGANS_TO_USE, RESTRUCTURING_FOLDERS, NUMBER_OF_PARTICLES = (["prostate", "vessie", "rectum", "uretre", "prostate_calcification"], False, 1e5)
    #-------------------- input, output --------------------
    PATIENTS_DIRECTORY = sys.argv[-2]
    OUTPUT_PATH = sys.argv[-1]
    #-------------------- Selecting component types --------------------
    extractor_selected = "permanent_implant_brachy"
    input_file_generator_selected = "topas_permanent_implant_brachy"
    runner_selected = "topas"
    output_file_format = "binary"
    #-------------------- Additional DICOM files --------------------
    generate_sr = True
    recreate_struct_with_simulation_geometry = True

    #-------------------- Simulation setup parameters --------------------
    reproduce_tg43_dose_grid = False  # Set to true only for egs_brachy
    custom_grid = {"scorer_origin": np.asarray([0, 0, 0]), "pixel_spacing": np.asarray([0.75, 0.5, 1]),
                   "shape": np.asarray([130, 160, 128])}  # only for TOPAS
    set_custom_grid_based_on_organ_location = True, "prostate" # only for TOPAS
    ct_calibration_curve = np.asarray([[-3025, 0.001],
                                       [-1000, 0.001],
                                       [0, 1.008],
                                       [61.9, 1.073],
                                       [1000, 1.667],
                                       [2000, 2.300],
                                       [3000, 2.933],
                                       [3100, 2.999],
                                       [5000, 2.999],
                                       [10000, 7.365],
                                       [20000, 10.000],
                                       [25000, 10.000]])

    series_description = "Test_series_description"
    #-------------------- Building components with their parameter--------------------
    # even if some parameters are not needed in some cases, they are left to serve as reference
    dicom_extractor = DicomExtractors(segmentation=["prostate_calcifications"], build_structures=True,
                                      recreate_struct=recreate_struct_with_simulation_geometry, series_description=series_description)
    input_file_generator = InputFileGenerators(total_particles=NUMBER_OF_PARTICLES,
                                               run_mode="normal", # EGS_BRACHY ONLY "normal" for TG186 and "superposition" for TG43
                                               list_of_desired_structures=ORGANS_TO_USE,
                                               crop_to_contour_margin=20, # Margin to add to the contour when cropping in mm
                                               material_attribution_dict=TOPAS_MATERIAL_CONVERTER, #Set Material to use here
                                               egs_brachy_home=r'/EGSnrc_CLRP/egs_home/egs_brachy',#EGS_BRACHY ONLY path to egs_brachy folder
                                               batches=1,
                                               chunk=1,
                                               add="",
                                               generate_sr=generate_sr,
                                               crop=True, # Weither to crop CT to structures or not
                                               expand_tg45_phantom=500,
                                               code_version="3.9",
                                               topas_output_type="binary",
                                               ct_calibration_curve=ct_calibration_curve,
                                               custom_dose_grid=custom_grid)

    nb_of_threads = 2
    simulation_runner = SimulationRunners(nb_treads=nb_threads, waiting_time=30, #See egsNRC documentation for more details on parrallelization runs
                                          egs_brachy_home=r'/EGSnrc_CLRP/egs_home/egs_brachy')

    output_cleaner = OutputCleaners(
        software="Systematic MC recalculation Workflow V0.5: DL training commit: ***",
        dose_summation_type="PLAN",
        patient_orientation="",
        bits_allocated=16, # Resolution of dosegrid values
        series_description=series_description,
        generate_dvh=True, # Whether to generate DVH or not
        generate_sr=generate_sr,
        dvh_calculate_full_volume=False,
        dvh_use_structure_extents=False,
        dvh_comment="Generated by dicompyler-core",
        dvh_normalization_point=[0, 0, 0],
        dvh_interpolation_segments=2,
        dvh_dose_limit=60000,
        prescription_dose=144,
        use_updated_rt_struct=True) # Whether to use updated RT struct or not


    #-------------------- Running the pipeline--------------------
    for patient in os.listdir(PATIENTS_DIRECTORY):
        patient_folder_path = os.path.join(PATIENTS_DIRECTORY, patient)
        if RESTRUCTURING_FOLDERS:
            restructure_dicom_folder(patient_folder_path, patient_folder_path)

        for studies in os.listdir(patient_folder_path):
            study_path = os.path.join(patient_folder_path, studies)
            simulation_files_path = os.path.join(OUTPUT_PATH, f"simulation_files_{patient}_{studies}".replace(" ", "_"))
            os.mkdir(simulation_files_path)
            final_output_folder = os.path.join(OUTPUT_PATH, f"final_output_{patient}_{studies}".replace(" ", "_"))
            os.mkdir(final_output_folder)
            log_file = os.path.join(simulation_files_path, "logs.logs")
            logging.basicConfig(handlers=[logging.FileHandler(log_file), logging.StreamHandler()], level=logging.INFO,
                                format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                                datefmt='%H:%M:%S')
            plan = dicom_extractor.extract_context_from_dicoms(extractor_selected, study_path, final_output_folder)
            if set_custom_grid_based_on_organ_location[0]:
                center_of_organ = plan.structures.get_specific_mask(set_custom_grid_based_on_organ_location[1],
                                                                    set_custom_grid_based_on_organ_location[
                                                                        1]).get_mask_center()

                if custom_grid is None:
                    ct_shape = plan.structures.get_specific_mask(set_custom_grid_based_on_organ_location[1],
                                                                 set_custom_grid_based_on_organ_location[
                                                                     1]).get_3d_mask().shape
                    input_file_generator.reset_custom_grid({"pixel_spacing": plan.structures.z_y_x_spacing,
                                                            "shape": ct_shape,
                                                            "scorer_origin": center_of_organ})
                else:
                    custom_grid["scorer_origin"] = center_of_organ
                    input_file_generator.reset_custom_grid(custom_grid)

            try:
                sim_files_folder, meta_data_dict, all_sr_sequence = input_file_generator.generate_input_files(
                    input_file_generator_selected,
                    plan, simulation_files_path)
            except NotImplementedError:
                logging.warning("This study has been ignored because seed model is not implemented")
                break

            output_folder = simulation_runner.launch_simulation(runner_selected, sim_files_folder,
                                                                simulation_files_path)
            image_position = np.asarray([0, 0, 0], dtype=np.float64)
            if plan.structures_are_built and not reproduce_tg43_dose_grid:
                image_position = np.asarray(plan.structures.x_y_z_origin)
            if "image_position_offset" in meta_data_dict.keys():
                image_position += np.asarray(meta_data_dict["image_position_offset"])

            image_orientation_patient = np.asarray([1, 0, 0, 0, 1, 0],
                                                   dtype=np.float64)
            if plan.structures_are_built and not reproduce_tg43_dose_grid:
                image_orientation_patient = np.asarray(plan.structures.x_y_z_rotation_vectors)
            if "image_orientation_patient_offset" in meta_data_dict.keys():
                image_orientation_patient += np.asarray(meta_data_dict["image_orientation_patient_offset"])

            to_dose_factor = plan.dose_factor
            if "dose_factor_offset" in meta_data_dict.keys():
                to_dose_factor = to_dose_factor * meta_data_dict["dose_factor_offset"]
                if "topas" == runner_selected:
                    to_dose_factor = to_dose_factor / (NUMBER_OF_PARTICLES * nb_of_threads)
            flipped = False
            if "flipped" in meta_data_dict.keys():
                flipped = "flipped"

            final_output_path = output_cleaner.clean_output(output_file_format, output_folder, final_output_folder,
                                                            study_path, image_position=image_position,
                                                            image_orientation_patient=image_orientation_patient,
                                                            to_dose_factor=to_dose_factor, sr_item_list=all_sr_sequence,
                                                            log_file=log_file, flipped=flipped)
            # shutil.rmtree(simulation_files_path) # Uncomment to delete simulation files after processing

        if RESTRUCTURING_FOLDERS:
            destructure_folder(patient_folder_path)
