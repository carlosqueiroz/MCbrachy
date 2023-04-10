import getopt
import logging.config
import os
import shutil
import sys
import numpy as np
from dicom_rt_context_extractor.utils.dicom_folder_structurer import restructure_dicom_folder, destructure_folder
from components.simulation_runners import SimulationRunners
from components.output_cleaners import OutputCleaners
from components.input_file_generators import InputFileGenerators
from components.extractors import DicomExtractors
from root import ROOT

TOPAS_MATERIAL_CONVERTER = {"prostate": "TG186Prostate",
                            "vessie": "TG186MeanMaleSoftTissue",
                            "rectum": "Air",
                            "uretre": "TG186MeanMaleSoftTissue",
                            "Bladder Neck": "TG186MeanMaleSoftTissue",
                            "calcification": "CALCIFICATION_ICRU46"}

# EGS_BRACHY_MATERIAL_CONVERTER = {"prostate": "PROSTATE_WW86",
#                                  "vessie": "URINARY_BLADDER_EMPTY",
#                                  "rectum": "AIR_TG43",
#                                  "uretre": "URETHRA_WW86",
#                                  "Bladder Neck": "URINARY_BLADDER_EMPTY",
#                                  "prostate_calcification": "CALCIFICATION_ICRU46"}
EGS_BRACHY_MATERIAL_CONVERTER = {"prostate": "WATER_1.000",
                                 "vessie": "WATER_1.000",
                                 "rectum": "WATER_1.000",
                                 "uretre": "WATER_1.000",
                                 "Bladder Neck": "WATER_1.000",
                                 "prostate_calcification": "WATER_1.000"}

# ["prostate", "vessie", "rectum", "uretre", "prostate_calcification"]
if __name__ == "__main__":
    ORGANS_TO_USE, RESTRUCTURING_FOLDERS, NUMBER_OF_PARTICLES = (["prostate", "vessie", "rectum", "uretre"], False, 1e7)
    PATIENTS_DIRECTORY = sys.argv[-2]
    OUTPUT_PATH = sys.argv[-1]
    extractor_selected = "permanent_implant_brachy"
    input_file_generator_selected = "egs_brachy_permanent_implant_brachy"
    runner_selected = "egs_brachy"
    output_file_format = "a3ddose"
    generate_sr = True
    recreate_struct = True
    reproduce_tg43_dose_grid = False
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
    series_description = "MCTG43CT_dose_recalculation"
    dicom_extractor = DicomExtractors(segmentation=[], build_structures=True,
                                      recreate_struct=recreate_struct, series_description=series_description)
    input_file_generator = InputFileGenerators(total_particles=NUMBER_OF_PARTICLES,
                                               run_mode="superposition",
                                               list_of_desired_structures=ORGANS_TO_USE,
                                               material_attribution_dict=EGS_BRACHY_MATERIAL_CONVERTER,
                                               egs_brachy_home=r'/EGSnrc_CLRP/egs_home/egs_brachy',
                                               batches=1,
                                               chunk=1,
                                               add="",
                                               generate_sr=generate_sr,
                                               crop=True,
                                               expand_tg45_phantom=500,
                                               code_version="commit 8ffa121f685b8a070d69b781d957bc0208fb608c",
                                               topas_output_type="binary",
                                               ct_calibration_curve=ct_calibration_curve
                                               )
    simulation_runner = SimulationRunners(nb_treads=12, waiting_time=30,
                                          egs_brachy_home=r'/EGSnrc_CLRP/egs_home/egs_brachy')

    output_cleaner = OutputCleaners(
        software="Systematic MC recalculation Workflow V0.4: MCTG43 commit: a6103b959926e2c280b3d3870fc0eefab71de342",
        dose_summation_type="PLAN",
        patient_orientation="",
        bits_allocated=16,
        series_description=series_description,
        generate_dvh=True,
        generate_sr=generate_sr,
        dvh_calculate_full_volume=False,
        dvh_use_structure_extents=False,
        dvh_comment="Generated by dicompyler-core",
        dvh_normalization_point=[0, 0, 0],
        dvh_interpolation_segments=2,
        dvh_dose_limit=60000,
        prescription_dose=144,
        use_updated_rt_struct=True)

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
            flipped = False
            if "flipped" in meta_data_dict.keys():
                flipped = "flipped"

            final_output_path = output_cleaner.clean_output(output_file_format, output_folder, final_output_folder,
                                                            study_path, image_position=image_position,
                                                            image_orientation_patient=image_orientation_patient,
                                                            to_dose_factor=to_dose_factor, sr_item_list=all_sr_sequence,
                                                            log_file=log_file, flipped=flipped)
            # shutil.rmtree(simulation_files_path)

        if RESTRUCTURING_FOLDERS:
            destructure_folder(patient_folder_path)
