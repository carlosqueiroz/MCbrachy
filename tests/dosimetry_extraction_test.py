import os
import unittest
from extraction_pipeline_components.dosimetry_extraction import *
from root import ROOT

test_log_filename = os.path.join(ROOT, "logs", "test_logs")
logging.basicConfig(filename=test_log_filename,
                    format='%(asctime)s [%(levelname)s, %(module)s.%(funcName)s]: %(message)s',
                    filemode='w+',
                    level=logging.DEBUG)

data_folder = os.path.join(ROOT, "tests", "test_data")


class TestConvertIndexDoseGridIntoDosimetry(unittest.TestCase):
    def test_converter(self):
        dose_index_grid = np.asarray([[3, 8, 9, 10], [1, 5, 7, 11]])
        dose_grid = convert_index_dose_grid_into_dosimetry(dose_index_grid, 1.4)
        self.assertFalse((dose_index_grid * 1.4 - dose_grid).any())


class TestExtractPositioningFromRtDose(unittest.TestCase):
    def test_ldr_rt_dose(self):
        path_to_rt_dose = os.path.join(data_folder, "test_patient", "study", "rt_dose", "RTDOSE99.dcm")
        img_shape_3d, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors = extract_positioning_from_rt_dose(path_to_rt_dose)
        self.assertEqual(img_shape_3d, (77, 69, 85))
        self.assertEqual(x_y_z_spacing, (1.025963, 0.96749246428571, 1.02631578947368))
        self.assertEqual(x_y_z_origin, [-22.996212999999, 72.550671, -700])
        self.assertEqual(x_y_z_rotation_vectors, [1, 0, 0, 0, 1, 0])


class TestExtractDVH(unittest.TestCase):
    def test_no_DVH(self):
        path_to_rt_dose = os.path.join(data_folder, "test_patient", "study", "rt_dose", "RTDOSE99.dcm")
        dvh_dict = extract_dvh(path_to_rt_dose)
        self.assertEqual(dvh_dict, {})

    def test_with_dvh(self):
        path_to_rt_dose = os.path.join(data_folder, "RTDOSE_with_DVH.dcm")
        dvh_dict = extract_dvh(path_to_rt_dose)
        self.assertEqual(len(dvh_dict.keys()), 29)
        self.assertEqual(dvh_dict[1]["dvh_data"].shape, (3, 8043))
        self.assertEqual(dvh_dict[1]["dose_units"], "GY")
        self.assertEqual(dvh_dict[1]["dvh_scaling"], 1.0)
        self.assertEqual(dvh_dict[1]["volume_units"], "CM3")
        self.assertEqual(dvh_dict[1]["nb_bins"], 8043)
        self.assertEqual(dvh_dict[1]["min_dose"], 0.00048250919)
        self.assertEqual(dvh_dict[1]["max_dose"], 80.4173937888199)
        self.assertEqual(dvh_dict[1]["mean_dose"], 15.3580312059228)

    def test_convert_dvh_data_into_value_table_array(self):
        initial_dvh = np.asarray([0.5, 1, 0.5, 2, 0.5, 3, 0.5, 4, 0.5, 5, 0.5, 6, 0.5, 7, 0.5, 8])
        new_dvh = convert_dvh_data_into_value_table_array(initial_dvh, 8)
        self.assertFalse((np.asarray([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]) - new_dvh[2, :]).any())
        self.assertFalse((np.asarray([1., 2., 3., 4., 5., 6., 7., 8.]) - new_dvh[1, :]).any())
        self.assertFalse((np.asarray([0.25, 0.75, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75]) - new_dvh[0, :]).any())


class TestExtractDosimetry(unittest.TestCase):
    def test_no_dvh(self):
        path_to_rt_dose = os.path.join(data_folder, "test_patient", "study", "rt_dose", "RTDOSE99.dcm")
        dosi = extract_dosimetry(path_to_rt_dose)
        self.assertEqual(dosi.dose_grid_shape, (77, 69, 85))
        self.assertEqual(dosi.pixel_spacing, (1.025963, 0.96749246428571, 1.02631578947368))
        self.assertEqual(dosi.image_position_in_patient, [-22.996212999999, 72.550671, -700])
        self.assertEqual(dosi.patient_orientation, [1, 0, 0, 0, 1, 0])
        self.assertEqual(dosi.rt_dose_uid, "1.2.826.0.1.3680043.10.424.3347861674843696263926395926853075079")
        self.assertEqual(dosi.rt_plan_uid, "1.2.826.0.1.3680043.10.424.1326279788265105019278215552609106950")
        self.assertEqual(dosi.rt_struct_uid, None)
        self.assertEqual(dosi.list_of_dvh, [])

    def test_with_dvh(self):
        path_to_rt_dose = os.path.join(data_folder, "RTDOSE_with_DVH.dcm")
        dosi = extract_dosimetry(path_to_rt_dose)
        self.assertEqual(dosi.dose_grid_shape, (191, 114, 177))
        self.assertEqual(dosi.pixel_spacing, (2.5, 2.5, -1.0))
        self.assertEqual(dosi.image_position_in_patient, [-223.2910156, -367.7369026, -325])
        self.assertEqual(dosi.patient_orientation, [1, 0, 0, 0, 1, 0])
        self.assertEqual(dosi.rt_dose_uid, "1.3.6.1.4.1.14519.5.2.1.2193.7172.164297574198062016125837186827")
        self.assertEqual(dosi.rt_plan_uid, "1.3.6.1.4.1.14519.5.2.1.2193.7172.206067362454172824588685033899")
        self.assertEqual(dosi.rt_struct_uid, "1.3.6.1.4.1.14519.5.2.1.2193.7172.752610900965808553460727836467")
        self.assertEqual(len(dosi.list_of_dvh), 29)
        self.assertEqual(dosi.list_of_dvh[0].dvh_data.shape, (3, 8043))
        self.assertEqual(dosi.list_of_dvh[0].dose_units, "GY")
        self.assertEqual(dosi.list_of_dvh[0].dvh_dose_scaling, 1.0)
        self.assertEqual(dosi.list_of_dvh[0].dvh_volume_units, "CM3")
        self.assertEqual(dosi.list_of_dvh[0].dvh_number_of_bins, 8043)
        self.assertEqual(dosi.list_of_dvh[0].dvh_min, 0.00048250919)
        self.assertEqual(dosi.list_of_dvh[0].dvh_max, 80.4173937888199)
        self.assertEqual(dosi.list_of_dvh[0].dvh_mean, 15.3580312059228)
        self.assertEqual(dosi.list_of_dvh[0].reference_roi_number, 1)


if __name__ == '__main__':
    unittest.main()
