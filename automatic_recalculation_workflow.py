import getopt
import logging
import os
import sys
from datetime import date, time

from dicom_rt_context_extractor.utils.dicom_folder_structurer import restructure_dicom_folder, destructure_folder
from root import ROOT
from simulation_runners import SimulationRunners
from output_cleaners import OutputCleaners
from input_file_generators import InputFileGenerators
from extractors import DicomExtractors
from dicom_sr_builder.sr_builder import SRBuilder


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
                                 "rectum": "RECTUM_ICRP23",
                                 "uretre": "URETHRA_WW86",
                                 "Bladder Neck": "URINARY_BLADDER_EMPTY",
                                 "calcification": "CALCIFICATION_ICRU46"}

if __name__ == "__main__":
    def logs_file_setup(file_path, level=logging.INFO):
        logs_file = file_path
        logging.basicConfig(filename=logs_file, filemode='w+', level=level)
        handler = logging.StreamHandler(sys.stdout)
        logging.getLogger().addHandler(handler)


    ORGANS_TO_USE, RESTRUCTURING_FOLDERS, NUMBER_OF_PARTICLES = (["prostate"], False, 1e3)
    PATIENTS_DIRECTORY = sys.argv[-2]
    OUTPUT_PATH = sys.argv[-1]

    extractor_selected = "permanent_implant_brachy"
    input_file_generator_selected = "egs_brachy_permanent_implant_brachy"
    runner_selected = "egs_brachy"
    output_file_format = "a3ddose"
    generate_sr = True

    dicom_extractor = DicomExtractors(segmentation=["prostate_calcification"])
    input_file_generator = InputFileGenerators(total_particles=NUMBER_OF_PARTICLES,
                                               list_of_desired_structures=ORGANS_TO_USE,
                                               material_attribution_dict=EGS_BRACHY_MATERIAL_CONVERTER,
                                               egs_brachy_home=r'/EGSnrc_CLRP/egs_home/egs_brachy',
                                               batches=1,
                                               chunk=1,
                                               add="",
                                               generate_sr=generate_sr,
                                               crop=True,
                                               code_version="")
    simulation_runner = SimulationRunners(nb_treads=1, waiting_time=5,
                                          egs_brachy_home=r'/EGSnrc_CLRP/egs_home/egs_brachy')
    output_cleaner = OutputCleaners(software="Systematic MC recalculation Workflow V0.2",
                                    image_position=r'0\0\0',
                                    image_orientation_patient=r'1\0\0\0\1\0',
                                    to_dose_factor=1.0,
                                    dose_summation_type="PLAN",
                                    patient_orientation="",
                                    bits_allocated=16,
                                    series_description="EGS_BRACHY_TG186_DOSE",
                                    generate_dvh=False)

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
            log_file = os.path.join(ROOT, f"simulation_files", f"simulation_files_{patient}_{studies}", "logs.logs")
            logs_file_setup(log_file)
            plan = dicom_extractor.extract_context_from_dicoms(extractor_selected, study_path, final_output_folder)
            sim_files_folder, meta_data_dict, all_sr_sequence = input_file_generator.generate_input_files(
                input_file_generator_selected,
                plan, simulation_files_path)

            output_folder = simulation_runner.launch_simulation(runner_selected, sim_files_folder,
                                                                simulation_files_path)
            try:
                final_output_path = output_cleaner.clean_output(output_file_format, output_folder, final_output_folder,
                                                                plan.plan_path)
            except:
                pass
            if generate_sr:
                content_sequence_items = []
                for content_sequence in all_sr_sequence:
                    content_sequence_items.append(content_sequence.BuildDictionary())

                with open(log_file, 'r') as file:
                    logs_as_text = file.read().replace('\n', ' ')

                content_sequence_items.append({"ValueType": "TEXT",
                                               "RelationshipType": "HAS ACQ CONTEXT",
                                               "ConceptNameCodeSequence": {"CodeValue": "1000",
                                                                           "CodingSchemeDesignator": "CUSTOM",
                                                                           "CodeMeaning": "Logs"},
                                               "Value": logs_as_text})
                whole_content_sequence = {"ValueType": "CONTAINER",
                                          "ConceptNameCodeSequence": {"CodeValue": "100",
                                                                      "CodingSchemeDesignator": "CUSTOM",
                                                                      "CodeMeaning": "MC simulation parameters"},
                                          "ContinuityOfContent": "SEPERATE",
                                          "Value": content_sequence_items}

                sr_builder = SRBuilder()
                sr_builder.add_content_sequence(whole_content_sequence)
                sr_builder.build()
                sr_path = os.path.join(final_output_folder, f"SR_{plan.patient}_{plan.study}.dcm")
                sr_builder.save_sr_to(sr_path)

        if RESTRUCTURING_FOLDERS:
            destructure_folder(patient_folder_path)
