from string import Template

TG186_PATIENT = Template(
    """
##### DICOM PATIENT #####
s:Ge/PatientGroup/Type   = "Group"
s:Ge/PatientGroup/Parent = "World"


s:Ge/Patient/DataType  = "int"
s:Ge/Patient/InputDirectory = "${input_directory}"
s:Ge/Patient/InputFile = "${input_file_name}"
s:Ge/Patient/Type  = "TsImageCube"
s:Ge/Patient/Parent = "PatientGroup"
s:Ge/Patient/Material = "G4_WATER"
d:Ge/Patient/TransX             = ${transx} mm
d:Ge/Patient/TransY             = ${transy} mm
d:Ge/Patient/TransZ             = ${transy} mm
d:Ge/Patient/RotX               = ${rotx} deg
d:Ge/Patient/RotY               = ${roty} deg
d:Ge/Patient/RotZ               = ${rotz} deg
i:Ge/Patient/NumberOfVoxelsX  =  ${nb_of_columns}
i:Ge/Patient/NumberOfVoxelsY  =  ${nb_of_rows}
iv:Ge/Patient/NumberOfVoxelsZ = 1 ${nb_of_slices}
d:Ge/Patient/VoxelSizeX       = ${voxel_size_x} mm
d:Ge/Patient/VoxelSizeY       = ${voxel_size_y} mm
dv:Ge/Patient/VoxelSizeZ       = 1 ${voxel_size_z} mm

#### TG186 Material Assignment
s:Ge/Patient/ImagingToMaterialConverter = "MaterialTagNumber"

iv:Ge/Patient/MaterialTagNumbers = ${tag_numbers}
sv:Ge/Patient/MaterialNames = ${material_names}
####
""")