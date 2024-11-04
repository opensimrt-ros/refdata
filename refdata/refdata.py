#!/bin/env python3
#from https://wwrichard.net/2014/09/02/do-it-yourself-normative-data-comparison-free-download/
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.axes_grid1 import Divider, Size,  make_axes_locatable
from importlib.metadata import version
import os

def check_ver(package, ver_requirements):
    ver_requirements_list = ver_requirements.split('.')
    ver_list = version(package).split('.')
    major = ver_list[0]
    minor = ''
    other = ''
    if len(ver_list)>1:
        minor = ver_list[1]
    if len(ver_list)>2:
        other = ver_list[2:]
    if int(major)<int(ver_requirements_list[0]) or int(minor)<int(ver_requirements_list[1]):
        raise Exception(f"requirements for {package} not met need {ver_requirements}, have {'.'.join(ver_list)}")
        
check_ver('matplotlib', "3.8")

def check_data(data_dir):
    dirs_to_check = ["grf_data","id_data","so_data","ik_data"]
    for some_dir in dirs_to_check:
        if not os.path.exists(os.path.join(data_dir,some_dir)):
            raise Exception(f"source data {some_dir} not found. graph generation with references will fail")
    print("data found okay!")

check_data(os.path.join(os.path.dirname(__file__),"../data"))

import numpy as np
import glob
from numpy import matlib 
from scipy import interpolate
from scipy import signal
from scipy.signal import argrelextrema
from scipy.interpolate import PchipInterpolator
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import os
import graph_params

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

##Setting graphing parameters
ROW_OF_FLOTS=15

def set_graph_params():
    SMALL_SIZE = 12
    MEDIUM_SIZE = 18
    BIGGER_SIZE = 22

    matplotlib.rc('text', usetex = True)
    matplotlib.rc('font', **{'family' : "sans-serif"})
    #params = {'text.latex.preamble' : [r'\usepackage{siunitx}', r'\usepackage{sfmath}']}
    fontProperties = {'family':'sans-serif', 'weight': 'normal', 'size': 12}
    #plt.rcParams.update(params)

    plt.rc('text.latex', preamble=r'\usepackage{cmbright}')
    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
    plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
    #plt.rcParams['figure.figsize'] = [12, 6]
    #plt.rcParams['figure.dpi'] = 400 # 200 e.g. is really fine, but slower

set_graph_params()


#plot_ref_id("ankle")

def load_reference_ik_data():
    module_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(module_dir,"..","data","ik_data", "IK_REFERENCES_PAPER.csv")
    return pd.read_csv(csv_file_path, skiprows=1)

class RefDataPrimitive:
    def __init__(self):
        self.name = ""
        self.x = None
        self.mean = None
        self.sd = None
    def __repr__(self):
        return f"RefDataPrimitive(): {self.name} "
    def __str__(self):
        return f"RefDataPrimitive():\n name: {self.name}\n x: {self.x}\n mean: {self.mean}\n sd: {self.sd}"

def repeat_x(x_, n_times):
    x = x_
    STARTS_AT_ZERO = False
    if STARTS_AT_ZERO:
        x_zero_increment = x_[1]-x_[0]
    else:
        x_zero_increment = 0
    for i in range(n_times-1):

        x = np.hstack((x, x_+np.max(x)+x_zero_increment))
    return x

