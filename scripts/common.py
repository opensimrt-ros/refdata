#!/bin/env python3
import os
import logging
from refdata import refdata

from rich.logging import RichHandler
logging.basicConfig(format='%(funcName)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', 
                    handlers=[RichHandler()],
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
import pprint
import yaml
import pickle

if False:

    this_action_name = "walking"
    ##Edit next line to select at least this action!
    actions_to_be_shown = [ "walking" ]
    #['walk','gait','slow','fast']

    subject_num="EX01RE"
    weight= 53
    skip_trials =[]


def get_trial(name):

    a = yaml.safe_load(open(name,"rb"))

    this_action_name = a['this_action_name']
    actions_to_be_shown = a['actions_to_be_shown']
    subject_num = a['subject_num']
    weight = a['weight']
    skip_trials = a['skip_trials']
    trial_dir = a['directory']
    return this_action_name, actions_to_be_shown,subject_num,weight,skip_trials,trial_dir
###############################################################################

#ik_files, grfL_files,grfR_files, id_files, so_files, ik_lower_files, lumps = sort_files(actions_to_be_shown)                

def get_files(trial_file):
    a = yaml.safe_load(open(trial_file,"rb"))
    ik_files = a['ik']
    grfL_files = a['grfL']
    grfR_files = a['grfR']
    id_files = a['id']
    so_files = a['so']
    ik_lower_files = a['ik_lower']
    left_times = a['left']
    right_times = a['right']

    return ik_files, grfL_files,grfR_files, id_files, so_files, ik_lower_files, left_times, right_times 

def build_clipings(fs, side_list):
    d = {}
    for fsi, sli, in zip(fs,side_list):
        d.update({fsi:sli})
    return d

def fdp_graph(action_trials,xy_clippings_both, GRAPH_NAME, subject_num,out_dir,this_action_name,actions_to_be_shown,action,conv_names=None,grid=(3,3),std=False,ref=None,subject_identifier="Subject_Identifier_Please_Change"):
    
    all_curves_for_this_person = refdata.generate_action_plots(action_trials, xy_clippings_both, ref=ref,
           skip_trials=[],
           action=action, include_actions=actions_to_be_shown,
           conv_names=conv_names)
    ## Draws with stds from dataset
    if not all_curves_for_this_person:
        raise(Exception("all_curves is empty, check if data matches the reference provided"))
    #print(all_curves_for_this_person)
    _ = refdata.plot_std_plots(all_curves_for_this_person, plot_std=std, ref=ref, subplot_grid = grid,subject_identifier=subject_identifier)

    if type(ref) == type(None):
        GRAPH_NAME+="_no_ref_"

    if std:
        std_str = "stds"
    else:
        std_str = "all"

    file_name =f'sub{subject_num}_{GRAPH_NAME}_{this_action_name}{grid[0]}{grid[1]}_{std_str}' 
    refdata.plt.savefig(os.path.join(out_dir, f'{file_name}.pdf'), bbox_inches = 'tight')
    pickle.dump( all_curves_for_this_person, open(os.path.join(out_dir, f'{file_name}.p'),"wb"))
    
     


