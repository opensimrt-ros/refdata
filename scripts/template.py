#!/bin/env python3
import sys, os
sys.path.append("../")
from common import *
from refdata import refdata


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

    xy_time_clippings_left = build_clipings(grfL_files,left_times)
    xy_time_clippings_right = build_clipings(grfR_files,right_times)
    xy_clippings_both_ik = (xy_time_clippings_left,xy_time_clippings_right)

    GRAPH_NAME = "Template"
    SIZE = "3x3"
    STD=True

    save_graph(subject_num,out_dir,this_action_name,"Template","3x3",std=True)

if __name__== "__main__":
    run("trial_data.yaml","pruned_files.yaml","./")



