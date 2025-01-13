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

if __name__== "__main__":
    for sub in ["EXS01RE","EXS1RE", "EXS02RE" ]:
        pre_path = f"../../RTValidation_Extra/{sub}"
        ##mkdir

        out_path = f"./{sub}"
        for session in glob.glob(pre_path+"/SESSION*"):
            ses = os.basename(session)
            #idk
            sub_path = session
            for action in ["walking","sts","squat"]:
                output_dir = f"{out_path}/{action}/{ses}"
                os.makedirs(output_dir)
                trial_data = os.path.join(sub_path, f"{action}_data.yaml")
                if os.path.isfile(trial_data):
                    #raise(Exception(f"{trial_data} not found!"))
                    print(f"{trial_data} not found!")
                    continue

                pruned_files = os.path.join(sub_path, f"{action}_pruned.yaml")

                find_transitions.run(trial_data,pruned_files,output_dir)
                print("*"*100)
                refdata.logger.warning("ATTENTION: please update the pruned_files.yaml with the step segmentation that you got from vicon")
                print("*"*100)
                try:
                    generate_graph_grf.run(trial_data,pruned_files,output_dir)
                except:
                    pass
                try:
                    generate_graph_ik.run(trial_data,pruned_files,output_dir)
                except:
                    pass
                try:
                    generate_graph_id.run(trial_data,pruned_files,output_dir)
                except:
                    pass
                try:
                    generate_graph_so.run(trial_data,pruned_files,output_dir)
                except:
                    pass



