#! /bin/bash
. /EGSnrc_CLRP/HEN_HOUSE/scripts/egsnrc_bashrc_additions
. /EGSnrc_CLRP/HEN_HOUSE/scripts/clrp_bashrc_additions
alias egs_parallel="/EGSnrc_CLRP/HEN_HOUSE/scripts/bin/egs-parallel"
alias topas="/topas/topas/bin/topas"
./venv/bin/python automatic_recalculation_workflow.py -o prostate -o vessie -o uretre -o rectum -o calcification -a egs_brachy -s True -r False $1 $2