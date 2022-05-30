###############################################################################
# plot_evolution takes the saved file in pickle format and plot the evolution
# in time of the proportion of (busy chip, busy violation or seu_count) for
# each chip
###############################################################################

import save_load
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import collections
import matplotlib
from matplotlib.colors import LogNorm
save_picture = "C:/Users/alafay/cernbox/WINDOWS/Desktop/Log_analysis/Pictures/"
np.seterr(divide='ignore', invalid='ignore')
plt.rcParams.update({'figure.max_open_warning': 0})

###############################################################################
# filter_by_zone takes the id of a zone and  a dict and returns the same dict
# filtered for every chip to be part of the zone and the type_log is in
# ["program","ecs","DaqBaseTest","PRBS","Noise","Noise-masked", "Physics",
#  "Physics-masked","program_ru","Pulser", "Pulser-PbPb","Pulser-pp","RuMonitoring"]
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
# and gives (list_date, nb of errors/nb of triggers) being arrays used to plot
def give_tab(dict_, h, d, f, z, type_log = ""):
    date_start = datetime(2021,10,21)
    date_end = datetime(2022,5,1)
    date_list = pd.date_range(date_start, date_end)
    
    temp_dict = filter_by_zone(dict_, h, d, f, z, type_log)
    
    list_keys = list(temp_dict.keys())
    # array stores the sum of the errors/nb of triggers
    tab = np.zeros((len(list_keys),len(date_list)))
    
    for i in range(len(list_keys)):
        list_events = temp_dict[list_keys[i]]
        for event in list_events:
            date = event[0]
            time_delta = (date - date_start).days
            if time_delta != 148:
                tab[i,time_delta] += event[1]
    for time_delta in range(len(tab[0])):
        if np.sum(tab[:,time_delta]) > 3e-5:
            print((h,d,f,z))
            print(time_delta)
    return list_keys, date_list, tab

