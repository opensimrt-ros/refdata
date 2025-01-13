#!/bin/env python3
import sys, os
sys.path.append("../")
from common import *
from refdata import refdata
import find_transitions
import generate_graph_grf
import generate_graph_ik
import generate_graph_id
import generate_graph_so
import shutil
import glob

_pre_path = glob.glob(f"../../RTValidation_Extra/*")

if __name__== "__main__":
    for pre_path in _pre_path:
        if not "RE" in pre_path:
            continue
        sub = os.path.basename(pre_path)
        ##mkdir

        out_path = f"./output/{sub}"
        print("*"*100)
        print("*"*100)
        print("*"*100)
        print("*"*100)
        print(sub,pre_path)
        print("*"*100)
        print("*"*100)
        print("*"*100)
        print("*"*100)
        
        for session in glob.glob(pre_path+"/SESSION*"):
            ses = os.path.basename(session)
            #idk
            sub_path = session
            for action in ["walking","sts","squat"]:
                print("+"*100)
                print(action)
                print("+"*100)
                output_dir = f"{out_path}/{ses}/{action}"
                if not os.path.isfile(output_dir):
                    os.makedirs(output_dir)
                trial_data = os.path.join(sub_path, f"{action}_data.yaml")
                if not os.path.isfile(trial_data):
                    #raise(Exception(f"{trial_data} not found!"))
                    print(f"{trial_data} not found!")
                    continue

                trial_files = os.path.join(output_dir, f"{action}_files.yaml")
                pruned_files = os.path.join(output_dir, f"{action}_pruned.yaml")

                if not os.path.isfile(pruned_files):
                    find_transitions.run(trial_data,trial_files,pruned_files,output_dir)
                    print("*"*120)
                    refdata.logger.warning(f"ATTENTION: please update the {pruned_files} with the step segmentation that you got from vicon")
                    print("*"*120)
                try:
                    generate_graph_grf.run(trial_data,pruned_files,output_dir)
                    generate_graph_ik.run(trial_data,pruned_files,output_dir)
                    generate_graph_id.run(trial_data,pruned_files,output_dir)
                    generate_graph_so.run(trial_data,pruned_files,output_dir)
                except:
                    print(f"failed in {output_dir}")

