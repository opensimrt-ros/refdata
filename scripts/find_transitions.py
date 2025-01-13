#!/bin/env python3
import os, sys
sys.path.append("../")
from refdata.files import sort_files, construct_new_names, rename_trials
from refdata import refdata
import numpy as np
import matplotlib.pyplot as plt
from importlib import reload

import glob

from common import *

def prettier(name, l):
    s = f"{name}:"+"\n"
    for li in l:
        s+="- "+repr(li) +"\n"
    return s
    

def run(trial_data_yaml, trial_files_yaml,trial_files_yaml_pruned ,out_dir):
    print(trial_data_yaml,trial_files_yaml)
    print(trial_data_yaml,trial_files_yaml)
    print(trial_data_yaml,trial_files_yaml)
    print(trial_data_yaml,trial_files_yaml)
    print(trial_data_yaml,trial_files_yaml)
    print(trial_data_yaml,trial_files_yaml)
    print(trial_data_yaml,trial_files_yaml)
    print(trial_data_yaml,trial_files_yaml)
    print(trial_data_yaml,trial_files_yaml)
    print(trial_data_yaml,trial_files_yaml)
    print(trial_data_yaml,trial_files_yaml)
    print(trial_data_yaml,trial_files_yaml)
    print(trial_data_yaml,trial_files_yaml)
    refdata.plt.rcParams['figure.figsize'] = [12, 5]
    refdata.ROW_OF_FLOTS = 1

    ######################### TRIAL INFO ##########################################
    this_action_name, actions_to_be_shown,subject_num,weight,skip_trials,trial_dir = get_trial(trial_data_yaml)

    ik_files, grfL_files,grfR_files, id_files, so_files, ik_lower_files, lumps = sort_files(action_list=actions_to_be_shown,directory=trial_dir)                               

    conv_names = refdata.graph_params.get_id_graph_params(weight)

    step_seg_l_list = []
    step_seg_r_list = []

    fig, ax = plt.subplots(len(ik_files)*2,1,figsize=(18,len(ik_files)*10))
    for i, (ik_, grfL_, grfR_) in enumerate(zip(ik_files, grfL_files, grfR_files)):   
        ik_2 = refdata.TrialData(ik_, remove_time_offset=False)
        zero_time = np.min(ik_2.data.time.values)
        step_seg_l_list.append(refdata.each_side_plot(grfL_,zero_time,grf_name_prefix = "1_ground_", side="Left", weight=weight,nicer_plot=True, figax = [fig,ax[2*i]]))
        step_seg_r_list.append(refdata.each_side_plot(grfR_,zero_time,grf_name_prefix = "ground_", side="Right", weight=weight,nicer_plot=True, figax = [fig,ax[2*i+1]]))

    plt.savefig(os.path.join(out_dir,"segmentation.pdf"), bbox_inches = 'tight')
    #plt.show()

    files = {'ik':ik_files,
             'grfL':grfL_files,
             'grfR':grfR_files,
             'id':id_files,
             'so':so_files,
             'ik_lower':ik_lower_files
             }


    with open(trial_files_yaml,'w',encoding="utf-8") as f:

        yaml.dump(files,f)
        f.write(prettier("left",step_seg_l_list))
        f.write(prettier("right",step_seg_r_list))
    create_pruned(trial_files_yaml,trial_files_yaml_pruned,skip_trials)

def prune_files(dic,skip_files):
    print(dic)
    if len(skip_files) == 0:
        return dic
    d = {}
    for k,v in dic.items():
        a = []
        for i, f in enumerate(v):
            if not i in skip_files:
                a.append(f)
        d.update({k:a})
    return d

def create_pruned(trial_file,pruned_trial_file, skip_files):
    a = yaml.safe_load(open(trial_file,"rb"))
    b = prune_files(a,skip_files)
    print(b)
    files = {'ik':b['ik'],
             'grfL':b['grfL'],
             'grfR':b['grfR'],
             'id':b['id'],
             'so':b['so'],
             'ik_lower':b['ik_lower']
             }
    with open(pruned_trial_file,'w',encoding="utf-8") as f:

        yaml.dump(files,f)
        f.write(prettier("left",b['left']))
        f.write(prettier("right",b['right']))


if __name__== "__main__":
    #only file necessary is "trial_data.yaml", everything else will be from the trial itself or generated
    run("trial_data.yaml","trial_files.yaml",'pruned_files.yaml',"./")
    print("*"*100)
    refdata.logger.warning("ATTENTION: please update the pruned_files.yaml with the step segmentation that you got from vicon")
    print("*"*100)

