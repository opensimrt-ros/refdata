#!/usr/bin/env sh

######################################################################
# @author      : frederico (frederico@asoldasme)
# @file        : get_data
# @created     : tisdag jan 07, 2025 11:36:27 CET
#
# @description : 
######################################################################

wget https://springernature.figshare.com/ndownloader/files/22063191 -v -O GRF_F_V_PRO_left.csv
wget https://springernature.figshare.com/ndownloader/files/22063119 -v -O GRF_F_V_PRO_right.csv

wget https://springernature.figshare.com/ndownloader/files/22063185 -v -O GRF_F_AP_PRO_left.csv
wget https://springernature.figshare.com/ndownloader/files/22063101 -v -O GRF_F_AP_PRO_right.csv

wget https://springernature.figshare.com/ndownloader/files/22063113 -v -O GRF_F_ML_PRO_left.csv
wget https://springernature.figshare.com/ndownloader/files/22063086 -v -O GRF_F_ML_PRO_right.csv
