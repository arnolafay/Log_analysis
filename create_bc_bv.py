###############################################################################
# bc_bv is the first step to analyse the errors (bc busy chip - bv busy violation) 
###############################################################################

import save_load
import open_log
from datetime import datetime
import read_main_infos
import re
import os
from tqdm import tqdm

###############################################################################
# extract_id give the id of an error
# it converts "hA-dB-fC-zD, sensor [tr,id,con] [E, F, G]"
# to (A, B, C, D, E, F, G)
def extract_id(txt):
    h = int(txt[1])
    d = int(txt[4])
    f = int(txt[7])
    z = int(txt[10])
    tr = int(txt[33:35])
    id_ = int(txt[36:38])
    con = int(txt[39:41])
    return(h,d,f,z,tr,id_,con)

###############################################################################
# extract_from_lines extracts every error from the file and stores them in a 
# dictionnary given in argument according to this : {chip:([dates],[number given by the error])}
def extract_from_lines(filename, dict_error, error = ""):
    lines = open_log.lines(filename)
    type_exp = open_log.types(filename) 
    try :
        trig = read_main_infos.find_triggerssent(lines)   
        number_of_triggers = trig[0]
        correction = trig[1]
    except IndexError:
        return
    if number_of_triggers == 0 or not correction:
        return
    for line in lines:
        match = re.search("h.-d.-f.-z., sensor \[tr,id,con\] \[..,..,..\]",str(line))
        if bool(match):
            id_chip = match.group()
            chip = extract_id(id_chip)
            if not chip in dict_error.keys():
                dict_error[chip] = []
        if len(line) >= 4 and line[2] == "WARNING" and ("busy " + error) in line[3]:
            date = datetime.strptime(line[0], "%Y-%m-%d %H:%M:%S,%f")
            nb_error = line[3].split("busy "+ error + ":")[1]
            dict_error[chip].append((date,float(nb_error)/float(number_of_triggers),type_exp))

###############################################################################
# extract_from_lines extracts every error from the file and stores them in a 
# dictionnary given in argument according to this : {chip:([dates],[number given by the error])}
def extract_from_lines_MEB(filename, dict_error, error = ""):
    lines = open_log.lines(filename)
    type_exp = open_log.types(filename) 
    try :
        trig = read_main_infos.find_triggerssent(lines)   
        number_of_triggers = trig[0]
        correction = trig[1]
    except IndexError:
        return
    if number_of_triggers == 0 or not correction:
        return
    for line in lines:
        match = re.search("h.-d.-f.-z., sensor \[tr,id,con\] \[..,..,..\]",str(line))
        if bool(match):
            id_chip = match.group()
            chip = extract_id(id_chip)
            if not chip in dict_error.keys():
                dict_error[chip] = []
        if len(line) >= 4 and line[2] == "WARNING" and ("busy " + error) in line[3]:
            date = datetime.strptime(line[0], "%Y-%m-%d %H:%M:%S,%f")
            nb_error = int(line[3].split("busy "+ error + ":")[1])
            if int(number_of_triggers)/2 % 65536 == nb_error:
                dict_error[chip].append((date, 1, type_exp))
                print(1)
            elif int(number_of_triggers) % 65536 == nb_error + 1:
                dict_error[chip].append((date, 2, type_exp))
                print(2)
            elif int(number_of_triggers) % 65536 == nb_error:
                dict_error[chip].append((date, 3, type_exp))
                print(3)
            if nb_error > 1000:
                print(filename)
                

###############################################################################
# do_all create a dictionnary and fill it with every error of every file of
# the open_log.log_folder
def do_all():
    basepath = open_log.log_folder
    dict_bv = {}
    dict_bc = {}
    dict_bc_meb = {}
    for entry in tqdm(os.listdir(basepath)):
        if os.path.isfile(os.path.join(basepath, entry)):
            extract_from_lines(entry, dict_bv, "violations")
            extract_from_lines(entry, dict_bc, "chip")
            extract_from_lines_MEB(entry, dict_bc_meb, "chip")
    save_load.save(dict_bv, "dict_busy_violation")
    save_load.save(dict_bc, "dict_busy_chip")
    save_load.save(dict_bc_meb, "dict_bc_meb")
