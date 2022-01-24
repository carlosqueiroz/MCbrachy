from dicom_rt_context_extractor.storage_objects.rt_dose_storage_classes import Dosimetry
from topas_file_generator.scorers.dose_grid_from_dicom_rt import dose_grid_from_dicom_rt


def generate_topas_scorer(clinical_dosi: Dosimetry, output_path):
    voxel_size_z, voxel_size_y, voxel_size_x = clinical_dosi.pixel_spacing
    nb_z, nb_y, nb_x = clinical_dosi.dose_grid_shape
    originx = clinical_dosi.image_position_in_patient[0]
    originy = clinical_dosi.image_position_in_patient[1]
    originz = clinical_dosi.image_position_in_patient[2]
    transx = originx - (nb_x * voxel_size_x - voxel_size_x) / 2
    transy = originy - (nb_y * voxel_size_y - voxel_size_y) / 2
    transz = -originz - (nb_z * voxel_size_z - voxel_size_z) / 2
    hlx = voxel_size_x * nb_x / 2
    hly = voxel_size_y * nb_y / 2
    hlz = voxel_size_z * nb_z / 2

    return dose_grid_from_dicom_rt.substitute(output_path=output_path, transx=transx,
                                              transy=transy, transz=transz, rotx="0.", roty="0.", rotz="0.",
                                              nb_of_columns=nb_x, nb_of_rows=nb_y, nb_of_slices=nb_z,
                                              voxel_size_x=voxel_size_x, voxel_size_z=voxel_size_x,
                                              voxel_size_y=voxel_size_y, hlx=hlx, hlz=hlz, hly=hly)


def generate_egs_brachy_scorer():
    raise NotImplementedError