class RefData:
    def __init__(self, action_type):
        self.action_type = action_type
        self.reference_curve_dict = {}
        self.plot_2_sd = False

    def plot(self, reference_name_name= "all"):

        if reference_name_name == "all":
            reference_name_name = []
            for reference_name, _ in self.reference_curve_dict.items():
                reference_name_name.append(reference_name)

        if isinstance(reference_name_name,list):
            for reference_name in reference_name_name:
                self.plot_reference_name(reference_name)
        if isinstance(reference_name_name,str):
            self.plot_reference_name(reference_name_name)

    def get_curve_y(self, y_in, x, xnew, num_cycles,scale, inverted=False ):
        y   = np.tile(y_in,num_cycles+4)
        #print(len(y))
        fy =  interpolate.interp1d(x,y)
        ynew = fy(xnew)
        Y = ynew*scale
        if inverted:
            return -Y
        return Y

    def get_curve_x(self, ik_id_so_i, x_offset, num_cycles,scale ):
        x   = repeat_x(ik_id_so_i.x,num_cycles+4)
        #print(x)
        #print("lenx %d"%len(x))
        xnew = np.arange(x_offset%360, 100*num_cycles+x_offset%360, 1)
        #print(xnew)
        X =(xnew-x_offset)*scale
        return X,x, xnew

    def get_reference_name_curve(self, reference_name, num_cycles=4,scale=[1,1], inverted=False):
        x_offset = 0

        X_list = []
        Y_list = []
        for ik_id_so_i in self.reference_curve_dict[reference_name]:
            print(ik_id_so_i)
            X,x, xnew = self.get_curve_x(ik_id_so_i, x_offset, num_cycles,scale[0] )
            Y = self.get_curve_y(ik_id_so_i.mean, x, xnew, num_cycles,scale[1], inverted=inverted)
            X_list.append(X)
            Y_list.append(Y)

        return X_list,Y_list

    def plot_reference_name(self, reference_name, num_cycles=4,scale=[1,1], avg_line=True, inverted = False, ax = None, alpha_=0.9): 
        """
        reference_name: is the name of the reference reference_name to be plotted
        num_cycles: is an integer

        """
        #print("plotting reference!")
        if not ax:
            fig = plt.figure()
            ax = plt.gca()

        if not self.reference_curve_dict:
            print("reference curve dictionary not set!")
            return
        #plt.figure()
        #plt.title(reference_name)

        x_offset = 0
        #num_cycles = num_cycles_+4
        if reference_name in self.reference_curve_dict:
            ik_id_so_i = self.reference_curve_dict[reference_name][0]
        #for ik_id_so_i in self.reference_curve_dict[reference_name]:

            X,x, xnew = self.get_curve_x(ik_id_so_i, x_offset, num_cycles,scale[0])
            #print("leny %d"%len(ik_id_so_i.mean))
            Y = self.get_curve_y(ik_id_so_i.mean, x, xnew, num_cycles,scale[1])
            YP = self.get_curve_y(ik_id_so_i.mean+ik_id_so_i.sd, x, xnew, num_cycles,scale[1])
            YM = self.get_curve_y(ik_id_so_i.mean-ik_id_so_i.sd, x, xnew, num_cycles,scale[1])

            if inverted:
                Y = -Y
                YP = -YP
                YM = -YM

            if avg_line:
                ax.plot(X, Y, "-", label="{} mean".format(ik_id_so_i.name))
            ax.fill_between(X,YP, YM, alpha=alpha_, label= "{} 1 std ".format(ik_id_so_i.name),  linewidth=1, color="gray")

            if self.plot_2_sd:

                Y2P = self.get_curve_y(ik_id_so_i.mean+2*ik_id_so_i.sd, x, xnew, num_cycles,scale[1])
                Y2M = self.get_curve_y(ik_id_so_i.mean-2*ik_id_so_i.sd, x, xnew, num_cycles,scale[1])
                if inverted:
                    Y2P = -Y2P
                    Y2M = -Y2M

                ax.fill_between(X,Y2P, Y2M, alpha=alpha_, label= "{} 2 std ".format(ik_id_so_i.name),  linewidth=1, color="lightgray")
        else:
            logging.warn("I dont have the reference %s"%reference_name)
        #plt.legend()
        #plt.show()            

def latex_friendly_column_names(name):
    name = name.replace(" ", "_")
    name = name.replace("/","_")
    return name

## newer function loading the whole xlsx file
class GaitNormativeRefData(RefData):
    def __init__(self, own_action_name="gait"):
        RefData.__init__(self,own_action_name)
    def set_from_sheet(self, sheet_name=None):
        if not sheet_name:
            raise(ValueError("need sheet_name"))
        module_dir = os.path.dirname(os.path.abspath(__file__))
        xlsx_file_path = os.path.join(module_dir,"..","data","normative-dataset-comparison.xlsx")
        
        ik_names = {}
        index_name="'Gait_percentage'"
        
        df = pd.read_excel(io=xlsx_file_path, sheet_name=sheet_name,  header=[0,1], 
                   index_col=[0,1], )
        
        unique_movement_names = list(set(df.index.get_level_values(0)))
        latex_friendly_names = [latex_friendly_column_names(name) for name in unique_movement_names]
        
        
        for movement_name, friendly_movement_name in zip(unique_movement_names,latex_friendly_names):
            
            self.reference_curve_dict.update({friendly_movement_name:[RefDataPrimitive(),RefDataPrimitive()]})
            
            for col in df.columns:
                ik_index = None
                if col[0] == 'Your data':
                    continue
                if 'one' in col[0]:
                    ik_index = 0
                if 'two' in col[0]:
                    ik_index = 1
                #print(col, movement_name, ik_index)

                self.reference_curve_dict[friendly_movement_name][ik_index].name = col[0]    


                if col[1] == 'Average':
                    self.reference_curve_dict[friendly_movement_name][ik_index].mean = df[col][movement_name].values
                    self.reference_curve_dict[friendly_movement_name][ik_index].x = 100*np.array(df[col][movement_name].index)
                    #print(self.reference_curve_dict[friendly_movement_name][ik_index].x)
                if col[1] == 'SD':
                    self.reference_curve_dict[friendly_movement_name][ik_index].sd = df[col][movement_name].values
                

class GaitIKRefData(GaitNormativeRefData):
    def __init__(self, action="gait"):
        GaitNormativeRefData.__init__(self, action)
        self.set_from_sheet(sheet_name=u"Joint Rotations")
    #def plot_reference_name(self, reference_name, scale=[], num_cycles = 0, avg_line=False, ax=None):
    #    pass

