# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 13:36:12 2022

@author: alafay

runfile('C:/Users/alafay/cernbox/WINDOWS/Desktop/Log_analysis/Python/tests.py', wdir=r'C:/Users/alafay/cernbox/WINDOWS/Desktop/Log_analysis/Python')

"""
import open_log
import read_main_infos
import save_load
import categorize_infos
from tqdm import tqdm
import create_bc_bv
import generate_log_summary
import seu_count
import compare_bc_bv
import plot_evolution
import os
import matplotlib.pyplot as plt
import test_meb

saving_folder = save_load.saving_folder
log_folder = open_log.log_folder

"""
filenames = ["Physics-masked_20211030_235227_h1d0.log",
             "HsLinkTest_20210716_111207.log",
             "DaqBaseTest_20210827_153028.log",
             "Noise_20210915_152227.log",
             "Noise-masked_20210929_183822.log",
             "Pulser-pbpb_20220207_110559.log",
             "Pulser-pp_20210831_145331.log",
             "Physics_20211012_140534.log",
             "RuMonitoring_20210805_174442.log"]

lines = open_log.lines(filenames[0])
"""
    
def open_and_find_infos(filename):
    lines_temp = open_log.open_file(filename)
    read_main_infos.find_infos(lines_temp)


def analyze_noise_masked():
    count = 0
    base = "C:/Users/alafay/cernbox/WINDOWS/Desktop/First peak/Physics-masked_20211007_181/"
    for entry in tqdm(os.listdir(base)):
        if os.path.isfile(os.path.join(base, entry)):
            lines = open_log.lines(entry)
            for line in lines:
                if len(line) >= 4 and "busy chip:49406" in line[3]:
                    count += 1
    return count

def plt_timedelta_triggerfreq():
    plt.figure(figsize = (12,8))
    list_x = []
    list_y = []
    # List all files in a directory using os.listdir
    basepath = "C:/Users/alafay/cernbox/WINDOWS/Desktop/Project/Logs/cru/"
    for entry in tqdm(os.listdir(basepath)):
        if os.path.isfile(os.path.join(basepath, entry)):
            if entry[:14] == "Physics-masked":
                lines = open_log.lines(entry)
                if read_main_infos.find_end_date(lines)[1]:
                    try:
                        trigger = read_main_infos.find_triggerssent(lines)[0]
                        hba = read_main_infos.find_HBA(lines)
                        freq = read_main_infos.find_freq(lines)*10*3
                        timedelta = read_main_infos.proper_script_duration(lines)
                        if freq != 0:
                            list_x.append(trigger)
                            list_y.append(hba)
                            #list_y.append(timedelta.seconds)
                    except IndexError:
                        pass
    plt.ylabel("Triggers sent")
    plt.xlabel("Heart beat accepted")
    plt.plot(list_y,list_x,'x')
    plt.show()
            
            
