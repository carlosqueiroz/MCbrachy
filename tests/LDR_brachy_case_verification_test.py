import unittest
import os
import logging
import json
from preprocessing_pipeline_components import LDR_brachy_case_verification as LDR_brachy_check
from root import ROOT
from unittest.mock import patch

test_log_filename = os.path.join(ROOT, r'logs\test_logs.logs')
logging.basicConfig(filename=test_log_filename,
                    format='%(asctime)s [%(levelname)s, %(module)s.%(funcName)s]: %(message)s',
                    filemode='w+',
                    level=logging.DEBUG)

data_folder = os.path.join(ROOT, r'tests\test_data')


class TestVerifyIfBrachyTreatmentType(unittest.TestCase):
    def test_not_RTPLAN(self):
        data_path = os.path.join(data_folder, '1-1.dcm')
        verification = LDR_brachy_check.verify_if_brachy_treatment_type(data_path, "HDR")

        self.assertFalse(verification)

    def test_bad_treatment_plan(self):
        data_path = os.path.join(data_folder, 'HDR.dcm')
        verification = LDR_brachy_check.verify_if_brachy_treatment_type(data_path, "LDR")

        self.assertFalse(verification)

    def test_good_treatment_plan(self):
        data_path = os.path.join(data_folder, 'HDR.dcm')
        verification = LDR_brachy_check.verify_if_brachy_treatment_type(data_path, "HDR")
        self.assertTrue(verification)


class TestVerifyIfSourceCorrespondsToTreatmentType(unittest.TestCase):
    def test_not_RTPLAN(self):
        data_path = os.path.join(data_folder, '1-1.dcm')
        verification = LDR_brachy_check.verify_if_source_corresponds_to_treatment_type(data_path, "HDR")

        self.assertFalse(verification)

    def test_bad_source_for_plan(self):
        data_path = os.path.join(data_folder, 'HDR.dcm')
        verification = LDR_brachy_check.verify_if_source_corresponds_to_treatment_type(data_path, "LDR")

        self.assertFalse(verification)

    def test_good_source_for_plan(self):
        data_path = os.path.join(data_folder, 'HDR.dcm')
        verification = LDR_brachy_check.verify_if_source_corresponds_to_treatment_type(data_path, "HDR")
        self.assertTrue(verification)


class TestAddExpressionToTreatmentVocab(unittest.TestCase):
    def setUp(self):
        test_vocab_path = os.path.join(data_folder, "test_vocab.json")
        vocab_file = open(test_vocab_path, "w")
        json.dump({}, vocab_file)
        vocab_file.close()
        LDR_brachy_check.treatment_vocab_path = test_vocab_path

    def test_adding_category_when_empty(self):
        with patch("preprocessing_pipeline_components.LDR_brachy_case_verification.get_input", return_value='Yes'):
            LDR_brachy_check.add_expression_to_treatment_vocab("Prostate", {})
        treatment_site_vocabulary_file = open(LDR_brachy_check.treatment_vocab_path, "r")
        treatment_site_vocabulary = json.loads(treatment_site_vocabulary_file.read())
        treatment_site_vocabulary_file.close()
        self.assertEqual(treatment_site_vocabulary, {"Yes": ["Prostate"]})
        with patch("preprocessing_pipeline_components.LDR_brachy_case_verification.get_input", return_value='No'):
            LDR_brachy_check.add_expression_to_treatment_vocab("Vessie", {})
        treatment_site_vocabulary_file = open(LDR_brachy_check.treatment_vocab_path, "r")
        treatment_site_vocabulary = json.loads(treatment_site_vocabulary_file.read())
        treatment_site_vocabulary_file.close()
        self.assertEqual(treatment_site_vocabulary, {})

    def test_adding_category_when_not_empty(self):
        with patch("preprocessing_pipeline_components.LDR_brachy_case_verification.get_input", return_value='Yes'):
            LDR_brachy_check.add_expression_to_treatment_vocab("Rectum", {"Prostate": ["Prostate", "prostate"],
                                                                          "Vessie": ["Vessie", "vessie"]})

        treatment_site_vocabulary_file = open(LDR_brachy_check.treatment_vocab_path, "r")
        treatment_site_vocabulary = json.loads(treatment_site_vocabulary_file.read())
        treatment_site_vocabulary_file.close()
        self.assertEqual(treatment_site_vocabulary, {"Prostate": ["Prostate", "prostate"],
                                                     "Vessie": ["Vessie", "vessie"], "Yes": ["Rectum"]})

        with patch("preprocessing_pipeline_components.LDR_brachy_case_verification.get_input", return_value='Yes'):
            LDR_brachy_check.add_expression_to_treatment_vocab("rectum", {"Prostate": ["Prostate", "prostate"],
                                                                          "Vessie": ["Vessie", "vessie"],
                                                                          "Yes": ["Rectum"]})
        treatment_site_vocabulary_file = open(LDR_brachy_check.treatment_vocab_path, "r")
        treatment_site_vocabulary = json.loads(treatment_site_vocabulary_file.read())
        treatment_site_vocabulary_file.close()

        self.assertEqual(treatment_site_vocabulary, {"Prostate": ["Prostate", "prostate"],
                                                     "Vessie": ["Vessie", "vessie"], "Yes": ["Rectum", "rectum"]})

    def tearDown(self) -> None:
        if os.path.exists(LDR_brachy_check.treatment_vocab_path):
            os.remove(LDR_brachy_check.treatment_vocab_path)