class GaitIDRefData(GaitNormativeRefData): ## name is not following conventions,
        def __init__(self, action="gait"):
            GaitNormativeRefData.__init__(self, action)
            self.set_from_sheet(sheet_name=u"Joint Moments")
            ## but the names on the sheet are inconsistent, so we need to change the dictionary keys
            dict_map = {'Ankle_Rotation_Moment':'Foot_Int_Ext',
                    'Hip_Extensor_Moment_':'Hip_Flx_Ext',
                    'Knee_Abductor_Moment_':'Knee_Abductor_Moment_',
                    'Hip_Abductor_Moment_':'Hip_Add_Abd',
                    'Plantarflexor_Moment_':'Ankle_Dor_Pla',
                    'Knee_Extensor_Moment_':'Knee_Flx_Ext'
                    }
            new_dict = {}
            for key, value in self.reference_curve_dict.items():
                new_dict.update({dict_map[key]:self.reference_curve_dict[key]})
            self.reference_curve_dict = new_dict



class GaitPowerRefData(GaitNormativeRefData):
        def __init__(self, action="gait"):
            GaitNormativeRefData.__init__(self, action)
            self.set_from_sheet(sheet_name=u"Joint Power")

class IdData(RefData):
    def __init__(self, action=""):
        RefData.__init__(self, action)
    #def plot_reference_name(self, reference_name, scale=[], num_cycles = 0, avg_line=False, ax=None):
    #    pass

def IdGaitData(action="gait"): ## name is not following conventions,
    logging.warn("name changed to follow conventions, use GaitIDRefData instead")
    return GaitIDRefData(action=action)

##TODO: I am not being consistent with the names here
class SoData(RefData):
    def __init__(self, action=""):
        RefData.__init__(self, action)

    def plot_reference_name(self,reference_name,scale=[1/99,1], num_cycles=1, avg_line=False, ax=None):
        pass


def generate_action_plots(action_trials_, xy_clippings_both, skip_trials=[], ref=GaitIKRefData(),
        conv_names=graph_params.get_ik_graph_params(), include_actions=[], action=None):
    all_curves_for_this_person = {}

    for l_r, clips in enumerate(xy_clippings_both):
        for i_file,(file, which_clippings) in enumerate(clips.items()):
            try:
            #for i_file, file in enumerate(action_trials):
                this_action_name = ""
                #print(i_file)
                #print(skip_trials)
                matching_actions = [action_name for action_name in include_actions if action_name in file]
                if not matching_actions or i_file in skip_trials :
                    print("skipping file: %s"%file)
                    continue
                elif len(matching_actions) >1:
                    raise ValueError("More than one action in the specified file name!")
                else:
                    if action:
                        this_action_name= action
                    else:
                        this_action_name = matching_actions[0]
                this_trial = TrialData(file)

                data = this_trial.data

                for joint_or_muscle_name, ref_name in conv_names.items():

                    if joint_or_muscle_name in data.columns:
                        joint_or_muscle_name_suffix = ["",""]
                    elif joint_or_muscle_name+"_l" in data.columns and joint_or_muscle_name+"_r" in data.columns:
                        joint_or_muscle_name_suffix = ["_l","_r"]
                    else:
                        continue ## I think...
                    if ref_name["plot_it"]:
                        #print(joint_or_muscle_name_suffix)
                        joint_or_muscle_complete_name = joint_or_muscle_name+joint_or_muscle_name_suffix[l_r]
                        if not joint_or_muscle_complete_name in all_curves_for_this_person.keys():
                            all_curves_for_this_person.update({joint_or_muscle_complete_name:([],"","")})

                        side = l_r
                        if "pelvis" in joint_or_muscle_complete_name or "lumbar" in joint_or_muscle_complete_name:
                            side = -1
                            #print(xy_clippings_both[1])
                        #    which_clippings = xy_clippings_both[1][file]
                        #else:
                            #print(xy_clippings_both[l_r])
                        #    which_clippings = xy_clippings_both[l_r][file]
                        xi, curves = reshape_curves(normalize_steps(clip_curve(data["time"],
                            data[joint_or_muscle_complete_name]*ref_name["scale"][1]+ref_name["offset"],
                            time_clips = which_clippings )))

                        list_of_curves = all_curves_for_this_person[joint_or_muscle_complete_name][0]
                        list_of_curves.append((xi,curves))
                        ##define side for plot:
                        #if joint_or_muscle_suffix:
                        #    side = l_r
                        #else: ## pelvis or lumbar joints
                        #    side = -1
                        all_curves_for_this_person.update({joint_or_muscle_complete_name:(list_of_curves, ref_name,side)})
            except:
                print("failed in %s"%i_file)
                pass
    return all_curves_for_this_person

def generate_gait_plots(gait_trials,xy_clippings_both, **kwargs):
    return generate_action_plots(gait_trials, xy_clippings_both, action="gait", include_actions= ["gait", "walk", "fast","slow"], **kwargs)

def remove_repeated(handles, labels):
    nh = []
    nl = []
    #print(labels)
    for h, l in zip(handles, labels):
        if not l in nl:
            nl.append(l)
            nh.append(h)
    #print(nl)
    try:
        nh, nl = zip(*sorted(zip(nh, nl), key=lambda x: x[1]))
    except:
        pass
    return nh, nl

