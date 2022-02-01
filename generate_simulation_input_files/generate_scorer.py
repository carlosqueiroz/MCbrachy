import os

from dicom_rt_context_extractor.storage_objects.rt_dose_storage_classes import Dosimetry
from topas_file_generator.scorers.dose_grid_from_dicom_rt import dose_grid_from_dicom_rt
from generate_simulation_input_files.material_attribution import EGS_BRACHY_MATERIAL_CONVERTER
from egs_brachy_file_generator.scoring.with_egs_phant import SCORER_WITH_EGS_PHANT

from root import ROOT


def generate_topas_scorer(clinical_dosi: Dosimetry, output_path, output_type):
    voxel_size_z, voxel_size_y, voxel_size_x = 2, 0.37109375, 0.37109375
    nb_z, nb_y, nb_x = 99, 512, 512
    originx = 0.0
    originy = 0.0
    originz = 0.0
    transx = originx + (nb_x * voxel_size_x - voxel_size_x) / 2
    transy = originy + (nb_y * voxel_size_y - voxel_size_y) / 2
    transz = originz - (nb_z * voxel_size_z - voxel_size_z) / 2
    hlx = voxel_size_x * nb_x / 2
    hly = voxel_size_y * nb_y / 2
    hlz = voxel_size_z * nb_z / 2
    muen_path = os.path.join(ROOT, "simulation_files", "Muen.dat")

    return dose_grid_from_dicom_rt.substitute(output_path=output_path, transx=transx,
                                              transy=transy, transz=transz, rotx="0.", roty="0.", rotz="0.",
                                              nb_of_columns=nb_x, nb_of_rows=nb_y, nb_of_slices=nb_z,
                                              voxel_size_x=voxel_size_x, voxel_size_z=voxel_size_x,
                                              voxel_size_y=voxel_size_y, hlx=hlx, hlz=hlz, hly=hly,
                                              output_type=output_type, data_path=muen_path)


def generate_egs_brachy_scorer(list_of_structures, path_to_egs_brachy_folder):
    media = "WATER_0.998"
    for struct in list_of_structures:
        media = media + " " + EGS_BRACHY_MATERIAL_CONVERTER[struct]

    return SCORER_WITH_EGS_PHANT.substitute(egs_folder_path=path_to_egs_brachy_folder, list_of_materials=media)