###############################################################################  
# plot_disk_tab create a plot for a given disk and a given typ_log (if 
# type_log = "", not filtered in type_log)
# it creates several subplot for each zone of the disk and save the whole plot
def plot_disk_tab(dict_, h, d, list_chip, type_error = "", type_log = ""):
    fig, axs = plt.subplots(2, 4, figsize=(28,12))
    
    # for each type_of_error, we gives vmin and vmax for the plots, and ratio
    # and threshold to determinate which chips are not working well
    if type_error == "seu count trigger" :
        ratio = 0.1
        threshold = 1e-3
        vmin = 1e-11
        vmax = 1e-7
        
    elif type_error == "seu count hb" :
        ratio = 0.1
        threshold = 1e-3
        vmin = 1e-6
        vmax = 1e-2
    
    elif type_error == "busy violation":
        ratio = 0.05
        threshold = 1e-10
        vmin = 1e-11
        vmax = 1e-7
        
    elif type_error == "busy chip":
        ratio = 0.1
        threshold = 1e-10
        vmin = 1e-11
        vmax = 1e-7
    
    fig.suptitle(f'Evolution of the ratio number of {type_error} per number of triggers for the disk h{h}d{d} - {type_log}', fontsize = 20)
    
    for f in [0,1]:
        for z in [0,1,2,3]:
            
            matplotlib.rc('font', size=14)
            matplotlib.rc('axes', titlesize=14)
            
            ax = axs[f,z]
            list_keys, date_list, tab = give_tab(dict_, h, d, f, z, type_log.replace("All",""))
            
            for i in range(len(list_keys)):
                if float((tab[i]> threshold).sum()) / float(len(date_list)) > ratio:
                    if not list_keys[i] in list_chip:
                        list_chip.append(list_keys[i])
            
            ax.set_title(f'f{f}z{z}', fontsize = 15)
            
            list_keys_chip = [key[4:7] for key in list_keys]
            
            n = len(list_keys)
            ax.set_yticks(ticks = np.arange(0.5,n+0.5))
            ax.set_yticklabels(list_keys_chip)
            
            ax.pcolor(tab, cmap="jet", norm=LogNorm(vmin,vmax))
                
            if f != 1:
                ax.set_xticklabels( () )
            else:
                n = len(date_list)
                date_list_2 = [date_list[0].date() 
                               ,date_list[n//4].date() 
                               ,date_list[2*n//4].date()
                               ,date_list[3*n//4].date()
                               ,date_list[n-1].date()]
                ax.set_xticks(ticks=[0,50,100,150,200])
                ax.set_xticklabels(labels=date_list_2)
                
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_rotation('vertical')
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize('x-small')
    
    pcm = ax.pcolormesh(tab,cmap = "jet", norm = LogNorm(vmin,vmax))

    fig.colorbar(pcm, ax = axs.ravel().tolist())
    plt.savefig(save_picture + "Evolution/" + type_log + "/" + type_error.replace(" ","_") + "/" + f'h{h}d{d}' + ".png")
    plt.close()
    
    
###############################################################################  
# plot_disk_tab_meb create a plot for a given disk and a given typ_log (if 
# type_log = "", not filtered in type_log)
# it creates several subplot for each zone of the disk and save the whole plot
def plot_disk_tab_meb(dict_, h, d, type_error = "", type_log = ""):
    fig, axs = plt.subplots(2, 4, figsize=(28,12))
    
    fig.suptitle(f'Evolution of the ratio number of {type_error} per number of triggers for the disk h{h}d{d} - {type_log}', fontsize = 20)
    
    for f in [0,1]:
        for z in [0,1,2,3]:
            
            matplotlib.rc('font', size=14)
            matplotlib.rc('axes', titlesize=14)
            
            ax = axs[f,z]
            list_keys, date_list, tab = give_tab(dict_, h, d, f, z, type_log.replace("All",""))
            

            
            ax.set_title(f'f{f}z{z}', fontsize = 15)
            
            list_keys_chip = [key[4:7] for key in list_keys]
            
            n = len(list_keys)
            ax.set_yticks(ticks = np.arange(0.5,n+0.5))
            ax.set_yticklabels(list_keys_chip)
            
            ax.pcolor(tab, cmap="jet")
                
            if f != 1:
                ax.set_xticklabels( () )
            else:
                n = len(date_list)
                date_list_2 = [date_list[0].date() 
                               ,date_list[n//4].date() 
                               ,date_list[2*n//4].date()
                               ,date_list[3*n//4].date()
                               ,date_list[n-1].date()]
                ax.set_xticks(ticks=[0,50,100,150,200])
                ax.set_xticklabels(labels=date_list_2)
                
            for tick in ax.xaxis.get_major_ticks():
                tick.label.set_rotation('vertical')
            for tick in ax.yaxis.get_major_ticks():
                tick.label.set_fontsize('x-small')
    
    pcm = ax.pcolormesh(tab,cmap = "jet")

    fig.colorbar(pcm, ax = axs.ravel().tolist())
    plt.savefig(save_picture + "Evolution/" + type_log + "/" + type_error.replace(" ","_") + "_meb" + "/" + f'h{h}d{d}' + ".png")
    plt.close()


###############################################################################
# do_all saves the files for each disk, each error and each type_log where the 
# error is encountered, and creates a list of the chips where the error are
# particularly meeted
def do_all():
    """
    list_chip_bv = []
    type_error = "busy violation"
    dict_bv = save_load.load("dict_busy_violation")
    for h in [0,1]:
        for d in range(5):
            plot_disk_tab(dict_bv, h, d, list_chip_bv, type_error, "All")
            for type_log in ["Physics-masked", "Noise"]:
               plot_disk_tab(dict_bv, h, d, list_chip_bv, type_error, type_log)
    save_load.save(list_chip_bv, "chips_busy_violation")
    
    list_chip_bc = []
    type_error = "busy chip"
    dict_bc = save_load.load("dict_busy_chip")
    for h in [0,1]:
        for d in range(5):
            plot_disk_tab(dict_bc, h, d, list_chip_bc, type_error, "All")
            for type_log in ["Physics-masked", "Noise"]:
               plot_disk_tab(dict_bc, h, d, list_chip_bc, type_error, type_log)
    save_load.save(list_chip_bc, "chips_busy_chip")
    
    """
    list_chip_seu_trigger = []
    type_error = "seu count trigger"
    dict_seu_count = save_load.load("dict_seu_count_trigger")
    for h in [0,1]:
        for d in range(5):
            plot_disk_tab(dict_seu_count, h, d, list_chip_seu_trigger, type_error, "All")
            for type_log in ["Physics-masked", "Noise", "Pulser", "Pulser-PbPb", "Pulser-pp"]:
               plot_disk_tab(dict_seu_count, h, d, list_chip_seu_trigger, type_error, type_log)
    save_load.save(list_chip_seu_trigger, "chips_seu_count_trigger")
    
    list_chip_seu_hb = []
    type_error = "seu count hb"
    dict_seu_count = save_load.load("dict_seu_count_hb")
    for h in [0,1]:
        for d in range(5):
            plot_disk_tab(dict_seu_count, h, d, list_chip_seu_hb, type_error, "All")
            for type_log in ["Physics-masked", "Noise", "Pulser", "Pulser-PbPb", "Pulser-pp"]:
               plot_disk_tab(dict_seu_count, h, d, list_chip_seu_hb, type_error, type_log)
    save_load.save(list_chip_seu_hb, "chips_seu_count_hb")
    """
    
    type_error = "busy chip"
    dict_bc = save_load.load("dict_bc_meb")
    for h in [0,1]:
        for d in range(5):
            plot_disk_tab_meb(dict_bc, h, d, type_error, "All")
            for type_log in ["Physics-masked", "Noise"]:
               plot_disk_tab_meb(dict_bc, h, d, type_error, type_log)
    """