def actual_plot(X,Y,ax,side, plot_std, steps_label= "{}steps 1-{}",change_x_ticks=True, use_color_cycle=True):
    colorspace_range = len(Y)
    cycle_begin = 1
    if use_color_cycle:
        cycle_begin = 0.5
    cycle_end = 1
    if side == 0:
        mean_color = "red"
        std_p = "darkred"
        std_m = "firebrick"
        mean_name = "Left "
        #color_cycle = plt.cm.copper(np.linspace(0,1,len(Y)+2))
        color_cycle = plt.cm.Reds(np.linspace(cycle_begin,cycle_end,colorspace_range))
    elif side == 1:
        mean_color = "blue"
        std_p = "darkblue"
        std_m = "navy"
        mean_name = "Right "
        #color_cycle = plt.cm.cool(np.linspace(0,1,len(Y)+2))
        color_cycle = plt.cm.Blues(np.linspace(cycle_begin,cycle_end,colorspace_range))
    elif side == -1:
        mean_color = "green"
        std_p = "darkgreen"
        std_m = "seagreen"
        mean_name = ""
        #print("greeen")
        #color_cycle = plt.cm.winter(np.linspace(0,1,len(Y)+2))
        color_cycle = plt.cm.Greens(np.linspace(cycle_begin,cycle_end,colorspace_range))
    else:
        raise Exception("side does not have a color defined!")

    if plot_std:
        #print(mean_name)
        #print("Mean{}".format(mean_name))
        ax.plot(X,Y.mean(axis=0), color = mean_color, label="{}Mean".format(mean_name))
        ax.plot(X,Y.mean(axis=0)+Y.std(axis=0), "-.", color = std_p, label="{}+1 SD".format(mean_name))
        ax.plot(X,Y.mean(axis=0)-Y.std(axis=0), "-.", color = std_m, label="{}-1 SD".format(mean_name))
    else:
        ax.set_prop_cycle('color',color_cycle)
        one_label = False
        n =  len(Y)
        my_alpha = np.min([(1./n+0.4),1.])
        for i, y in enumerate(Y):
            #ax.plot(X,y,label="step %d"%i)
            if not one_label and i>=n/2:
                #ax.plot(X,y,label="{}steps 1-{}".format(mean_name,n))
                ax.plot(X,y,label=steps_label.format(mean_name,n),alpha=my_alpha)
                one_label=True
            else:
                ax.plot(X,y,alpha=my_alpha)
    if change_x_ticks:
        ax.set_xticks([0,.20,.40,.60,.80,1.00],labels=[0,20,40,60,80,100])
        

def create_axs_dimensions(nrows, ncols, margin= 2, header = 2, subheigth = 8, subwidth= 8): ## now it is in cm

    m = margin /2.54
    h = header /2.54

    a= subheigth/2.54
    b= subwidth /2.54

    width = ncols * (m + b+ m)
    height = nrows * (h +a +h)

    axarr = np.empty((nrows, ncols), dtype =object)
    
    #print(height, width)

    fig = plt.figure(figsize=(width, height)) #, facecolor = 'lightblue')

    for i in range(nrows):
        for j in range(ncols):
            axarr[i,j] = fig.add_axes([(m+j*(2*m+b))/width,
                (height - (i+1)*(2*h+a)+h)/height,
                b/width,
                a/height])

    return fig, axarr

def plot_std_plots(all_curves_for_any_person, plot_std=True, plot_ref_curves=True, ref=GaitIKRefData(), subplot_grid=(ROW_OF_FLOTS+1,3), steps_label="{}steps 1-{}", legend=True, axs=None, fig=None, use_color_cycle=True):
    new_curves_dict = {}
    if ref:
        action_type = ref.action_type
    else:
        action_type = "???"
    if type(axs) == type(None) or type(fig)==type(None):
        fig, axs = create_axs_dimensions(*subplot_grid)
        #fig, axs = plt.subplots(*subplot_grid, squeeze=False)
        
        for ax in axs.flatten():
            ax.set_axis_off()
    #else:        
    #    fig.tight_layout(pad=5.0)
    all_handles = []
    all_labels = []
    if plot_std:
        plot_save_name_suffix = "std"
    else:
        plot_save_name_suffix = "each_step"


    def plot_all_joint_or_muscles_for_person(all_curves_for_this_person, plot_ref_curves=True):
        for name, list_of_curves in all_curves_for_this_person.items():

            curves_combined = []
            ref_name = list_of_curves[1]
            side = list_of_curves[2]

            for curves in list_of_curves[0]:
                x = curves[0]
                for curve in curves[1]:
                    curves_combined.append((x, curve))

            x, new_curves_combined = reshape_curves(curves_combined) 
            new_curves_dict.update({name:(x,new_curves_combined)})
            X = new_curves_dict[name][0]
            Y = new_curves_dict[name][1]

            ax = axs[ ref_name["position"][0],ref_name["position"][1]]
            ax.set_axis_on()
            if plot_ref_curves:
                if not ref:
                    print("I was asked to display references, but no reference defined!")
                else:
                    ref.plot_reference_name(ref_name["name"], scale=[1/99,ref_name["scale"][0]], 
                        num_cycles=1, avg_line=False, ax=ax)
            actual_plot(X,Y,ax,side, plot_std, steps_label=steps_label,use_color_cycle=use_color_cycle)

            ax.set_title(ref_name["title"])
            ax.set(xlabel=f"\MakeUppercase {action_type} cycle [\%]", ylabel=ref_name["yaxis_name"])
            ax.set_ylim(ref_name["axes_limits"])
            handles, labels = ax.get_legend_handles_labels()
            all_handles.extend(handles)
            all_labels.extend(labels)


    if isinstance(all_curves_for_any_person, dict):
        plot_all_joint_or_muscles_for_person(all_curves_for_any_person, plot_ref_curves=plot_ref_curves)
        nh, nl = remove_repeated(all_handles, all_labels)    
        if legend:
            fig.legend(nh, nl,loc='center left', bbox_to_anchor=(1, 0.5))#, loc='lower right')
        #plt.savefig('figure_{}.pdf'.format(plot_save_name_suffix), bbox_inches='tight')
        #plt.show()
    if isinstance(all_curves_for_any_person, list):
        for all_curves_for_this_person in all_curves_for_any_person:
            plot_all_joint_or_muscles_for_person(all_curves_for_this_person, plot_ref_curves=False)
        nh, nl = remove_repeated(all_handles, all_labels)        
        if legend:
            fig.legend(nh, nl,loc='center left', bbox_to_anchor=(1, 0.5))#, loc='lower right')
        #plt.savefig('figure_multiple_people_{}.pdf'.format(plot_save_name_suffix), bbox_inches='tight')
        #plt.show()

    #change the size of the figure to show always exactly the same way 





    return axs, fig, nh, nl




