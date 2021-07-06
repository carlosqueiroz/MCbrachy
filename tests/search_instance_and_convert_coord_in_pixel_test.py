import unittest
from root import ROOT
from extraction_pipeline_components.utils.search_instance_and_convert_coord_in_pixel import *

test_log_filename = os.path.join(ROOT, r'logs\test_logs')
logging.basicConfig(filename=test_log_filename,
                    format='%(asctime)s [%(levelname)s, %(module)s.%(funcName)s]: %(message)s',
                    filemode='w+',
                    level=logging.DEBUG)

data_folder = os.path.join(ROOT, r'tests\test_data')


class TestExtractPositionningInformations(unittest.TestCase):
    def test_normal_cases(self):
        path_to_image = os.path.join(data_folder, "fictional_study", "series0", "1-01.dcm")
        img_shape_2d, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors = extract_positionning_informations(
            path_to_image)

        self.assertEqual(img_shape_2d, (448, 448))
        self.assertEqual(x_y_z_spacing, (0.46875, 0.46875, 1.5))
        self.assertEqual(x_y_z_origin, [-95.314769766409, -131.02905652754, -66.513922691345])
        self.assertEqual(x_y_z_rotation_vectors, [1, -2.051034e-010, 0, 2.051034e-010, 1, 0])

    def test_bad_file_cases(self):
        path_to_image = os.path.join(data_folder, "1-1.dcm")
        img_shape_2d, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors = extract_positionning_informations(
            path_to_image)

        self.assertEqual(img_shape_2d, (0., 0.))
        self.assertEqual(x_y_z_spacing, (0., 0., 0.0))
        self.assertEqual(x_y_z_origin, [0., 0., 0.])
        self.assertEqual(x_y_z_rotation_vectors, [0., 0., 0., 0., 0., 0.])


class TestFindInstanceInFolder(unittest.TestCase):
    def test_level_1_folder(self):
        uid = "1.3.6.1.4.1.14519.5.2.1.226742563510968359814545353392980263364"
        folder_path = os.path.join(data_folder, "fictional_study", "series0")
        path_to_instance = find_instance_in_folder(uid, folder_path)
        self.assertEqual(path_to_instance, os.path.join(data_folder, "fictional_study", "series0", "1-01.dcm"))
        bad_uid = "3.6.1.4.1.14519.5.2.1.226742563510968359814545353392980263364"
        path_to_instance = find_instance_in_folder(bad_uid, folder_path)
        self.assertEqual(path_to_instance, None)

    def test_level_2_folder(self):
        uid = "1.3.6.1.4.1.14519.5.2.1.226742563510968359814545353392980263364"
        folder_path = os.path.join(data_folder, "fictional_study")
        path_to_instance = find_instance_in_folder(uid, folder_path)
        self.assertEqual(path_to_instance, os.path.join(data_folder, "fictional_study", "series0", "1-01.dcm"))
        bad_uid = "3.6.1.4.1.14519.5.2.1.226742563510968359814545353392980263364"
        path_to_instance = find_instance_in_folder(bad_uid, folder_path)
        self.assertEqual(path_to_instance, None)

    def test_level_3_folder(self):
        uid = "1.3.6.1.4.1.14519.5.2.1.226742563510968359814545353392980263364"
        folder_path = data_folder
        path_to_instance = find_instance_in_folder(uid, folder_path)
        self.assertEqual(path_to_instance, os.path.join(data_folder, "fictional_study", "series0", "1-01.dcm"))
        bad_uid = "3.6.1.4.1.14519.5.2.1.226742563510968359814545353392980263364"
        path_to_instance = find_instance_in_folder(bad_uid, folder_path)
        self.assertEqual(path_to_instance, None)


class TestConvertRealCoordToPixelCoord(unittest.TestCase):
    def test_conversion(self):
        path_to_image = os.path.join(data_folder, "fictional_study", "series0", "1-01.dcm")
        img_shape_2d, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors = extract_positionning_informations(
            path_to_image)
        values = np.asarray([[54.3, -32.2, 40.0], [52.2, -34.2, 40.0]])
        pixel_values = convert_real_coord_to_pixel_coord(values, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors)
        self.assertFalse((pixel_values - np.asarray([[319, 211, -71], [315, 207, -71]])).any())

    def test_deconversion(self):
        path_to_image = os.path.join(data_folder, "fictional_study", "series0", "1-01.dcm")
        img_shape_2d, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors = extract_positionning_informations(
            path_to_image)
        values = np.asarray([[54.3, -32.2, 40.0], [52.2, -34.2, 40.0]])
        pixel_values = convert_real_coord_to_pixel_coord(values, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors)
        de_conv = convert_pixel_coord_to_real_coord(pixel_values, x_y_z_spacing, x_y_z_origin, x_y_z_rotation_vectors)
        self.assertTrue(np.where(abs(de_conv - np.asarray([[54.3, -32.2, 40.0],
                                                           [52.2, -34.2, 40.0]])) > 0.25, 0, 1).all())


if __name__ == '__main__':
    unittest.main()
