import unittest
import os
import logging
import json
from preprocessing_pipeline_components import contour_verification as conv
from root import ROOT
from unittest.mock import patch

test_log_filename = os.path.join(ROOT, "logs", "test_logs")
logging.basicConfig(filename=test_log_filename,
                    format='%(asctime)s [%(levelname)s, %(module)s.%(funcName)s]: %(message)s',
                    filemode='w+',
                    level=logging.DEBUG)

data_folder = os.path.join(ROOT, "tests", "test_data")


class TestAddExpressionToContourVocab(unittest.TestCase):
    def setUp(self):
        test_vocab_path = os.path.join(data_folder, "test_vocab.json")
        vocab_file = open(test_vocab_path, "w")
        json.dump({}, vocab_file)
        vocab_file.close()
        conv.contour_vocab_path = test_vocab_path

    def test_adding_category_when_empty(self):
        with patch("preprocessing_pipeline_components.contour_verification.get_input", return_value='Yes'):
            conv.add_expression_to_contour_vocab("Prostate", {})
        contour_site_vocabulary_file = open(conv.contour_vocab_path, "r")
        contour_site_vocabulary = json.loads(contour_site_vocabulary_file.read())
        contour_site_vocabulary_file.close()
        self.assertEqual(contour_site_vocabulary, {"Yes": ["Prostate"]})
        with patch("preprocessing_pipeline_components.contour_verification.get_input", return_value='No'):
            conv.add_expression_to_contour_vocab("Vessie", {})
        contour_site_vocabulary_file = open(conv.contour_vocab_path, "r")
        contour_site_vocabulary = json.loads(contour_site_vocabulary_file.read())
        contour_site_vocabulary_file.close()
        self.assertEqual(contour_site_vocabulary, {})

    def test_adding_category_when_not_empty(self):
        with patch("preprocessing_pipeline_components.contour_verification.get_input", return_value='Yes'):
            conv.add_expression_to_contour_vocab("Rectum", {"Prostate": ["Prostate", "prostate"],
                                                            "Vessie": ["Vessie", "vessie"]})

        contour_site_vocabulary_file = open(conv.contour_vocab_path, "r")
        contour_site_vocabulary = json.loads(contour_site_vocabulary_file.read())
        contour_site_vocabulary_file.close()
        self.assertEqual(contour_site_vocabulary, {"Prostate": ["Prostate", "prostate"],
                                                   "Vessie": ["Vessie", "vessie"], "Yes": ["Rectum"]})

        with patch("preprocessing_pipeline_components.contour_verification.get_input", return_value='Yes'):
            conv.add_expression_to_contour_vocab("rectum", {"Prostate": ["Prostate", "prostate"],
                                                            "Vessie": ["Vessie", "vessie"],
                                                            "Yes": ["Rectum"]})
        contour_site_vocabulary_file = open(conv.contour_vocab_path, "r")
        contour_site_vocabulary = json.loads(contour_site_vocabulary_file.read())
        contour_site_vocabulary_file.close()

        self.assertEqual(contour_site_vocabulary, {"Prostate": ["Prostate", "prostate"],
                                                   "Vessie": ["Vessie", "vessie"], "Yes": ["Rectum", "rectum"]})

    def tearDown(self) -> None:
        if os.path.exists(conv.contour_vocab_path):
            os.remove(conv.contour_vocab_path)