class TrialData:
    def __init__(self, file, remove_time_offset=True):
        print("file: %s"%file)
        self.data = pd.read_csv (file, sep = '\t', skiprows=4)
        if remove_time_offset: #remove time ofset
            self.data["time"] = self.data["time"] - self.data["time"][0]
        for col in self.data.columns:
            if col == "time":
                continue
            else:
                self.data[col] =  self.data[col]

    def trim_time(self, start_time, end_time):
        #df = df[(df['closing_price'] >= 99) & (df['closing_price'] <= 101)]
        #data = data[(data["time"] >= time_start[i_file]) & (data["time"] <= time_end[i_file]+time_start[i_file])]
        self.data = self.data[(self.data["time"] >= start_time) & (self.data["time"] <= end_time+start_time)]
        #print(data)

        #remove time offset again because we changed where it starts
        self.data.time = self.data["time"] - np.min(self.data["time"])
        self.data.set_index('time')

    def get_as_np(self, cols="all"):
        if cols == "all":
            return self.data.iloc[:,:].values
        else: 
            return self.data.loc[:,cols].values
        
        
def generate_somejoint_or_muscle_curves(some_action_trials, skip_trials, curve_prefix="knee_angle", conv_names=graph_params.get_ik_graph_params(),left_or_right=0):
    xy_joint_or_muscles = ({},{})
    for i_file, file in enumerate(some_action_trials):
        if i_file in skip_trials:
            print("skipping file: %s"%file)
            continue

        this_trial = TrialData(file)
        #this_trial.trim_time(time_start[i_file], time_end[i_file] )

        data = this_trial.data

        for joint_or_muscle_name, ref_name in conv_names.items():
            if joint_or_muscle_name in data.columns:
                joint_or_muscle_name_suffix = [""]
            else:
                joint_or_muscle_name_suffix = ["_l","_r"]

            if ref_name["plot_it"]:
                for l_r, joint_or_muscle_suffix in enumerate(joint_or_muscle_name_suffix):
                    joint_or_muscle_complete_name = joint_or_muscle_name+joint_or_muscle_suffix

                    if joint_or_muscle_complete_name=="%s_r"%curve_prefix:
                        y = data[joint_or_muscle_complete_name]*ref_name["scale"][1]
                        x = data["time"]
                        xy_joint_or_muscles[1].update({file:(x,y,[])})
                    elif joint_or_muscle_complete_name=="%s_l"%curve_prefix:
                        y = data[joint_or_muscle_complete_name]*ref_name["scale"][1]
                        x = data["time"]
                        xy_joint_or_muscles[0].update({file:(x,y,[])})
                    elif joint_or_muscle_complete_name==curve_prefix:
                        print("FORCE PLATE?")
                        y = data[joint_or_muscle_complete_name]*ref_name["scale"][1]
                        x = data["time"]
                        xy_joint_or_muscles[left_or_right].update({file:(x,y,[])})

    return xy_joint_or_muscles


