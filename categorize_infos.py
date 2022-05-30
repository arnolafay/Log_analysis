###############################################################################
# infos manage the infos of a log file
# we chose an info from INFO, CRITICAL, ERROR, WARNING and it makes a list from
# every info is meeted
###############################################################################

import re
import save_load
import open_log
saving_folder = save_load.saving_folder
from tqdm import tqdm
import os

###############################################################################
# find_dict takes a filename and a dict, and fill the dictionnary of a format
# {key : (count, filename)} that gives a count of how many time each error
# appears , and hte first filename where the test is encountered
def find_dict(filename,type_infos, info_str):
    lines = open_log.lines(filename)
    for l in lines:
        if len(l) >= 3 and l[2] == info_str.upper():
            test = l[1] +"separation" +l[3]
            if not test in type_infos.keys():
                type_infos[test] = [1, filename]
                
            else:
                type_infos[test][0] += 1
    return type_infos
                    
###############################################################################
# write_infos create a txt file from the pickle file saved before
def write(info_str):
    type_infos = save_load.load("sorted" + info_str + "types")
    with open(saving_folder + info_str + "types.txt", "w") as filout:
        for infos in type_infos.keys():
            infos_splitted = infos.split("separation")
            filout.write(f"| {infos_splitted[0]:<29} | {infos_splitted[1]:<115} |" + 
                        f"{type_infos[infos][1] :40} |" + 
                       str(type_infos[infos][0]) + "| \n") 
            
###############################################################################
# sort_info sort the file stored in the pickle file
# it replace all the digits by X, because it always represents an adress, and
# every list of X by only one X
def sort(info_str):
    type_infos = save_load.load(info_str + "types")
    sorted_infos = {}
    for info in type_infos.keys():
        info_saved = info
        info = info.split("separation")
        info[1] = info[1].replace("True","BOOL").replace("False","BOOL")
        info[1] = re.sub(r"[0-9A-F]{2,}", "X", info[1])
        info[1] = re.sub(r"[0-9]+", "X",info[1])
        info[1] = re.sub(r"X+", "X",info[1])
        info[1] = info[1].replace("  "," ")
        info[1] = info[1].replace("[ X,","[X,")
        
        info[1] = re.sub(r"\[BOOL,.*\]", "[BOOL,...]",info[1])
        
        info = info[0] + "separation" + info[1]
        if not info in sorted_infos.keys():
            sorted_infos[info] = type_infos[info_saved]
        else:
            sorted_infos[info][0] += 1
    save_load.save(sorted_infos,"sorted" + info_str + "types")
    
###############################################################################
# do_all gathers the different step for the info textfile to be created for
# all the logfiles contained in open_log.log_folder    
def do_all(info_str = ""):
    type_infos = {}
    basepath = open_log.log_folder
    for entry in tqdm(os.listdir(basepath)):
        if os.path.isfile(os.path.join(basepath, entry)):
            type_infos = find_dict(entry, type_infos, info_str)
    save_load.save(type_infos, info_str + "types")
    sort(info_str)
    write(info_str)
    