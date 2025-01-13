#!/bin/env python3
import sys, os
sys.path.append("../")
from common import *
from refdata import refdata


def run(trial_data_yaml,trial_files_yaml,out_dir):

    this_action_name, actions_to_be_shown,subject_num,weight,skip_trials,trial_dir = get_trial(trial_data_yaml)

    ik_files, grfL_files,grfR_files, id_files, so_files, ik_lower_files, left_times, right_times =get_files(trial_files_yaml)



    action_trials_left= []
    for trial in grfL_files:
        for action_name in actions_to_be_shown:
            if action_name in trial:
                action_trials_left.append(trial)
    logger.info(action_trials_left)
    action_trials_right= []
    for trial in grfR_files:
        for action_name in actions_to_be_shown:
            if action_name in trial:
                action_trials_right.append(trial)
    logger.info(action_trials_right)


    xy_idk_grfL = refdata.generate_somejoint_or_muscle_curves(action_trials_left,[],
                                                              curve_prefix="1_ground_force_vy",
                                                             conv_names= 
                                                              refdata.graph_params.generate_grf_conv_names(0,weight),
                                                              left_or_right=0)
    xy_idk_grfR = refdata.generate_somejoint_or_muscle_curves(action_trials_right,[],
                                                              curve_prefix="ground_force_vy",
                                                             conv_names= 
                                                              refdata.graph_params.generate_grf_conv_names(1,weight),
                                                              left_or_right=1)


    xy_time_clippings_left = build_clipings(grfL_files,left_times)
    xy_time_clippings_right = build_clipings(grfR_files,right_times)
    logger.info(xy_time_clippings_left)
    logger.info(xy_time_clippings_right)

    ##show some left side curve
    if False: #True:
        for name, xy_tuples in xy_idk_grfL[0].items():
            if name == action_trials_left[2]:
                #plt.title(name)
                print(name)
                refdata.clip_curve_test(xy_tuples[0],xy_tuples[1], time_clips = xy_time_clippings_left[name] )

    ##show some right side curve            
    if False: #True:
        for name, xy_tuples in xy_idk_grfR[1].items():
            if name == action_trials_right[0]:
                #plt.title(name)
                print(name)
                refdata.clip_curve_test(xy_tuples[0],xy_tuples[1], time_clips = xy_time_clippings_right[name] )
                
    ##This has to run

    xy_clippings_both = (xy_time_clippings_left,xy_time_clippings_right)
    print(xy_clippings_both[0])
    print(xy_clippings_both[1])

    ## Shows all trials
    if False: #True:
        for name, xy_tuples in xy_idk_grfL[0].items():    
            for action_name in actions_to_be_shown:
                if action_name in name:
                    print(name+r" left")        
                    refdata.clip_curve_test(xy_tuples[0],xy_tuples[1], time_clips = xy_time_clippings_left[name] )
        for name, xy_tuples in xy_idk_grfR[1].items():
            for action_name in actions_to_be_shown:
                if action_name in name:
                    print(name+r" right")        
                    refdata.clip_curve_test(xy_tuples[0],xy_tuples[1], time_clips = xy_time_clippings_right[name] )

    grf_ref_data = refdata.GRFWalkingRefData()

    conv_names = {}
    conv_names.update(refdata.graph_params.generate_grf_conv_names(0,weight))
    conv_names.update(refdata.graph_params.generate_grf_conv_names(1,weight))

    for std in [True,False]:
        GRAPH_NAME = f'cop_id_center_ref'
        fdp_graph([],xy_clippings_both, GRAPH_NAME, subject_num,out_dir,this_action_name,actions_to_be_shown,this_action_name,conv_names=conv_names,grid=(3,3),std=std, ref=grf_ref_data)

if __name__== "__main__":
    run("trial_data.yaml","trial_files.yaml","./")



