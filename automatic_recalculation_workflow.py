import getopt
import logging.config
import os
import sys
import numpy as np
from dicom_rt_context_extractor.utils.dicom_folder_structurer import restructure_dicom_folder, destructure_folder
from root import ROOT
from simulation_runners import SimulationRunners
from output_cleaners import OutputCleaners
from input_file_generators import InputFileGenerators
from extractors import DicomExtractors


def get_aguments(argv):
    restructuring = False
    recalculation_algorithm = "topas"
    segment_calcification = False
    organ_contours_to_use = []
    number_of_particles = 1e4

    try:
        opts, args = getopt.getopt(argv, "i:o:a:r:s:p:")
    except getopt.GetoptError:
        print('automatic_recalculation_workflow.py -i <inputfolder> -o <organs_to_use> -a <reacalculation_method> -r '
              '<restructure> -s <segmenting_calcifications>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-i':
            if os.path.exists(arg):
                patient_directory = arg
        elif opt == '-o':
            organ_contours_to_use.append(arg)
        elif opt == '-a':
            if arg not in ["topas", "egs_brachy"]:
                print(
                    'automatic_recalculation_workflow.py -i <inputfolder> -o <organs_to_use> -a '
                    '<reacalculation_method> -r '
                    '<restructure> -s <segmenting_calcifications>')
                sys.exit()
            recalculation_algorithm = arg
        elif opt == "-r":
            if arg == "True":
                restructuring = True
            elif arg == "False":
                restructuring = False
            else:
                print(
                    'automatic_recalculation_workflow.py -i <inputfolder> -o <organs_to_use> -a '
                    '<reacalculation_method> -r '
                    '<restructure> -s <segmenting_calcifications>')
                sys.exit()

        elif opt == "-s":
            if arg == "True":
                segment_calcification = True
            elif arg == "False":
                segment_calcification = False
            else:
                print(
                    'automatic_recalculation_workflow.py -i <inputfolder> -o <organs_to_use> -a '
                    '<reacalculation_method> -r '
                    '<restructure> -s <segmenting_calcifications>')
                sys.exit()

        elif opt == "-p":
            number_of_particles = int(arg)

        else:
            print('automatic_recalculation_workflow.py -i <inputfolder> -a <algorithm> -r <restructure>')
            sys.exit()

    return organ_contours_to_use, recalculation_algorithm, restructuring, segment_calcification, number_of_particles


TOPAS_MATERIAL_CONVERTER = {"prostate": "TG186Prostate",
                            "vessie": "TG186MeanMaleSoftTissue",
                            "rectum": "Air",
                            "uretre": "TG186MeanMaleSoftTissue",
                            "Bladder Neck": "TG186MeanMaleSoftTissue",
                            "calcification": "CALCIFICATION_ICRU46"}

EGS_BRACHY_MATERIAL_CONVERTER = {"prostate": "PROSTATE_WW86",
                                 "vessie": "URINARY_BLADDER_EMPTY",
                                 "rectum": "AIR_TG43",
                                 "uretre": "URETHRA_WW86",
                                 "Bladder Neck": "URINARY_BLADDER_EMPTY",
                                 "prostate_calcification": "CALCIFICATION_ICRU46"}

if __name__ == "__main__":
    ORGANS_TO_USE, RESTRUCTURING_FOLDERS, NUMBER_OF_PARTICLES = (["prostate", "vessie", "uretre",
                                                                  "rectum"], False, 5e8)
    PATIENTS_DIRECTORY = sys.argv[-2]
    OUTPUT_PATH = sys.argv[-1]
    extractor_selected = "permanent_implant_brachy"
    input_file_generator_selected = "egs_brachy_permanent_implant_brachy"
    runner_selected = "egs_brachy"
    output_file_format = "a3ddose"
    generate_sr = True
    dicom_extractor = DicomExtractors(segmentation=[])
    input_file_generator = InputFileGenerators(total_particles=NUMBER_OF_PARTICLES,
                                               list_of_desired_structures=ORGANS_TO_USE,
                                               material_attribution_dict=EGS_BRACHY_MATERIAL_CONVERTER,
                                               egs_brachy_home=r'/EGSnrc_CLRP/egs_home/egs_brachy',
                                               batches=1,
                                               chunk=1,
                                               add="",
                                               generate_sr=generate_sr,
                                               crop=True,
                                               expand_tg45_phantom=40,
                                               code_version="",
                                               topas_output_type="binary")
    simulation_runner = SimulationRunners(nb_treads=4, waiting_time=5,
                                          egs_brachy_home=r'/EGSnrc_CLRP/egs_home/egs_brachy')

    output_cleaner = OutputCleaners(software="Systematic MC recalculation Workflow V0.2",
                                    dose_summation_type="PLAN",
                                    patient_orientation="",
                                    bits_allocated=64,
                                    series_description="EGS_BRACHY_TG186_DOSE_COMP",
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
            simulation_files_path = os.path.join(ROOT, f"simulation_files", f"simulation_files_{patient}_{studies}")
            os.mkdir(simulation_files_path)
            final_output_folder = os.path.join(OUTPUT_PATH, f"final_output_{patient}_{studies}")
            os.mkdir(final_output_folder)
            log_file = os.path.join(simulation_files_path, "logs.logs")
            logging.basicConfig(filename=log_file, level=logging.INFO,
                                format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                                datefmt='%H:%M:%S')
            plan = dicom_extractor.extract_context_from_dicoms(extractor_selected, study_path, final_output_folder)
            sim_files_folder, meta_data_dict, all_sr_sequence = input_file_generator.generate_input_files(
                input_file_generator_selected,
                plan, simulation_files_path)

            output_folder = simulation_runner.launch_simulation(runner_selected, sim_files_folder,
                                                                simulation_files_path)

            image_position = np.asarray(plan.structures.x_y_z_origin)
            if "image_position_offset" in meta_data_dict.keys():
                image_position += np.asarray(meta_data_dict["image_position_offset"])

            image_orientation_patient = np.asarray(plan.structures.x_y_z_rotation_vectors)
            if "image_orientation_patient_offset" in meta_data_dict.keys():
                image_orientation_patient += np.asarray(meta_data_dict["image_orientation_patient_offset"])

            to_dose_factor = plan.dose_factor
            if "dose_factor_offset" in meta_data_dict.keys():
                to_dose_factor = to_dose_factor * meta_data_dict["dose_factor_offset"]

            final_output_path = output_cleaner.clean_output(output_file_format, output_folder, final_output_folder,
                                                            study_path, image_position=image_position,
                                                            image_orientation_patient=image_orientation_patient,
                                                            to_dose_factor=to_dose_factor, sr_item_list=all_sr_sequence,
                                                            log_file=log_file)

        if RESTRUCTURING_FOLDERS:
            destructure_folder(patient_folder_path)
