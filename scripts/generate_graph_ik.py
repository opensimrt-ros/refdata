#!/bin/env python3
import sys, os
sys.path.append("../")
from common import *
from refdata import refdata
import pickle



def run(trial_data_yaml,trial_files_yaml,out_dir):

    this_action_name, actions_to_be_shown,subject_num,weight,skip_trials,trial_dir = get_trial(trial_data_yaml)

    ik_files, grfL_files,grfR_files, id_files, so_files, ik_lower_files, left_times, right_times =get_files(trial_files_yaml)

    action_trials= []
    for trial in ik_files:
        for action_name in actions_to_be_shown:
            if action_name in trial:
                action_trials.append(trial)

    ##idk what to do about this rn
    if False:
        xy_knees_ik = refdata.generate_somejoint_or_muscle_curves(action_trials,[], curve_prefix="ankle_angle")

        xy_knees_list0 = []
        xy_knees_list1 = []
        for name, xy_tuples in xy_time_clippings_left.items():
            xy_knees_list0.append(xy_tuples)    
        for name, xy_tuples in xy_time_clippings_right.items():
            xy_knees_list1.append(xy_tuples)  

    xy_time_clippings_left = build_clipings(ik_files,left_times)
    xy_time_clippings_right = build_clipings(ik_files,right_times)
    xy_clippings_both_ik = (xy_time_clippings_left,xy_time_clippings_right)

    cc = [(refdata.graph_params.get_ik_graph_params(),(3,3)),
          (refdata.graph_params.get_ik_short_graph_params(),(1,3))]

    asRefData = None
    try:
        asRefData = pickle.load( open( os.path.join(trial_dir,f"ik_ref_{this_action_name}_data_s{subject_num}.p"), "rb" ) )
    except:
        pass
    ref = {
            'center':refdata.GaitIKRefData(),
            'vicon': asRefData
            }
    for refref in ref.items():
        for conv_names in cc:
            for std in [True,False]:
                GRAPH_NAME = f'ik_{refref[0]}_ref'

                fdp_graph(action_trials,xy_clippings_both_ik, GRAPH_NAME, subject_num,out_dir,this_action_name,actions_to_be_shown,this_action_name,conv_names=conv_names[0],grid=conv_names[1],std=std, ref=refref[1])

if __name__== "__main__":
    run("trial_data.yaml","pruned_files.yaml","./")