def clip_curve(time, curve_val, time_clips = [(0.1,1.13),(1.13,2.2),(2.2,3.26),(3.26,4.39),(4.39,5.55)], PLOT_IT=False):
    actions = []
    non_actions = []
    if not time_clips:
        return 
    def get_index_of_time(x):
        #time is always increasing so this is trivial:
        for i, x_i in enumerate(time):
            if x_i>x:
                return i
    #print(time_clips)
    for i in range(len(time_clips)-1):
        li = get_index_of_time(time_clips[i][0])
        ui = get_index_of_time(time_clips[i][1])
        #print(li)
        #print(time.values[li])

        xi = time[li:ui] #- time.values[li]
        yi = curve_val[li:ui]
        actions.append((xi,yi))
    for i in range(len(time_clips)-1):
        li = get_index_of_time(time_clips[i][1])
        ui = get_index_of_time(time_clips[i+1][0])
        xi = time[li:ui]
        yi = curve_val[li:ui]
        non_actions.append((xi,yi))
    ## add beginning and end to non_actions:
    non_actions.append((time[0:get_index_of_time(time_clips[0][0])],curve_val[0:get_index_of_time(time_clips[0][0])]))
    non_actions.append((time[get_index_of_time(time_clips[-1][0]):-1],curve_val[get_index_of_time(time_clips[-1][0]):-1]))
    ## test if i did it correctly
    if PLOT_IT:
        fig, ax = plt.subplots()
        for xi_yi in actions:
            xi = xi_yi[0]
            yi = xi_yi[1]
            plt.plot(xi,yi)
        for xi_yi in non_actions:
            plt.plot(xi_yi[0],xi_yi[1],'lightgray')
        ax.xaxis.set_major_locator(MultipleLocator(1))
        ax.xaxis.set_minor_locator(AutoMinorLocator(5))
        ax.grid(which='major', color='#CCCCCC', linestyle='--')
        ax.grid(which='minor', color='#CCCCCC', linestyle=':')
        plt.show()
    return actions
#steps = clip_curve(x,y)

def clip_curve_test(time, curve_val, time_clips = [(0.1,1.13),(1.13,2.2),(2.2,3.26),(3.26,4.39),(4.39,5.55)]):
    clip_curve(time, curve_val, time_clips, PLOT_IT=True) 

    
def reshape_curves(curves, PLOT_IT=False, lower_lim = None, upper_lim = None): ##they have the same x, so now it will return x, Y
    ##to be able to get the average curve they need to line up and have the same number of samples
    max_len = 0
    new_curves = []

    finding_lower = False
    finding_upper = False
    if not lower_lim:
        finding_lower = True
        lower_lim = 1e200
    if not upper_lim:
        finding_upper = True
        upper_lim = -1e200
    for curve in curves:
        #print(curve)
        if max_len < get_length(curve[0]):
            max_len = get_length(curve[0])
        if finding_lower and np.min(curve[0]) < lower_lim:
            lower_lim = np.min(curve[0])
        if finding_upper and np.max(curve[0])> upper_lim:
            upper_lim = np.max(curve[0])
    #max len
    #print(max_len)
    xi = np.linspace(lower_lim,upper_lim, num=max_len)
    for curve in curves:
        fy =  interpolate.interp1d(curve[0],curve[1])
        new_curves.append(fy(xi))
    if PLOT_IT:
        for yi in new_curves:
            plt.plot(xi,yi)
        plt.show()
    return xi, np.array(new_curves)

#a = reshape_curves(normalize_steps(steps))
#print(a[0])

def normalize_steps(steps_, PLOT_IT=False):
    ## all steps will last 1.
    normalized_steps = []
    for i, xi_yi in enumerate(steps_):
        xi = np.linspace(0, 1, num=len(xi_yi[1]))
        normalized_steps.append((xi,xi_yi[1].values))
    if PLOT_IT:
        for xi_yi in normalized_steps:
            xi = xi_yi[0]
            yi = xi_yi[1]
            plt.plot(xi,yi)
        plt.show()
    return normalized_steps
#unit test:
#normalize_steps(steps);


def get_length(something):
    if isinstance(something,list):
        return len(something)
    if isinstance(something,np.ndarray):
        return something.size
    print(something)
    raise("wtf!!!!!!!!!!!!!")

#print(get_length([1,2,3,4]))
#print(get_length(np.array([1,2,3,4])))


#reload(refdata)

class AxCurves():
    def __init__(self, position = None,curves_dic = None, reference =None, joint_or_muscle_complete_name=None ):
        self.position = position
        self.curves_dic = curves_dic
        self.reference = reference
        self.name = joint_or_muscle_complete_name
    def update(self):
        ref_name = self.curves_dic[self.name][1]
        ref_name["position"] = self.position
        self.curves_dic[self.name] = (self.curves_dic[self.name][0], ref_name, self.curves_dic[self.name][2])
        
from copy import deepcopy

def creat_axs(cccc, ref= IdGaitData()):
    ## deepcopy?
    local_cccc = deepcopy(cccc)
    axcurve_list_ = []
    for name, list_of_curves in local_cccc.items():
        some_ax = AxCurves()
        ref_name = list_of_curves[1]
        side = list_of_curves[2]
        some_ax.position = ref_name["position"]
        some_ax.curves_dic = {name:list_of_curves}
        some_ax.name = name
        some_ax.reference = ref
        some_ax.update()
        #print(ref_name)
        axcurve_list_.append(some_ax)
    return axcurve_list_
        
#axcurve_list = creat_axs(all_curves_for_this_person)


