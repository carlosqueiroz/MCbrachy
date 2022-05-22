#! /bin/bash
. /EGSnrc_CLRP/HEN_HOUSE/scripts/egsnrc_bashrc_additions
. /EGSnrc_CLRP/HEN_HOUSE/scripts/clrp_bashrc_additions
./venv/bin/python automatic_recalculation_workflow.py -o prostate -o vessie -o uretre -o rectum -o calcification -a egs_brachy -s True -r False $1 $2