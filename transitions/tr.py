#!/lscratch/frekle/miniconda3/envs/automl/bin/python

# vim:fenc=utf-8

#
# @author      : frekle (frekle@bml01.mech.kth.se)
# @file        : a
# @created     : Thursday Jun 27, 2024 15:21:48 CEST
#

##### this will be obviously missing the data!

## you can get it with
## $ wget https://springernature.figshare.com/ndownloader/files/28998063
##
## if they change the link you will need to find it. it's a 1.5gb file


import numpy as np
import h5py
# this shebang wont use conda stuff i think ####!/usr/bin/env python3
import matplotlib.pyplot as plt

class ref ():
    def __init__(self,array):
        self.arr = array
        self.mean = None
        self.sd = None
        if array.any():
            self.mean = array.mean(axis=0)
            self.sd = array.std(axis=0)

class ref3d():
    def __init__(self,arrayx, arrayy, arrayz):
        self.x = ref(arrayx)
        self.y = ref(arrayy)
        self.z = ref(arrayz)
        self.sagittal_only=False

f = h5py.File('28998063','r')

walk = "Walk/s1/i0"

ramp = "Walk/s1/i10" ##our ramp is 9 degrees 10 is close enough

stairs = "Stair/s2w/i25"

all_subs=['AB01', 'AB02', 'AB03', 'AB04', 'AB05', 'AB06', 'AB07', 'AB08', 'AB09', 'AB10']

joint_refs = {}

joint_list = ['AnkleAngles', 'FootProgressAngles', 'HipAngles', 'KneeAngles', 'PelvisAngles']

#modes = ['events', 'forceplates', 'jointAngles', 'jointForces', 'jointMoments', 'jointPowers', 'markers']
modes = ['jointAngles', 'jointMoments']

act_dic = {"Walk":walk,
           "Ramp":ramp,
           "Stairs":stairs}

remove_modes_for_now  = {'events', 'forceplates', 'markers',}
for act, act_name in act_dic.items():
    modes = set(f.get(f"/Normalized/AB01/{act_name}").keys()) 
    modes -= remove_modes_for_now
    print(modes)
    for mode in modes:
        for joint in list(f.get(f"/Normalized/AB01/{act_name}/{mode}").keys()):#joint_list:
            joint_stepsx = []
            joint_stepsy = []
            joint_stepsz = []
            only_sag = None
            for sub in all_subs:
                try:
                    some_walk_data = np.array(f.get(f'/Normalized/{sub}/{act_name}/{mode}/{joint}'))
                except:
                    continue
            #ab01run = f.get('/Normalized/AB01/Run')

            ## to show the variables in that level
            #print(ab01run.get('s1x8').get('i0').get('jointAngles').keys())
                if not some_walk_data.shape:
                    continue
                for i in range(some_walk_data.shape[0]):
                    #plt.plot(some_walk_data[i,0,:], 'r')
    
                    ## because this dataset trully loves me they decided some data will only be in the sagital plane, so we need to account for that too.
                    
                    if len(some_walk_data.shape) == 3:
                        joint_stepsx.append(some_walk_data[i,0,:])
                        joint_stepsy.append(some_walk_data[i,1,:])
                        #plt.plot(some_walk_data[i,1,:], 'g')
                        zdata = some_walk_data[i,2,:]
                        only_sag = False
                        if mode == "jointAngles" and joint == "PelvisAngles":
                 
                            # the person can be looking back, so there will be a +-180 here and this will give me a huge standard deviation, so I need to check if this is the case before adding the step¨
                            if zdata.mean(axis = 0) > 150:
                                zdata -= 180
                            if zdata.mean(axis = 0) < -150:
                                zdata += 180
                            plt.plot(some_walk_data[i,2,:], 'b')
                            plt.plot(zdata, 'cyan')
                        
                        joint_stepsz.append(zdata)
                    else:
                        joint_stepsx = some_walk_data[i,:]
                        joint_stepsy = None
                        joint_stepsz = None
                        only_sag = True


            joint_arrx = np.array(joint_stepsx)#.transpose()
            joint_arry = np.array(joint_stepsy)#.transpose()
            joint_arrz = np.array(joint_stepsz)#.transpose()

            #refname = joint+mode #they already append the modality to the name soo..
            refname = act+joint
            this_ref = ref3d(joint_arrx, joint_arry, joint_arrz)
            this_ref.sagittal_only = only_sag
            joint_refs.update({refname:this_ref})

plt.show()

def main():
    for act, act_name in act_dic.items():
        modes = set(f.get(f"/Normalized/AB01/{act_name}").keys()) 
        modes -= remove_modes_for_now
        #joint_name = "AnkleAngles"
        for mode in modes:
            for joint_name in list(f[f"/Normalized/AB01/{act_name}/{mode}"].keys()):#joint_list:
            
                #if joint_name in ['StrideDetails']:
                #    continue
                ## for some people some data is missing, 
                refname = act+joint_name

                if not refname in joint_refs.keys():
                    print("skipping:"+refname )
                    continue
                joint_ref = joint_refs[refname] 
                t = np.linspace(0,1,num=joint_ref.x.mean.shape[0])
                mx =   joint_ref.x.mean
                mpsx = joint_ref.x.mean+joint_ref.x.sd
                mmsx = joint_ref.x.mean-joint_ref.x.sd
                
                if not joint_ref.sagittal_only:
                    my =   joint_ref.y.mean
                    mpsy = joint_ref.y.mean+joint_ref.y.sd
                    mmsy = joint_ref.y.mean-joint_ref.y.sd
                    
                    mz =   joint_ref.z.mean
                    mpsz = joint_ref.z.mean+joint_ref.z.sd
                    mmsz = joint_ref.z.mean-joint_ref.z.sd
                    #plt.plot(x,m, 'r')
                    #plt.plot(x, mps )
                    #plt.plot(x, mms)
                    
                    with open(f"ref3dNi/{act}{joint_name}.dat", "w") as fd:
                        print("ghot here")
                        fd.write(f"t mx mpsx mmsx my mpsy mmsy mz mpsz mmsz\n" )    
                        for ti, mix, mpsix, mmsix, miy, mpsiy, mmsiy, miz, mpsiz, mmsiz in zip(t,mx,mpsx,mmsx,my,mpsy,mmsy,mz,mpsz,mmsz):
                            #f.write(f"{xi}, {mi}, {mpsi}, {mmsi}\n" )
                            fd.write(f"{ti} {mix} {mpsix} {mmsix} {miy} {mpsiy} {mmsiy} {miz} {mpsiz} {mmsiz}\n" )
                
                else:
                                        
                    with open(f"ref3dNi/{act}{joint_name}Sag.dat", "w") as fd:
                        print("ghot here too")
                        fd.write(f"t mx mpsx mmsx \n" )    
                        for ti, mix, mpsix, mmsix in zip(t,mx,mpsx,mmsx):
                            #f.write(f"{xi}, {mi}, {mpsi}, {mmsi}\n" )
                            fd.write(f"{ti} {mix} {mpsix} {mmsix} \n" )
                
    #    plt.show()
if __name__ == '__main__':
	main()