def plotAX(some_Axs, ax, fig, plot_std=True, plot_ref_curves=False, legend=False):
    
    allnh = []
    allnl = []
    for axi in ax.flatten():
        axi.set_axis_off()
    for an_Ax in some_Axs:
        _,_,nh,nl = plot_std_plots(an_Ax.curves_dic, axs=ax, fig=fig, ref= an_Ax.reference, legend= False, plot_std=plot_std, plot_ref_curves=plot_ref_curves)
        allnh.extend(nh)
        allnl.extend(nl)
    allnh, allnl = remove_repeated(allnh, allnl) 
    if legend:
        fig.legend(allnh, allnl,loc='lower right', bbox_to_anchor=(0.85, 0.18))
    return fig, ax, allnh, allnl
       

       
        
#plotAX(axcurve_list, ax)

def apply_offset_to_axs(some_axcurve_list, vert_offset):
    new_list = []
    for i_axcu in some_axcurve_list:
        i_axcu.position = (i_axcu.position[0]+vert_offset, i_axcu.position[1])
        i_axcu.update()
        new_list.append(i_axcu)
    return new_list

from IPython.display import display, Javascript

def create_new_cell_below(content):
    display(Javascript('''
        var idx = Jupyter.notebook.get_selected_index();
        var codeCell = Jupyter.notebook.insert_cell_at_index('code', idx);
        codeCell.set_text('#GENERATED CELL!\\n%s');
        Jupyter.notebook.select(idx);
    ''' % content.replace('\n', '\\n')))

def find_steps(x, grf,weight):
    #plt.plot(x,grf)
    #plt.show()
    threshold = weight*9.8/10
    step = False
    step_seq = []
    step_start = 1e200
    step_stop = 1e200
    min_duration = 0.05
    lowering = False
    rising = False
    this_step = [None,None]
    for t, y in zip(x,grf):
        #print((y, threshold))
        if not step and y>threshold:
            #print(t)
            rising = True
            step_start= np.min([t,step_start])
            if t-step_start > min_duration:
                step = True
                #print("is step")
                this_step[0] = step_start
        if rising and y<threshold:
            rising = False
            step_start = 1e200
        if step and y<threshold:
            #print("trying to find lowering edge, %f, %f"%(t,step_stop))
            lowering = True
            step_stop = np.min([t,step_stop])
            if t-step_stop > min_duration:
                #print("found lowering %s"%step_stop)
                step = False
                this_step[1] = step_stop
                step_seq.append(this_step)
                this_step = [None,None]
                step_start = 1e200
                step_stop = 1e200
        if lowering and y>threshold:
            lowering = False
            step_stop = 1e200
    if this_step[0]:
        step_seq.append(this_step) ## appending the last incomplete step because we need the start for segmentation
    return step_seq

def gen_step_ticks(some_steps, weight):
    xy = [[],[]]
    lower_curve_bound = weight*9.8/10 
    textstr = [] # x,y, stepcount
    for i, a_step in enumerate(some_steps):
        xy[0].extend([a_step[0],a_step[0],a_step[0]])
        xy[1].extend([lower_curve_bound,700,np.nan])
        xy[0].extend([a_step[1],a_step[1],a_step[1]])
        xy[1].extend([lower_curve_bound,800,np.nan])
        ##if the boundary of the steps are None this is a problem
        if not a_step[0] and not a_step[1]:
            continue
        if a_step[0]:
            lwx = a_step[0]
        if a_step[1]:
            lwx = a_step[1]
        if a_step[0] and a_step[1]:
            lwx = a_step[0]/2+a_step[1]/2
        textstr.append([lwx,lower_curve_bound, ("st.%d"%i)])
    return xy[0],xy[1],textstr

##newer better, should work for gait 
def construct_step_segmentation_vector(some_steps):
    new_step_def_list = []
    for i,ith_step in enumerate(some_steps):
        #disregard the first step
        if i < len(some_steps)-1:
            ithpone= some_steps[i+1][0]
        else:
            ithpone= None
        if i == 0:
            continue
        new_step_def_list.append((ith_step[0], ithpone))
    return new_step_def_list
