## Systematic_MC_dose_recalculation

This repository contains the code used to perform the systematic Monte Carlo dose recalculation (currently only supporting LDR brachytherapy)
presented in the following publication:

-Citation to be added-

Since Monte Carlo simulation of clinical cases are often hard to come by, the aim of this code is to provide a framework to perform systematic Monte Carlo dose recalculation.
The code is designed to be as modular as possible, allowing the user to easily add new components to the pipeline.
The pipeline is designed to be used with Docker images, but can also be used with locally installed Monte Carlo codes.
The pipeline can be used with TOPAS and egs_brachy, but can be  adapted to other Monte Carlo codes. Finally, simulations
based on the TG43 and TG186 formalism of LDR brachytherapy are supported for both TOPAS and egs_brachy.

**NOTICE : This pipeline comes with no warranty. It is the user's responsibility to validate the results obtained with this pipeline.
PLEASE DO NOT USE LIKE A BLACK BOX.**

## License

The Systematic_MC_dose_recalculation code is copyrighted Samuel Ouellet. Systematic_MC_dose_recalculation is distributed as free software according to the terms
of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option), any later
version (http://www.gnu.org/licenses/).

## Documentation
The Monte Carlo dose recalculation workflow was split into four components, the
treatment context extractor, the simulation input file generator, the simulation launcher,
and finally, the output formatter. Shown in the figure, the entire pipeline was designed
to be a self-contained application with only DICOMs as both inputs and outputs. It is
important to note that all the clinical data fed to the pipeline has been fully conformed
to the DICOM standard beforehand.

![alt text](./structure_recalculation_pipeline.png?raw=true)

Each component of the pipeline is represented by a Class, contained in a separate Python file within the components folder.
Each component classes have different methods which differentiates what type of component to be used (ex for InputFileGenerators,
one can use it to generate TOPAS input files or egs_brachy input files). Each component class have only one public method,
which always has the type of component, the input, and the output folders as arguments. The first argument is the one
selecting which specific type of component (which method) to use. All the parameters needed for
each component class are set using **kwargs at the construction of the object. In the main python file (automatic_recalculation_workflow.py),
the different components are chained together to form the pipeline. First, all the components are constructed with the appropriate
parameters. Then, the main method of each components are called one after the other on each patient folder contained in the input folder.

To implement a new type of component, one must implement a new method in the appropriate component class. The name of the method
must then be added to the list of available methods in the main method of the component class. Given an input and output folder,
one must provide the needed files or objects for the following component to work, which is shared via the input and output folders of each components.
In order to keep this pipeline as simple as possible, it is recommended to develop python libraries,
which can then be imported into the pipeline. Such libraries have been developed or reused for the different components.

1.DicomExtractors
- https://gitlab.chudequebec.ca/sam23/dicom_rt_context_extractor (developed in this work)
- https://gitlab.chudequebec.ca/sam23/prostatecalcificationsegmentation (developed in this work)

2.InputFileGenerators
- https://gitlab.chudequebec.ca/sam23/topasfilegenerator (developed in this work)
- https://gitlab.chudequebec.ca/sam23/egs_brachy_file_generator (developed in this work)

3.SimulationLaunchers: In this case, Docker images were build to run the simulations.
- https://hub.docker.com/repository/docker/saoue66/topas/general
- https://hub.docker.com/repository/docker/saoue66/egs_brachy/general

4.OutputFormatters
- https://gitlab.chudequebec.ca/sam23/mcdose2dicom (developed in this work)
- https://gitlab.chudequebec.ca/sam23/dicom-sr-builder (developed in this work)
- https://github.com/markusbaker/py3ddose (reused in this work)
- https://pypi.org/project/topas2numpy/ (reused in this work)


### Usage
#### Setting up the pipeline

The first thing to consider when using the pipeline is the input data. The DICOMS RT files
must be organized in patient folders. As for the content of the patient folder, you have two
options. The first option is to have a folder hierarchy associated to the different DICOM
levels, being the study, series, and instance. So you should end up with folders associated
to each study, which contains folder representing the series, while they contain all the files.
The second option is to have all the DICOM RT files in the same folder. In this case, the 
pipeline will automatically reproduce the first option hierarchy. This is done by
setting the RESTRUCTURING_FOLDERS to True in the automatic_recalculation_workflow.py file.
The pipeline should be compatible with all DICOMs that follow the DICOM standard. However,
if this is not the case, the pipeline could be crashing at the extraction level, returning None
instead of the expected object. In this case, the DICOMs must be fixed before using the pipeline.

The second is to produce a dictionary to map all different structure names to a common name.
This is done by creating a json file containing the mapping. This file is located
in venv/Lib/site-packages/dicom_rt_context_extractor/storage_objects/storing_files/contour_vocabulary.json,
which should be either in your virtual environment (venv) or in your python installation folder. If you are using
the Docker image to run teh pipeline, we recommend to either add line to automatic_recalculation_workflow.py
to modify the venv/Lib/site-packages/dicom_rt_context_extractor/storage_objects/storing_files/contour_vocabulary.json
file or to fork the dicom_rt_context_extractor repository to modify the file directly and use that version of
the package in the requirements.txt . (Sorry, this is inefficient, but the maintenance of multiple packages made during a MSc. research project
is limited by the manpower...). At least the material mapping was done efficiently!


The third thing to consider is the access to the Monte Carlo codes. These con be either installed locally
or used via Docker images. If the Monte Carlo codes are installed locally, the path to the executable used
to launch simulations must be provided. For TOPAS, we recommend changing the executable path in the SimulationRunners.
For EGS_brachy, the executable path must be provided in the automatic_recalculation_workflow.py file and the egs_brachy
command should be accessible from any terminal (the commands in the entrypoint.sh could inspire you). If
If the Monte Carlo codes are used via Docker images (https://hub.docker.com/repository/docker/saoue66/topas/general,https://hub.docker.com/repository/docker/saoue66/egs_brachy/general),
the Docker images must be run instead of the executables in the SimulationRunners. 

IMPORTANT: We recommend using the Docker to run the entire pipeline, which is much simpler! For guidance,
refer to the Dockerized usage section.

The last thing to consider are the parameters of the pipeline. Theses parameters are set in the automatic_recalculation_workflow.py file.
Most variables are self-explanatory. The only thing to consider is the parameters of the different components. In this case,
comments are provided near the parameters that often need to be changed. As for the others, in-dept knowledge of the components
may be required to change them.

#### Local usage
IMPORTANT: We recommend using the Docker to run the entire pipeline, which is much simpler! For guidance, see the Dockerized usage section.

First, ensure that you have python 3.8 available. Then, clone the repository.
    
```bash
git clone https://gitlab.chudequebec.ca/sam23/dicom_rt_calcification_pipeline.git
```

Then install the requirements in a virtual environment. (path formats may change depending on host operating system)

```bash
cd dicom_rt_calcification_pipeline
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Then, once all the parameters are set in the automatic_recalculation_workflow.py file, the pipeline can be run using the following command:

```bash
python automatic_recalculation_workflow.py input_filder_path output_folder_path
```

#### Dockerized usage
First, clone the repository.
    
```bash
git clone https://gitlab.chudequebec.ca/sam23/dicom_rt_calcification_pipeline.git
```

To Dockerized the Systematic_MC_dose_recalculation, one must first have Docker installed and 
running on the machine (see https://docs.docker.com/engine/install/). To build the Docker image,
one can use the following commands (path format may change depending on host operating system):

```bash
docker build . -f docker_files\DockerfileTopas -t image_name:tag_name
docker build . -f docker_files\DockerfileEgsBrachy -t image_name:tag_name
```

Depending on the Monte Carlo code to be used, one must use the appropriate Dockerfile. Please note that
the image built will be based on the current version of the code. If the code is locally changed, the 
image must be rebuilt. To run the Docker image, one can use the following command:

```bash
docker run -v {path_to_patient_data_on_host_machine}:/patients:ro -v {path_to_output_folder_on_host_machine}:/output image_name:tag_name /patients /output
```

The first volume mount is used to mount the patient data folder on the host machine to the /patients folder.
The second volume mount is used to mount the output folder on the host machine to the /output folder. Mounting
folders means that the files in the folders will be accessible from within the Docker container. The last two
arguments are the paths to the patient data folder and the output folder within the Docker container.

IMPORTANT: Since the cluster used to run the Docker images when developping this pipeline could
only provide two arguments to the Docker run command (being input and output folder), the docker images were designed
to match this requirement. One could change the entrypoint.sh script to add more arguments to the Docker run command
which could then be used to set the different parameters needed in the automatic_recalculation_workflow.py file.
Thus, making the pipeline more flexible and reducing the numbers of docker builds needed for different configurations.

In case one wants to interact with the Docker container via the terminal, one can use the following command:

```bash
docker run -it --entrypoint /bin/bash -v {path_to_patient_data_on_host_machine}:/patients:ro -v {path_to_output_folder_on_host_machine}:/output image_name:tag_name
```

Many example docker images can be found on the Docker Hub (https://hub.docker.com/repository/docker/saoue66/monte_carlo_dose_recalculation_pipeline_ldr_brachy/general/). 
All example images are made to simulate 1e5 photons.

To use one of them, one can use the following command:

```bash
docker pull saoue66/monte_carlo_dose_recalculation_pipeline_ldr_brachy:tag_name
```

Once the image is pulled, one can run it using the following command:

```bash
docker run -v {path_to_patient_data_on_host_machine}:/patients:ro -v {path_to_output_folder_on_host_machine}:/output saoue66/monte_carlo_dose_recalculation_pipeline_ldr_brachy:tag_name /patients /output
```


## Contact

For more information about Systematic_MC_dose_recalculation please contact:

- Samuel Ouellet <samuel.ouellet.10@ulaval.ca>
- Luc Beaulieu <luc.beaulieu@phy.ulaval.ca>

## Citing Systematic_MC_dose_recalculation

Citations of DICOM_RT_context_extractor use the following reference:

Ouellet, S. et al. A Monte Carlo dose recalculation pipeline for durable datasets: an I-125 LDR prostate brachytherapy use case.   Physics in Medicine & Biology 68, 235001 (2023).

## Reporting Bugs

Please report any issues you find using the [issue
tracker on GitLab](https://gitlab.chudequebec.ca/sam23/dicom_rt_calcification_pipeline/-/issues)

## Contributing to DICOM_RT_context_extractor

Bug fixes and additional features are welcomed via pull requests on
Gitlab.

For unfamiliar contributors, here are the steps to follow to contribute to the
project:
1. Fork the project
2. Create a new branch
3. Make your changes
4. Commit your changes to your branch
5. Push your changes to your fork
6. Create a merge request
7. Wait for the merge request to be accepted

## Commit history (change log)

The complete commit history (i.e., change log) can be consulted https://gitlab.chudequebec.ca/sam23/dicom_rt_calcification_pipeline/-/commits/master.