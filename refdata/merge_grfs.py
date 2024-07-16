# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 10:20:26 2024

@author: frekle
"""
import numpy as np
import pandas as pd

## you also need the header!

custom_header = """DataType=double
version=3
OpenSimVersion=4.1
endheader
"""

custom_header_in_degrees = """DataType=double
version=3
OpenSimVersion=4.1
inDegrees=true
endheader
"""

#different version of pandas

args= {}
if int(pd.__version__.split(".")[0]) > 1 or int(pd.__version__.split(".")[0]) == 1 and int(pd.__version__.split(".")[1]) >= 5:
    args = {"lineterminator":"\n"}
else:
    args = {"line_terminator":"\n"}



def combine_and_save_2_files_and_remove_offset_from_ik(prefix):
    df_ik = pd.read_csv(f"{prefix}ik.sto", sep="\t", header=[4])
    df_ik = df_ik.round({'time':2})
    df_ik = df_ik.set_index("time")
    ##also remove wall time because opensim does not use correct precision strings for time...
    df_ik.index-=df_ik.index[0]
    
    with open(f"{prefix}ik_correct_time.sto",'w') as file:
        file.write(custom_header)
        df_ik.to_csv(file, sep="\t", **args)

    ## actually convert the columns to degrees
    columns_in_rads = ['pelvis_tilt','pelvis_list','pelvis_rotation','hip_flexion_r','hip_adduction_r','hip_rotation_r','hip_flexion_l','hip_adduction_l','hip_rotation_l','lumbar_extension','lumbar_bending','lumbar_rotation','knee_angle_r','knee_angle_l','ankle_angle_r','ankle_angle_l','subtalar_angle_r','subtalar_angle_l','mtp_angle_r','mtp_angle_l']

    df_ik[columns_in_rads] = df_ik[columns_in_rads].multiply(180/np.pi)

    with open(f"{prefix}ik_correct_time_in_degrees.sto",'w') as file:
        file.write(custom_header_in_degrees)
        df_ik.to_csv(file, sep="\t", **args)
    
    columns_to_remove = ['hip_adduction_r','hip_rotation_r','hip_adduction_l','hip_rotation_l']

    df_ik[columns_to_remove] = df_ik[columns_to_remove].multiply(0)
    
    with open(f"{prefix}ik_correct_time_in_degrees_zero_hip_non_sagittal.sto",'w') as file:
        file.write(custom_header_in_degrees)
        df_ik.to_csv(file, sep="\t", **args)
    
    df1 = pd.read_csv(f"{prefix}grfLeft.sto", sep="\t", header=[4])
    df1 = df1.loc[:,['time',
           '1_ground_force_vx', '1_ground_force_vy', '1_ground_force_vz',
           '1_ground_force_px', '1_ground_force_py', '1_ground_force_pz',
           '1_ground_torque_x', '1_ground_torque_y', '1_ground_torque_z']]
    df1 = df1.round({'time':2})
    df1 = df1.set_index("time")
    df2 = pd.read_csv(f"{prefix}grfRight.sto", sep="\t", header=[4])
    df2 = df2.loc[:,['time',
           'ground_force_vx', 'ground_force_vy', 'ground_force_vz',
           'ground_force_px', 'ground_force_py', 'ground_force_pz',
           'ground_torque_x', 'ground_torque_y', 'ground_torque_z']]
    df2 = df2.round({'time':2})
    df2= df2.set_index("time")

    df = pd.concat([df1,df2],axis=1)
    
    ##also remove wall time because opensim does not use correct precision strings for time...
    df.index-=df.index[0]
    
    with open(f"{prefix}grf_Combi.sto",'w') as file:
        file.write(custom_header)
        df.to_csv(file, sep="\t", **args)


#prefix= "2024-03-07-17-38-05s02_id_walking_filtered_SCRIPT0_1"

import glob, os

import argparse

def run(directory):
    #os.chdir("./")
    os.chdir(directory)
    list_grfs= []

    for file in glob.glob("*grfLeft.sto"):
        list_grfs.append(file.split("grfLeft.sto")[0])
        
        print(file)

    print(list_grfs)

    for prefix_ in list_grfs:
        combine_and_save_2_files_and_remove_offset_from_ik(prefix_)
    #df_ =pd.merge(df1, df2, left_index=True, right_index=True, how='outer')


if __name__== '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', dest='dir', type=str, help='Directory with the files you want to make more opensimable')
    args = parser.parse_args()

    if not (args.dir):
        parser.print_help()
        exit(1)
    
    run(args.dir)
