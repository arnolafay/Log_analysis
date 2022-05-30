#############################################################################
# compare_bc_bv allows to compare the apearances of errors for "busy chip" (bc)
# and "busy violation" (bv)
#############################################################################

import save_load
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import collections
import matplotlib
import os
import copy
np.seterr(divide='ignore', invalid='ignore')

save_picture = "C:/Users/alafay/cernbox/WINDOWS/Desktop/Project/Pictures/"

###############################################################################
# filter_by_zone takes the id of a zone and  a dictionnary
# and returns the same dict filtered for every chip to be part of the zone 
# type_log from ["program","ecs","DaqBaseTest","PRBS","Noise","Noise-masked",
#                "Physics","Physics-masked","program_ru","Pulser",
#                "Pulser-PbPb","Pulser-pp","RuMonitoring"]
   
def filter_by_zone(dict_, h,d,f,z, type_log= ""):
    if type_log == "":
        dict_zone = {key: dict_[key] for key in dict_.keys() 
                     if (key[0] == h and key[1] == d and key[2] == f and key[3] == z)}
    else:
        dict_zone = {}
        for key in dict_.keys():
            if key[0] == h and key[1] == d and key[2] == f and key[3] == z:
                events = dict_[key]
                dict_zone[key] = [event for event in events if event[2] == type_log]
    dict_zone = collections.OrderedDict(sorted(dict_zone.items()))       
    return dict_zone

###############################################################################
# give_arrays take a dictionnary of the form {chip:[(date, nb given by error, type_log)]}
# and gives X1,Y1 being arrays used to plot
# X1 is a list of dates
# Y1 is the nb of errors/nb of triggers during a day
def give_array(dict_):

    date_start = datetime(2021,9,1)
    date_end = datetime(2022,5,1)
    date_list = pd.date_range(date_start, date_end)
    
    # array stores the sum of the errors/nb of triggers
    array = np.zeros((len(date_list)))
    
    for list_event in dict_.values():
        for event in list_event:
            date = event[0]
            time_delta = (date - date_start).days
            array[time_delta] += event[1]
    
    # we then divide by the number of chips in the given dict to have the
    # total number of triggers (nb of trigger for 1 chip * nb of chips)
    return (date_list, array/len(dict_.keys()))


###############################################################################                
# simple_plot plots [nb of errors (nb given by the bc or bv)/nb of triggers] by day
def simple_plot(dict_bc, dict_bv):
    list_date, bc_array = give_array(dict_bc)
    list_date, bv_array = give_array(dict_bv)
    
    date_start, date_end = list_date[0],  list_date[-1]
    #plot the figure
    plt.figure(figsize = (12,8))
    plt.yscale("log")
    plt.ylim(1e-12,1e-1)
    plt.title("Number of errors / number of triggers per day for the whole detector",fontsize=15)
    plt.xlim(date_start,date_end)
    plt.plot(list_date, bc_array,'rx', label = "busy chip")
    plt.plot(list_date, bv_array,'bx',label = "busy violations")
    plt.legend()
    
    print(len(bc_array))
    print(len(bv_array))
    
    plt.show()
    

###############################################################################
# plot_disk gives the evolution of nb of error per day for each disk
def plot_disk(h,d, type_log = ""):
    dict_bc = save_load.load("dict_busy_chip")
    dict_bv = save_load.load("dict_busy_violation")
    
    date_start = datetime(2021,9,1)
    date_end = datetime(2022,5,1)
    
    fig, axs = plt.subplots(2, 4, figsize=(20,12))
    
    fig.suptitle(f'Number of errors / number of triggers per day for h{h}d{d} - {type_log}', fontsize = 25)
    
    for f in [0,1]:
        for z in [0,1,2,3]:
            matplotlib.rc('font', size=14)
            matplotlib.rc('axes', titlesize=14)
            
            ax = axs[f,z]
            list_date, bc_array = give_array(filter_by_zone(dict_bc,h,d,f,z, type_log))
            list_date, bv_array = give_array(filter_by_zone(dict_bv,h,d,f,z, type_log))
            ax.plot(list_date, bc_array, 'rx', label = "busy chip")
            ax.plot(list_date, bv_array, 'bx', label = "busy violations")
            ax.set_title(f'f{f}z{z}', fontsize = 20)
            ax.set_yscale("log")
            ax.set_ylim(1e-12,1e-1)
            ax.set_xlim(date_start,date_end)
            if f != 1:
                ax.set_xticklabels( () )
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_rotation('vertical')
            if z != 0:
                ax.set_yticklabels( () )
            
    plt.legend()
    if type_log == "":
        if not os.path.exists(save_picture + "all/"):
            os.makedirs(save_picture + "all/")
        plt.savefig(save_picture + "all/" + f'h{h}d{d}' + ".png")
    else:
        if not os.path.exists(save_picture + type_log + "/"):
            os.makedirs(save_picture + type_log + "/")
        plt.savefig(save_picture + "Error per day/" + type_log + "/" + f'h{h}d{d}' + ".png")
 
###############################################################################
# plot_bv_bc gives the number given by the errors busy violation and busy chip
# for a chip where the two errors appear at a difference of time of less than
# timedelta
def plot_bv_bc(dict_bc,dict_bv, time_delta = timedelta(seconds=10)):
    
    list_bc = []
    list_bv = []
    
    count = 0
    
    copied_dict_bc = copy.deepcopy(dict_bc)
    copied_dict_bv = copy.deepcopy(dict_bv)
    
    for chip in dict_bc.keys():
        for event_bv in dict_bv[chip]:
            for event_bc in copied_dict_bc[chip]:
                if np.abs(event_bv[0] - event_bc[0]) < time_delta:
                    list_bc.append(event_bc[1])
                    list_bv.append(event_bv[1])
                    
                    copied_dict_bv[chip].remove(event_bv)
                    copied_dict_bc[chip].remove(event_bc)
                    
                    count += 2
                    
    
    count_bv_wo_bc = np.sum([len(value) for value in copied_dict_bv.values()])
    count_bc_wo_bv = np.sum([len(value) for value in copied_dict_bc.values()])
                    
        
        
    
    plt.figure(figsize=(15,10))
    plt.plot(list_bc,list_bv,'x')
    plt.xlim(1e-11,1e-5)
    plt.ylim(1e-11,1e-5)
    plt.text(1.1e-11, 3e-6, f"Number of busy violation w/o busy chip : {count_bv_wo_bc} \n" +
                            f"Number of busy chip w/o busy violation : {count_bc_wo_bv} \n"
                            f"Number of plotted errors : {count}")
    plt.title("Pairs busy chip - busy violation for the same chip", fontsize = 18)
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Busy chip")
    plt.ylabel("Busy violation")
    plt.show()
    
    
    
