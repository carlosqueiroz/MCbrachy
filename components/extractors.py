import os

from dicom_rt_context_extractor.sources_information_extraction import extract_all_sources_informations
from dicom_rt_context_extractor.utils.search_instance_and_convert_coord_in_pixel import find_modality_in_folder
from prostate_calcification_segmentation.calcification_segmentation import segmenting_calcification


class DicomExtractors:
    def __init__(self, **kwargs):
        """

        :param input_file_folder:
        :param kwargs: for egs_brachy, kwargs must have nb_treads (int), waiting_time (float) and
                       egs_brachy_home (str)
        """
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])

        self.permanent_implant_brachy = self._extract_permanent_implant_brachy_context
        self.hdr_brachy = self._extract_hdr_brachy_context
        self.ldr_brachy = self._extract_ldr_brachy_context

    def _extract_permanent_implant_brachy_context(self, input_folder: str, output_folder: str) -> str:
        build_structures = True
        if hasattr(self, "build_structures"):
            build_structures = self.__getattribute__("build_structures")
        series_description = None
        if hasattr(self, "series_description"):
            series_description = self.__getattribute__("series_description")

        rt_plan_path = find_modality_in_folder("RTPLAN", input_folder)
        plan = extract_all_sources_informations(rt_plan_path)
        if build_structures:
            plan.extract_structures(input_folder)
            if hasattr(self, "segmentation"):
                if "prostate_calcification" in self.__getattribute__("segmentation"):
                    self._segment_prostate_calcification(plan, input_folder, output_folder)
            if hasattr(self, "recreate_struct"):
                if self.recreate_struct:
                    plan.structures.recreate_rt_struct_from_current_structure(series_description,
                                                                              os.path.join(output_folder,
                                                                                           "recreated_rt_struct.dcm"))
        plan.extract_dosimetry(input_folder)
        return plan

    def _extract_hdr_brachy_context(self, input_folder: str, output_folder: str) -> str:
        pass

    def _extract_ldr_brachy_context(self, input_folder: str, output_folder: str):
        pass

    def extract_context_from_dicoms(self, treatment_modality: str, input_folder: str, output_folder: str):
        assert treatment_modality in ["permanent_implant_brachy", "hdr_brachy", "ldr_brachy"]
        return self.__getattribute__(treatment_modality)(input_folder, output_folder)

    def _segment_prostate_calcification(self, plan, input_folder: str, output_folder):
        prostate_calcification_mask = segmenting_calcification(plan, 2.0, input_folder)
        plan.structures.add_mask_from_3d_array(prostate_calcification_mask,
                                               roi_name="prostate_calcification",
                                               observation_label="masking sources with cylindrical masks with"
                                                                 " thresholding",
                                               segmentation_method=1, add_to_original_rt_struct_file=False,
                                               saving_path=os.path.join(output_folder,
                                                                        f"updated_{plan.patient}_{plan.study}"
                                                                        f"_RTSTRUCT.dcm"),
                                               can_be_filled=False
                                               )
