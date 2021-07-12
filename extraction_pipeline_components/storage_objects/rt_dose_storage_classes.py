class Dosimetry:
    def __init__(self, dose_data, dose_units, image_position_in_patient, patientorientation, dose_grid_shape,
                 pixel_spacing, dose_grid_scaling, rt_plan_uid, rt_struct_uid, list_of_dvh):
        self.list_of_dvh = list_of_dvh
        self.rt_struct_uid = rt_struct_uid
        self.rt_plan_uid = rt_plan_uid
        self.dose_grid_scaling = dose_grid_scaling
        self.pixel_spacing = pixel_spacing
        self.dose_grid_shape = dose_grid_shape
        self.patientorientation = patientorientation
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


class DVHistogram:
    def __init__(self, reference_roi_number, dose_units, dvh_dose_scaling, dvh_volume_units, dvh_number_of_bins,
                 dvh_data, dvh_max, dvh_min, dvh_mean, parent_dosi):
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
