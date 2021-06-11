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
Now that we know whether or not it is a LDR prostate brachytherapy, it is now time to verify if
the desired contours are present in the DICOM RT STRUCT. Again, the expression used to specify an
organ or anatomical structure can vary. This is why the contour verification also uses a vocabulary
dictionary just like in the search of treatment site. Before explaining how verify_if_all_required_contours_are_present() works
, one should understand how verify_if_roi_in_desired_rois() works. Given a list of requires rois desired_rois,
this method verifies if the given roi is amonst the expression of one desired_roi. If yes, this method will return a tuple
of True and the index associated to the desired roi corresponding to the given roi. For instance,
```sh
import contour_verifiction

in_rois, index = contour_verifiction.verify_if_roi_in_desired_rois("Prostate", ["rectum", "prostate"], False)

```
Given the contour vocab dict
```sh
{"prostate": ["Prostate", "prostate1", "prostate"], "bladder": ["Bladder", "Vessie", "bladder"], "rectum": ["Rectum"]}
```
should return True and 1. In a case where the roi is in the vacab dict but not associated to any of the desired rois,
the method will return False and -1. In a case where the given roi is not even in the vocab dict, the user will be asked
where to add that new expression.

The verify_if_all_required_contours_are_present() simply calls the verify_if_roi_in_desired_rois() for every roi
found in the DICOM RT SRTUCT. Every time verify_if_all_required_contours_are_present() returns True, the verify_if_all_required_contours_are_present()
method removes the desired contour at the given index until there are no desired rois left in the list. If
the desired rois list becomes empty, the method returns True, but if the desired rois list is not 
empty after looking at all the rois of the DICOM, the method returns False.



##### Calcification verification

The last step is to identify calcification. To do so, it is necessary to look at the images.
The plot_whole_series() method allows the user to view any 3d images form the DICOMS. More 
precisely, this method plots a single slice of the 3d image at a time. A sliding button has been added 
to the plot in order to interact with the plot and be able to navigate from one slice to the other.
In the pipeline, knowing if something is shown is important to keep the pipeline flow from stopping.
This is why the plot_whole_series() returns True when something was shown to the user and False when something
goes wrong. Here is an example of an US image shown using plot_whole_series().

<p align="center">
<img src="https://gitlab.physmed.chudequebec.ca/sam23/dicom_rt_calcification_pipeline/raw/master/Images/example_US.png" width="600">
 </p>

The method manual_selection_of_calcification() simply uses the plot_whole_series()
method in order to show the DICOM 3D image to the user. As soon the user closes the image,
the user will be asked, through the command prompt, whether or not there was calcification.
If the answer is "Yes", the method will return True. On the other hand, if the answer is "No',
the method will return False. If the plot_whole_series() returns False, the method won't prompt
anything and simply return False

In order to verify if there is any calcification in an entire study, the
is_there_prostate_calcification_in_study() method simply calls manual_selection_of_calcification()
on every series containing images until one of them has calcification. If the method goes through
all of the series without ever receiving a positive answer, it will return False.

##### Data Tracker





##### Anonymization



## Postprocessing pipeline

Not developped yet