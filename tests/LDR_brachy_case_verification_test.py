import unittest
import os
import logging
import pydicom
from preprocessing_pipeline_components import LDR_brachy_case_verification as LDR_brachy_check
from root import ROOT

test_log_filename = os.path.join(ROOT, r'logs\test_logs')
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


if __name__ == '__main__':
    unittest.main()
