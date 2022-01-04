from simulation_files.topas_file_templates.scorer_definition import CLINICAL_DOSE_GRID


class Dosimetry:
    """
    This class represent the clinical dosimetry stored in the DICOM RTDOSE file.
    """

    def __init__(self, rt_dose_uid, dose_data, dose_units, image_position_in_patient, patient_orientation,
                 dose_grid_shape, pixel_spacing, dose_grid_scaling, rt_plan_uid, rt_struct_uid, list_of_dvh):
        """
        
        :param rt_dose_uid: 
        :param dose_data: 
        :param dose_units: 
        :param image_position_in_patient: 
        :param patient_orientation: 
        :param dose_grid_shape: 
        :param pixel_spacing: 
        :param dose_grid_scaling: 
        :param rt_plan_uid: 
        :param rt_struct_uid: 
        :param list_of_dvh: 
        """
        self.rt_dose_uid = rt_dose_uid
        self.list_of_dvh = list_of_dvh
        self.rt_struct_uid = rt_struct_uid
        self.rt_plan_uid = rt_plan_uid
        self.dose_grid_scaling = dose_grid_scaling
        self.pixel_spacing = pixel_spacing
        self.dose_grid_shape = dose_grid_shape
        self.patient_orientation = patient_orientation
        self.image_position_in_patient = image_position_in_patient
        self.dose_units = dose_units
        self.dose_data = dose_data

    def add_dvhistograms(self, dvh) -> None:
        """
        This method adds one or many Masks to the
        mask list_of_masks.

        :param dvh:
        :return: None
        """
        if type(dvh) is list:
            self.list_of_dvh.extend(dvh)

        else:
            self.list_of_dvh.append(dvh)

    def generate_topas_scorer(self, output_path):
        voxel_size_z, voxel_size_y, voxel_size_x = self.pixel_spacing
        nb_z, nb_y, nb_x = self.dose_grid_shape
        originx = self.image_position_in_patient[0]
        originy = self.image_position_in_patient[1]
        originz = self.image_position_in_patient[2]
        transx = originx - (nb_x * voxel_size_x - voxel_size_x) / 2
        transy = originy - (nb_y * voxel_size_y - voxel_size_y) / 2
        transz = -originz - (nb_z * voxel_size_z - voxel_size_z) / 2

        return CLINICAL_DOSE_GRID.substitute(input_directory=output_path, transx=transx,
                                             transy=transy, tranz=transz, rotx="0.", roty="0.", rotz="0.",
                                             nb_of_columns=nb_x, nb_of_rows=nb_y, nb_of_slices=nb_z,
                                             voxel_size_x=voxel_size_x, voxel_size_z=voxel_size_x,
                                             voxel_size_y=voxel_size_y)


class DVHistogram:
    """
    This class
    """

    def __init__(self, reference_roi_number, dose_units, dvh_dose_scaling, dvh_volume_units, dvh_number_of_bins,
                 dvh_data, dvh_max, dvh_min, dvh_mean, parent_dosi):
        """

        :param reference_roi_number:
        :param dose_units:
        :param dvh_dose_scaling:
        :param dvh_volume_units:
        :param dvh_number_of_bins:
        :param dvh_data:
        :param dvh_max:
        :param dvh_min:
        :param dvh_mean:
        :param parent_dosi:
        """
        self.parent_dosi = parent_dosi
        self.dvh_mean = dvh_mean
        self.dvh_min = dvh_min
        self.dvh_max = dvh_max
        self.reference_roi_number = reference_roi_number
        self.dose_units = dose_units
        self.dvh_dose_scaling = dvh_dose_scaling
        self.dvh_volume_units = dvh_volume_units
        self.dvh_number_of_bins = dvh_number_of_bins
        self.dvh_data = dvh_data
