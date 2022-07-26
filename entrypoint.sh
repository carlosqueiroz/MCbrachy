#! /bin/bash
export EGS_HOME="/EGSnrc_CLRP/egs_home/"
export EGS_CONFIG="/EGSnrc_CLRP/HEN_HOUSE/specs/linux.conf"
export HEN_HOUSE="/EGSnrc_CLRP/HEN_HOUSE/"
export EGS_BATCH_SYSTEM=at
# . /EGSnrc_CLRP/HEN_HOUSE/scripts/egsnrc_bashrc_additions
# . /EGSnrc_CLRP/HEN_HOUSE/scripts/clrp_bashrc_additions
alias egs_parallel="/EGSnrc_CLRP/HEN_HOUSE/scripts/bin/egs-parallel"
export TOPAS_G4_DATA_DIR=/G4Data
/workflow/venv/bin/python /workflow/automatic_recalculation_workflow.py -o prostate -o vessie -o uretre -o rectum -o calcification -a egs_brachy -s True -r False $1 $2