class TestVerifyIfRoiInDesiredRois(unittest.TestCase):
    def setUp(self):
        test_vocab_path = os.path.join(data_folder, "test_vocab.json")
        vocab_file = open(test_vocab_path, "w")
        json.dump({"prostate": ["Prostate"], "vessie": ["Vessie"]}, vocab_file)
        vocab_file.close()
        conv.contour_vocab_path = test_vocab_path

    def test_roi_not_desired_roi_but_in_vocab(self):
        verification, it = conv.verify_if_roi_in_desired_rois("Vessie", ["prostate"], True)
        self.assertFalse(verification)
        verification, it = conv.verify_if_roi_in_desired_rois("Vessie", ["prostate"])
        self.assertFalse(verification)
        verification, it = conv.verify_if_roi_in_desired_rois("Vessie", ["rectum"])
        self.assertFalse(verification)

    def test_roi_in_desired_roi_and_in_vocab(self):
        verification, it = conv.verify_if_roi_in_desired_rois("Prostate", ["prostate"], True)
        self.assertTrue(verification)
        self.assertEqual(it, 0)
        verification, it = conv.verify_if_roi_in_desired_rois("Vessie", ["vessie"])
        self.assertTrue(verification)
        self.assertEqual(it, 0)
        verification, it = conv.verify_if_roi_in_desired_rois("Vessie", ["vessie", "prostate"])
        self.assertTrue(verification)
        self.assertEqual(it, 0)
        verification, it = conv.verify_if_roi_in_desired_rois("Prostate", ["vessie", "prostate"])
        self.assertTrue(verification)
        self.assertEqual(it, 1)

    def test_roi_not_in_vocab(self):
        verification, it = conv.verify_if_roi_in_desired_rois("Prostate0", ["prostate"], True)
        self.assertFalse(verification)
        with patch("preprocessing_pipeline_components.contour_verification.get_input", return_value='Yes'):
            verification, it = conv.verify_if_roi_in_desired_rois("Prostate0", ["prostate"], True)
            self.assertFalse(verification)
        with patch("preprocessing_pipeline_components.contour_verification.get_input", return_value='No'):
            verification, it = conv.verify_if_roi_in_desired_rois("Prostate0", ["prostate"])
            self.assertFalse(verification)
        with patch("preprocessing_pipeline_components.contour_verification.get_input", return_value='Yes'):
            verification, it = conv.verify_if_roi_in_desired_rois("Prostate0", ["prostate"])
            self.assertFalse(verification)

        contour_vocabulary_file = open(conv.contour_vocab_path, "r")
        contour_vocabulary = json.loads(contour_vocabulary_file.read())
        contour_vocabulary_file.close()
        self.assertEqual(contour_vocabulary, {"prostate": ["Prostate"], "vessie": ["Vessie"], "Yes": ["Prostate0"]})

    def tearDown(self) -> None:
        if os.path.exists(conv.contour_vocab_path):
            os.remove(conv.contour_vocab_path)


class TestVerifyIfAllRequiredContoursArePresent(unittest.TestCase):
    def setUp(self):
        test_vocab_path = os.path.join(data_folder, "test_vocab.json")
        vocab_file = open(test_vocab_path, "w")
        json.dump({"prostate": ["Prostate"], "vessie": ["Bladder"]}, vocab_file)
        vocab_file.close()
        conv.contour_vocab_path = test_vocab_path

    def test_no_missing_roi(self):
        with patch("preprocessing_pipeline_components.contour_verification.get_input", return_value='No'):
            path_to_data = os.path.join(data_folder, "RTSTRUCT.dcm")
            verification = conv.verify_if_all_required_contours_are_present(path_to_data, ["prostate"])
            self.assertTrue(verification)
        with patch("preprocessing_pipeline_components.contour_verification.get_input", return_value='No'):
            path_to_data = os.path.join(data_folder, "RTSTRUCT.dcm")
            verification = conv.verify_if_all_required_contours_are_present(path_to_data, ["vessie"])
            self.assertTrue(verification)
        with patch("preprocessing_pipeline_components.contour_verification.get_input", return_value='No'):
            path_to_data = os.path.join(data_folder, "RTSTRUCT.dcm")
            verification = conv.verify_if_all_required_contours_are_present(path_to_data, ["vessie", "prostate"])
            self.assertTrue(verification)

    def test_missing_roi(self):
        vocab_file = open(conv.contour_vocab_path, "w")
        json.dump({"prostate": ["Prostate"], "vessie": ["Bladder"], "intestin": ["Intestin"]}, vocab_file)
        vocab_file.close()
        with patch("preprocessing_pipeline_components.contour_verification.get_input", return_value='No'):
            path_to_data = os.path.join(data_folder, "RTSTRUCT.dcm")
            verification = conv.verify_if_all_required_contours_are_present(path_to_data, ["intestin"])
            self.assertFalse(verification)
        with patch("preprocessing_pipeline_components.contour_verification.get_input", return_value='No'):
            path_to_data = os.path.join(data_folder, "RTSTRUCT.dcm")
            verification = conv.verify_if_all_required_contours_are_present(path_to_data, ["intestin", "vessie"])
            self.assertFalse(verification)
        with patch("preprocessing_pipeline_components.contour_verification.get_input", return_value='No'):
            path_to_data = os.path.join(data_folder, "RTSTRUCT.dcm")
            verification = conv.verify_if_all_required_contours_are_present(path_to_data, ["vessie", "intestin"])
            self.assertFalse(verification)

    def tearDown(self) -> None:
        if os.path.exists(conv.contour_vocab_path):
            os.remove(conv.contour_vocab_path)


if __name__ == '__main__':
    unittest.main()
