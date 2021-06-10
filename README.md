DICOM_RT_calcification_pipeline
=============
This project is separated into 2 parts. The first one is the preprocessing pipeline. It is mainly
used to parse a huge amount of DICOM datas in order to select the desired type of DICOMs. In this project's
case, the utimate objective was to select LDR prostate brachytherapy with and without prostate calcification.
But it can also be used in many other cases. The second one is the post processing. In this case, now tha the data
has carefully been selected, all the essential information needed for Monte Carlo dose calculation has to be
extracted from the DICOMs. Unfortunatly, this second part hasn't been developped yet.

## Preprocessing pipeline

#### LDR Brachytherapy case verification

This first part of the preprocessing pipeline verifies if the information located in the DICOM RT PLAN
indicate a low dose rate prostate brachytherapy. To do so, the user must first use the verify_if_brachy_treatment_type
function in order to verify if the treatment correspond to the desired brachytherapy treatment type. Here is an example
for high dose rate brachytherapy

```sh
import LDR_brachy_case_verification

DICOM_PATH = r"rt_plan.dcm"

is_hdr = LDR_brachy_case_verification.verify_if_brachy_treatment_type(DICOM_PATH, "HDR")

```
If desired, the user can afteward verify if all the radiactive sources are in the source_verification (in LDR_brachy_case_verification file)
list associated to the treatment type if only one of the sources does not fit what is expected, this method will return false. Finally,
The last method in this file, verify_treatment_site(), allows the user to validate that the treatment site is the desired one.
Because the same information can be specified in the DICOM in many ways, this method uses a vocabulary dictionary that
should look like this:

```sh
{"prostate": ["Prostate", "prostate1", "prostate"], "bladder": ["Bladder", "Vessie", "bladder"]}
```

In this case, if the user wants a case of prostate brachytherapy, all terms in ["Prostate", "prostate1", "prostate"]
will be accepted. If, for instance, the DICOM has a treatment site of "Rectum" and the disable_vocabulary_update is set
to false, the add_expression_to_treatment_vocab() method will ask the user in which category should Rectum go into. If 
the user specifies an existing category such as prostate, the method will add Rectum in the prostate list of terms.
If the user specifies an nonexisting category, the method will ask whether the user wants to create a new one.
If the user creates the new category named rectum, the vocabulary should become:
```sh
{"prostate": ["Prostate", "prostate1", "prostate"], "bladder": ["Bladder", "Vessie", "bladder"], "rectum": ["Rectum"]}
```
In other words, the user will be asked whether or not to add any expression not found in any category of the vocabulary.
Example of usage:
```sh
import LDR_brachy_case_verification

DICOM_PATH = r"rt_plan.dcm"

is_prostate = LDR_brachy_case_verification.verify_treatment_site(DICOM_PATH, "prostate", False)

```

##### Contour verification

##### Calcification verification

##### Data Tracker

##### Anonymization



## Postprocessing pipeline

Not developped yet