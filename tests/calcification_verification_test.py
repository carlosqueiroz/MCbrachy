import unittest
import os
import logging
import numpy as np
from unittest.mock import patch
from preprocessing_pipeline_components import calcification_verification as calv
from root import ROOT

test_log_filename = os.path.join(ROOT, r'logs\test_logs')
logging.basicConfig(filename=test_log_filename,
                    format='%(asctime)s [%(levelname)s, %(module)s.%(funcName)s]: %(message)s',
                    filemode='w+',
                    level=logging.DEBUG)

data_folder = os.path.join(ROOT, r'tests\test_data')


class TestGenerate3DImageFromSeries(unittest.TestCase):
    def test_if_all_instance_are_loaded(self):
        series0_folder = os.path.join(data_folder, 'fictional_study', "series0")
        image3d = calv.generate_3d_image_from_series(series0_folder)

        self.assertEqual(image3d.shape, (448, 448, 2))

    def test_reproductibility(self):
        series0_folder = os.path.join(data_folder, 'fictional_study', "series0")
        image3d = calv.generate_3d_image_from_series(series0_folder)
        image3d_2 = calv.generate_3d_image_from_series(series0_folder)
        series1_folder = os.path.join(data_folder, 'fictional_study', "series1")
        image3d_3 = calv.generate_3d_image_from_series(series1_folder)

        self.assertFalse((image3d - image3d_2).all())
        self.assertFalse((image3d - image3d_3).all())
        self.assertFalse((image3d_3 - image3d_2).all())

    def test_no_image(self):
        bad_series_folder = os.path.join(data_folder, 'VS-SEG-001', "study", "01992")
        image3d = calv.generate_3d_image_from_series(bad_series_folder)

        self.assertEqual(image3d, np.zeros(1))


class TestPlotWholeSeries(unittest.TestCase):

    def test_nothing_to_show(self):
        bad_series_folder = os.path.join(data_folder, 'VS-SEG-001', "study", "01992")
        something_to_plot = calv.plot_whole_series(bad_series_folder)
        self.assertFalse(something_to_plot)

    def test_something_to_show(self):
        with patch("preprocessing_pipeline_components.calcification_verification.plt.show"):
            series0_folder = os.path.join(data_folder, 'fictional_study', "series0")
            something_to_plot = calv.plot_whole_series(series0_folder)
            self.assertTrue(something_to_plot)


class TestManualSelectionOfCalcification(unittest.TestCase):

    def test_user_interaction_yes_case(self):
        with patch("preprocessing_pipeline_components.calcification_verification.plt.show"):
            with patch("preprocessing_pipeline_components.calcification_verification.get_input", return_value="Yes"):
                series0_folder = os.path.join(data_folder, 'fictional_study', "series0")
                calcification = calv.manual_selection_of_calcification(series0_folder)
                self.assertTrue(calcification)

    def test_user_interaction_no_case(self):
        with patch("preprocessing_pipeline_components.calcification_verification.plt.show"):
            with patch("preprocessing_pipeline_components.calcification_verification.get_input", return_value="No"):
                series0_folder = os.path.join(data_folder, 'fictional_study', "series0")
                calcification = calv.manual_selection_of_calcification(series0_folder)
                self.assertFalse(calcification)

    def test_no_image(self):
        bad_series_folder = os.path.join(data_folder, 'VS-SEG-001', "study", "01992")
        calcification = calv.manual_selection_of_calcification(bad_series_folder)
        self.assertFalse(calcification)


class TestIsThereProstateCalcificationInStudy(unittest.TestCase):

    def test_user_interaction_yes_case(self):
        with patch("preprocessing_pipeline_components.calcification_verification.plt.show"):
            with patch("preprocessing_pipeline_components.calcification_verification.get_input", return_value="Yes"):
                study_folder = os.path.join(data_folder, 'fictional_study')
                calcification = calv.is_there_prostate_calcification_in_study(study_folder)
                self.assertTrue(calcification)

    def test_user_interaction_no_case(self):
        with patch("preprocessing_pipeline_components.calcification_verification.plt.show"):
            with patch("preprocessing_pipeline_components.calcification_verification.get_input", return_value="No"):
                study_folder = os.path.join(data_folder, 'fictional_study')
                calcification = calv.is_there_prostate_calcification_in_study(study_folder)
                self.assertFalse(calcification)

    def test_no_images_in_study(self):
        bad_study_folder = os.path.join(data_folder, 'VS-SEG-001', "study")
        calcification = calv.is_there_prostate_calcification_in_study(bad_study_folder)
        self.assertFalse(calcification)





if __name__ == '__main__':
    unittest.main()