from copy import copy
def each_side_plot(grf_, zero_time, grf_name_prefix = "1_ground_", side="Left", weight=None, plot_all=False, time_offset=0, plot_no_offset=True):
    
    grf = TrialData(grf_, remove_time_offset=False)

    x_grf = np.array(list(grf.data.time-zero_time))
    x_grf_offset = copy(x_grf)
    x_grf_offset+= time_offset

    steps_vec = find_steps(x_grf_offset,grf.data[f"{grf_name_prefix}force_vy"], weight)

    st_seg = construct_step_segmentation_vector(steps_vec)
    
    #print(st_seg)
    all_handles = []
    all_labels = []
    
    fig, ax1 = plt.subplots(figsize=(18,4))
        
    #plt.plot(x_ik,ik_2.data.ankle_angle_l/3.141592*180,"--", label="ankle l")
    #plt.plot(x_ik,ik_2.data.hip_flexion_l/3.141592*180,"--", label="hip x l")
    
    xsl, ysl, textstrl = gen_step_ticks(steps_vec, weight)
    
    ax1.plot(x_grf,grf.data[f"{grf_name_prefix}force_py"],'r', label="py")
    if plot_all:
        ax1.plot(x_grf,grf.data[f"{grf_name_prefix}force_px"],'g', label="px")
        ax1.plot(x_grf,grf.data[f"{grf_name_prefix}force_pz"],'b', label="pz") 
    
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    handles, labels = ax1.get_legend_handles_labels()
    all_handles.extend(handles)
    all_labels.extend(labels)
    ax1.set_ylim((-0.05,1))

    
    # plotting step ticks
    ax2.plot(xsl,ysl,'g')
    for a_text in textstrl:
        ax2.annotate(a_text[2],(a_text[0],a_text[1]))
    
    if plot_no_offset:
        ax2.plot(x_grf,grf.data[f"{grf_name_prefix}force_vy"],'darkred', label="y")
    ax2.plot(x_grf_offset,grf.data[f"{grf_name_prefix}force_vy"],'coral', label="y t_off=%f"%time_offset)
    if plot_all:
        ax2.plot(x_grf_offset,grf.data[f"{grf_name_prefix}force_vx"],'lime', label="x")
        ax2.plot(x_grf_offset,grf.data[f"{grf_name_prefix}force_vz"],'navy', label="z")
    
    handles, labels = ax2.get_legend_handles_labels()
    all_handles.extend(handles)
    all_labels.extend(labels)


    plt.title(f"grf {side}")
    fig.legend(all_handles, all_labels)
    plt.show()

    try:
        round_output = np.vectorize(lambda n: (np.round(n,2) if n else 1000))
        return round_output(st_seg).tolist()
    except:
        return None

##########################

class GRFSET:

    def  __init__(self, file):
        _df = pd.read_csv(file)
        _a = _df.set_index(list(_df.columns[0:3]))
        _B = pd.DataFrame()
        _B['all_cols'] = _a.apply(lambda row: row.values, axis=1)
        self.dataset = _B
        self.get_mean()
        self.get_std()
       
    def get_mean(self):
        self.set_mean = self.dataset.all_cols.mean()
        self.x = np.arange(len(self.set_mean))
        return self.set_mean

    def get_std(self):
        self.std_dev = np.vstack(self.dataset.all_cols).std(axis=0)
        return self.std_dev
    
    def plot(self, ax=None):
        if not ax:
            ax = plt.gca()
        ax.plot(self.x,self.set_mean, label='mean')
        ax.fill_between(self.x,self.set_mean+self.std_dev, self.set_mean-self.std_dev, facecolor='red', alpha=0.9)

class GRFWalkingRefData(RefData):
    """
            from: https://www.nature.com/articles/s41597-020-0481-z#Sec5

    """
    def __init__(self, compress = 60):
        super(GRFWalkingRefData,self).__init__( "Walking")
        self.set_myself(compress=compress)

    def set_myself(self, compress =60):
        print("assuming stance phase is %f  of the total step duration"%compress)
        module_dir = os.path.dirname(os.path.abspath(__file__))

        #A = GRFSET('GRF_F_V_PRO_left.csv')
        #B = GRFSET('GRF_F_V_PRO_right.csv')
        
        #C = GRFSET('GRF_F_AP_PRO_left.csv')
        #D = GRFSET('GRF_F_AP_PRO_right.csv')
        
        #E = GRFSET('GRF_F_ML_PRO_left.csv')
        #F = GRFSET('GRF_F_ML_PRO_right.csv')
        
        
        
        for axis, movement_direction in zip(["x","y","z"], ["AP","V","ML"]):
            self.reference_curve_dict.update({"the_ground_force_v%s"%axis:[RefDataPrimitive(),RefDataPrimitive()]})
            for i, side in enumerate(["left", "right"]):
                #print(i)
                ## TODO: we cant have a lib that needs to calculate the std and mean deviations each time, this doesnt change it carrying the dataset around requires like 1gb!
                set_name = os.path.join(module_dir,"..","data","grf_data", "GRF_F_%s_PRO_%s.csv"%(movement_direction,side))
                this_set = GRFSET(set_name)
                #print(set_name)
                #print(this_set.set_mean)
                
                self.reference_curve_dict["the_ground_force_v%s"%axis][i].name = "%s Force %s"%(movement_direction, side)
                self.reference_curve_dict["the_ground_force_v%s"%axis][i].mean = extend_y(this_set.set_mean,compress)
                self.reference_curve_dict["the_ground_force_v%s"%axis][i].sd = extend_y(this_set.std_dev,compress)
                self.reference_curve_dict["the_ground_force_v%s"%axis][i].x = compress_x(this_set.x,compress)


def compress_x(x, percent=60):
    
    x = np.array(x)
    
    num_samples = int(np.ceil(percent/100.*len(x)))
    
    compressed = np.hstack([x, np.zeros((num_samples))])

    compressed = np.linspace(0,100, num= len(compressed))
    
    return compressed

def extend_y(x, percent=60):
    
    x = np.array(x)
    
    num_samples = int(np.ceil(percent/100.*len(x)))
    
    compressed = np.hstack([x, np.zeros((num_samples))])
    
    return compressed

#compress_x([1,2,3])
