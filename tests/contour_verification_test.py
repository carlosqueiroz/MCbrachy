import unittest
import os
import logging
import json
from preprocessing_pipeline_components import contour_verification as conv
from root import ROOT
from unittest.mock import patch

test_log_filename = os.path.join(ROOT, r'logs\test_logs.logs')
logging.basicConfig(filename=test_log_filename,
                    format='%(asctime)s [%(levelname)s, %(module)s.%(funcName)s]: %(message)s',
                    filemode='w+',
                    level=logging.DEBUG)

data_folder = os.path.join(ROOT, r'tests\test_data')


class TestAddExpressionToContourVocab(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
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


if __name__ == '__main__':
    unittest.main()
