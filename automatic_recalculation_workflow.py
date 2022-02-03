import getopt
import os
import subprocess
import sys

from shutil import copy, move
from clean_output_data.clean_egs_brachy_output import clean_egs_brachy_output
from clean_output_data.clean_topas_output import clean_topas_output
from dicom_rt_context_extractor.sources_information_extraction import extract_all_sources_informations
from dicom_rt_context_extractor.utils.dicom_folder_structurer import restructure_dicom_folder, destructure_folder
from dicom_rt_context_extractor.utils.search_instance_and_convert_coord_in_pixel import find_modality_in_folder, \
    find_instance_in_folder
from prostate_calcification_segmentation.calcification_segmentation import segmenting_calcification
from generate_simulation_input_files.generate_simulation_input_files import generate_whole_egs_brachy_input_file
from generate_simulation_input_files.generate_simulation_input_files import generate_whole_topas_input_file
from root import ROOT


def get_aguments(argv):
    restructuring = False
    recalculation_algorithm = "topas"
    segment_calcification = False
    organ_contours_to_use = []
    number_of_particles = 1e7

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


if __name__ == "__main__":
    ORGANS_TO_USE, RECALCULATION_ALGORITHM, RESTRUCTURING_FOLDERS, \
    SEGMENT_CALCIFICATIONS, NUMBER_OF_PARTICLES = get_aguments(sys.argv[1:-2])
    PATIENTS_DIRECTORY = sys.argv[-2]
    OUTPUT_PATH = sys.argv[-1]

    for patient in os.listdir(PATIENTS_DIRECTORY):
        patient_folder_path = os.path.join(PATIENTS_DIRECTORY, patient)
        if RESTRUCTURING_FOLDERS:
            restructure_dicom_folder(patient_folder_path, patient_folder_path)

        for studies in os.listdir(patient_folder_path):
            study_path = os.path.join(patient_folder_path, studies)
            # Lets find and extract the rt plan first
            rt_plan_path = find_modality_in_folder("RTPLAN", study_path)
            plan = extract_all_sources_informations(rt_plan_path)
            plan.extract_structures(study_path)
            plan.extract_dosimetry(study_path)
            struct = plan.get_structures()
            if SEGMENT_CALCIFICATIONS:
                struct.add_mask_from_3d_array(segmenting_calcification(plan, 1.9, study_path),
                                              roi_name="calcification",
                                              observation_label="masking souces with cylindrical masks with "
                                                                "thresholding",
                                              segmentation_method=1, add_to_original_rt_struct_file=True,
                                              saving_path=os.path.join(OUTPUT_PATH,
                                                                       f"updated_{patient}_{studies}_RTSTRUCT.dcm"))

            if RECALCULATION_ALGORITHM == "egs_brachy":
                phant_saving_path = os.path.join(OUTPUT_PATH,
                                                 f"egs_phant_{patient}_{studies}.egsphant")
                transform_saving_path = os.path.join(OUTPUT_PATH,
                                                 f"source_transform_{patient}_{studies}")
                input_saving_path = os.path.join(r'/EGSnrc_CLRP/egs_home/egs_brachy',
                                                 f"input_{patient}_{studies}.egsinp")
                output_saving_path = os.path.join(OUTPUT_PATH, f"input_{patient}_{studies}.phantom.3ddose")
                try:
                    generate_whole_egs_brachy_input_file(plan, int(NUMBER_OF_PARTICLES), ORGANS_TO_USE, transform_saving_path,
                                                         input_saving_path, r'/EGSnrc_CLRP/egs_home/egs_brachy',
                                                         phant_saving_path)
                    bash_command = f"/EGSnrc_CLRP/egs_home/bin/linux/egs_brachy -i input_{patient}_{studies}.egsinp"
                    simulation = subprocess.run(bash_command.split())
                    move(input_saving_path, os.path.join(OUTPUT_PATH, f"input_{patient}_{studies}.egsinp"))
                    copy(rf"/EGSnrc_CLRP/egs_home/egs_brachy/input_{patient}_{studies}.phantom.3ddose", output_saving_path)
                    path_to_rt_dose = find_instance_in_folder(plan.rt_dose_uid, study_path)
                    output_rt_dose = os.path.join(OUTPUT_PATH, f"egs_dose_{patient}_{studies}.dcm")
                    output_rt_dose_err = os.path.join(OUTPUT_PATH, f"egs_err_{patient}_{studies}.dcm")
                    output_rt_plan = os.path.join(OUTPUT_PATH, f"updated_plan_{patient}_{studies}.dcm")
                    clean_egs_brachy_output(output_saving_path, path_to_rt_dose, rt_plan_path, plan,
                                            output_rt_dose,
                                            output_rt_dose_err, output_rt_plan, "Scaling factor gives total dose in GY",
                                            "Warning, the scailing factor is the dose scailing factor error",
                                            "workflow:0",
                                            "EGS_BRACHY_TG186_DOSE")

                except NotImplementedError:
                    continue

            elif RECALCULATION_ALGORITHM == "topas":
                index_saving_path = os.path.join(OUTPUT_PATH,
                                                 f"mapping_{patient}_{studies}.bin")
                input_saving_path = os.path.join(OUTPUT_PATH,
                                                 f"input_{patient}_{studies}.txt")
                output_saving_path = os.path.join(OUTPUT_PATH, f"dose_{patient}_{studies}")
                try:
                    string_to_add = "i:Ts/NumberOfThreads = -2 \ni:Ts/ShowHistoryCountAtInterval = 10000"
                    os.chmod(os.path.join(ROOT, "simulation_files", "Muen.dat"), 0o777)
                    generate_whole_topas_input_file(plan, NUMBER_OF_PARTICLES, ORGANS_TO_USE, output_saving_path,
                                                    input_saving_path, index_saving_path,
                                                    output_type="binary", add=string_to_add)
                    bash_command = f"/topas/topas/bin/topas {input_saving_path}"
                    os.chmod(input_saving_path, 0o777)
                    os.chmod(index_saving_path, 0o777)
                    simulation = subprocess.run(bash_command.split())
                    path_to_rt_dose = find_instance_in_folder(plan.rt_dose_uid, study_path)
                    output_rt_dose = os.path.join(OUTPUT_PATH, f"topas_dose_{patient}_{studies}.dcm")
                    output_rt_dose_err = os.path.join(OUTPUT_PATH, f"topas_err_{patient}_{studies}.dcm")
                    output_rt_plan = os.path.join(OUTPUT_PATH, f"updated_plan_{patient}_{studies}.dcm")
                    clean_topas_output(output_saving_path + ".bin", path_to_rt_dose, rt_plan_path, plan, output_rt_dose,
                                       output_rt_dose_err, output_rt_plan, "Scaling factor gives total dose in GY",
                                       "Warning, the scailing factor is the dose scailing factor error", "workflow:0",
                                       "TOPAS_TG186_DOSE")

                except NotImplementedError:
                    continue

        if RESTRUCTURING_FOLDERS:
            destructure_folder(patient_folder_path)
