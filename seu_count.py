#############################################################################
# seu_count is the first step to analyse the seu_count 
#############################################################################

import open_log
from datetime import datetime
import re
from tqdm  import tqdm
import os
import save_load
import numpy as np
import read_main_infos
np.seterr(divide='ignore', invalid='ignore')
save_picture = "C:/Users/alafay/cernbox/WINDOWS/Desktop/Log_analysis/Pictures/"

###############################################################################
def extract_id_first_part(txt):
    h = int(txt[1])
    d = int(txt[4])
    f = int(txt[7])
    z = int(txt[10])
    return(h,d,f,z)


###############################################################################
# tr = [X, X, X] (# of X changing)
def extract_id_from_list(txt):
    list_id = []
    id_ = ""
    for char in txt:
        try:
            int(char)
            id_ += char
        except ValueError:
            if id_ != "":
                list_id.append(int(id_))
            id_ = ""
    return list_id
    

###############################################################################
def extract_from_lines(filename, dict_seu_count_trigger, dict_seu_count_hb):
    lines = open_log.lines(filename)
    type_exp = open_log.types(filename)     
    trs,seu_counts = [],[]
    
    try:
        hb =  read_main_infos.find_HB(lines)
    except IndexError:
        hb = 0
    
    try:
        trig =  read_main_infos.find_triggerssent(lines)
        trigger = trig[0]
        correction = trig[1]
    except IndexError:
        trigger = 0 
        correction = False
    if (trigger == 0 and hb == 0) or not correction:
        return
    
    for line in lines:
        if len(line) >= 4 and "end of run" in line[3]:
            return
        if len(line) >= 4 and line[1] == "SensorsDataPoint" and bool(re.match(r"RDO ..:h.-d.-f.-z., con ., tr = ", line[3])):
            date = datetime.strptime(line[0], "%Y-%m-%d %H:%M:%S,%f")
            h,d,f,z = extract_id_first_part(re.search(r"h.-d.-f.-z.", line[3]).group())
            con = int(re.search(r"con .", line[3]).group()[4])
            trs = extract_id_from_list(re.search(r"tr = .*", line[3]).group()[5:])
        elif len(line) >= 4 and line[1] == "SensorsDataPoint" and bool(re.match(r"RDO ..:h.-d.-f.-z., con ., seu_count = ", line[3])):
            seu_counts = extract_id_from_list(re.search(r"seu_count = .*", line[3]).group()[5:])
        
        for tr in trs:
            chip = h,d,f,z,tr,con    
            if not chip in dict_seu_count_trigger.keys():
                dict_seu_count_trigger[chip] = []
            if not chip in dict_seu_count_hb.keys():
                dict_seu_count_hb[chip] = []
        
        if trs != [] and seu_counts != []:
            for i in range(len(trs)):
                tr = trs[i]
                chip = h,d,f,z,tr,con   
                seu_count = seu_counts[i]
                if seu_count > 10:
                    if trigger != 0:
                        dict_seu_count_trigger[chip].append((date,float(seu_count)/float(trigger),type_exp))
                    elif trigger == 0 and hb != 0:
                        dict_seu_count_hb[chip].append((date,float(seu_count)/float(hb),type_exp))
                
            trs = []
            seu_counts = []

###############################################################################
def extract_from_lines_histogramme(filename, tab):
    lines = open_log.lines(filename)
    type_exp = open_log.types(filename)     
    trs,seu_counts = [],[]
    
    try:
        hb =  read_main_infos.find_HB(lines)
    except IndexError:
        hb = 0
    
    try:
        trig =  read_main_infos.find_triggerssent(lines)
        trigger = trig[0]
        correction = trig[1]
    except IndexError:
        trigger = 0 
        correction = False
    if (trigger == 0 and hb == 0) or not correction:
        return

    for line in lines:
        if len(line) >= 4 and "end of run" in line[3]:
            return
        if len(line) >= 4 and line[1] == "SensorsDataPoint" and bool(re.match(r"RDO ..:h.-d.-f.-z., con ., tr = ", line[3])):
            date = datetime.strptime(line[0], "%Y-%m-%d %H:%M:%S,%f")
            h,d,f,z = extract_id_first_part(re.search(r"h.-d.-f.-z.", line[3]).group())
            con = int(re.search(r"con .", line[3]).group()[4])
            trs = extract_id_from_list(re.search(r"tr = .*", line[3]).group()[5:])
        elif len(line) >= 4 and line[1] == "SensorsDataPoint" and bool(re.match(r"RDO ..:h.-d.-f.-z., con ., seu_count = ", line[3])):
            seu_counts = extract_id_from_list(re.search(r"seu_count = .*", line[3]).group()[5:])
        
        
        if trs != [] and seu_counts != []:
            for i in range(len(trs)):
                tr = trs[i]
                chip = h,d,f,z,tr,con   
                seu_count = seu_counts[i]
                if (trigger != 0 or hb != 0):
                    tab.append(seu_count)
                
            trs = []
            seu_counts = []
            
            
###############################################################################          
# do_all create a dictionnary and fill it with every error of every file of
# the open_log.log_folder
def do_all():
    basepath = open_log.log_folder
    dict_seu_count_hb = {}
    dict_seu_count_trigger = {}
    list_seu_count = []
    for entry in tqdm(os.listdir(basepath)):
        if os.path.isfile(os.path.join(basepath, entry)):
            extract_from_lines(entry,dict_seu_count_trigger, dict_seu_count_hb)
            extract_from_lines_histogramme(entry, list_seu_count)
    save_load.save(dict_seu_count_trigger, "dict_seu_count_trigger")
    save_load.save(dict_seu_count_hb, "dict_seu_count_hb")
    save_load.save(list_seu_count, "list_seu_count")