class TestVerifyTreatmentSite(unittest.TestCase):
    def setUp(self):
        test_vocab_path = os.path.join(data_folder, "test_vocab.json")
        vocab_file = open(test_vocab_path, "w")
        json.dump({}, vocab_file)
        vocab_file.close()
        LDR_brachy_check.vocab_path = test_vocab_path

    def test_not_RTPLAN(self):
        data_path = os.path.join(data_folder, '1-1.dcm')
        verification = LDR_brachy_check.verify_treatment_site(data_path, "HDR")

        self.assertFalse(verification)

    def test_treatment_site_in_vocab_and_in_specified_category(self):
        vocab_file = open(LDR_brachy_check.treatment_vocab_path, "w")
        json.dump({"prostate": ["Prostate"]}, vocab_file)
        vocab_file.close()
        data_path = os.path.join(data_folder, 'HDR.dcm')
        verification = LDR_brachy_check.verify_treatment_site(data_path, "prostate", True)
        self.assertTrue(verification)

    def test_treatment_site_in_vocab_and_in_wrong_category(self):
        vocab_file = open(LDR_brachy_check.treatment_vocab_path, "w")
        json.dump({"prostate": ["Prostate"], "vessie": ["Vessie"]}, vocab_file)
        vocab_file.close()
        data_path = os.path.join(data_folder, 'HDR.dcm')
        verification = LDR_brachy_check.verify_treatment_site(data_path, "vessie", True)
        self.assertFalse(verification)

    def test_treatment_site_not_in_vocab_with_vocab_update_disabled(self):
        vocab_file = open(LDR_brachy_check.treatment_vocab_path, "w")
        json.dump({"prostate": ["Vessie"]}, vocab_file)
        vocab_file.close()
        data_path = os.path.join(data_folder, 'HDR.dcm')
        verification = LDR_brachy_check.verify_treatment_site(data_path, "prostate", True)
        self.assertFalse(verification)

    def test_treatment_site_not_in_vocab_with_vocab_update_enabled(self):
        vocab_file = open(LDR_brachy_check.treatment_vocab_path, "w")
        json.dump({"Yes": ["Vessie"]}, vocab_file)
        vocab_file.close()
        data_path = os.path.join(data_folder, 'HDR.dcm')

        with patch("preprocessing_pipeline_components.LDR_brachy_case_verification.get_input", return_value='No'):
            verification = LDR_brachy_check.verify_treatment_site(data_path, "No")
            self.assertFalse(verification)

        vocab_file = open(LDR_brachy_check.treatment_vocab_path, "w")
        json.dump({"Yes": ["Vessie"], "No": ["Vessie"]}, vocab_file)
        vocab_file.close()

        with patch("preprocessing_pipeline_components.LDR_brachy_case_verification.get_input", return_value='Yes'):
            verification = LDR_brachy_check.verify_treatment_site(data_path, "Yes")
            self.assertTrue(verification)

        vocab_file = open(LDR_brachy_check.treatment_vocab_path, "w")
        json.dump({"Yes": ["Vessie"], "No": ["Vessie"]}, vocab_file)
        vocab_file.close()

        with patch("preprocessing_pipeline_components.LDR_brachy_case_verification.get_input", return_value='Yes'):
            verification = LDR_brachy_check.verify_treatment_site(data_path, "No")
            self.assertFalse(verification)

    def tearDown(self) -> None:
        if os.path.exists(LDR_brachy_check.treatment_vocab_path):
            os.remove(LDR_brachy_check.treatment_vocab_path)


if __name__ == '__main__':
    unittest.main()
