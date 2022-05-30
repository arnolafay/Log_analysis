###############################################################################
# generate_log_summary takes log file in entry and create a summary of this 
# log file containing the most important informations of it
###############################################################################

import open_log
import save_load
import read_main_infos
import re
import os
from tqdm import tqdm
saving_folder = save_load.saving_folder
log_summary_folder = "C:/Users/alafay/cernbox/WINDOWS/Desktop/Log_analysis/Log_Summaries/"

###############################################################################
# print_line take a line of information as created by the open_log file and
# and gives a string containing the informations
def print_info_line(line):
    res =  f"{str(line[0]) :<26} - "
    res += f"{str(line[1]) :<23}- "
    res += f"{str(line[2]) :<7} - "
    res += str(line[3]) + "\n"
    return res

###############################################################################
# print_normal_line without knowing the format of the line 
def print_normal_line(line):
    if len(line) == 4:
        return print_info_line(line)
    else:
        res = ""
        for word in line:
            res += str(word) + "    "
        res += "\n"
        return res

###############################################################################
# find_concerned_zone takes a line f information and return the zone written
# in it if there is some. Otherwise it returns None 
def find_concerned_zone(line):
    pattern = "h.-d.-f.-z."
    match = re.search(pattern, line[3])
    try:
        obj = match.group()
        return obj[7],obj[10]
    except AttributeError or IndexError:
        return                 

###############################################################################    
# event_0 takes a line where there is a number of event and check if this 
# number is 0
def event_0(line):
    temp = line[3].split("events:")
    number = int(temp[1])
    return number == 0

###############################################################################
# list_of_unworking_chip_fifo gives the chip where a 
# "lane_fifo_start () != chip_events ()" error occured in the logfile
def list_of_unworking_chip_fifo(lines):
    list_res = []
    for line in lines:
        if len(line) >= 4 and bool(re.search(r"lane_fifo_start \(.*\) != chip_events \(.*\)",line[3])):
            match = re.search(r"h.-d.-f.-z., sensor \[tr,id,con\] \[.*, .*, .*\]",line[3])
            list_res.append(line[3][match.start():match.end()])
    return list_res

###############################################################################
# list_of_unworking_chip_events gives the chip where a 
# "events () != triggers sent ()" error occured in the logfile
def list_of_unworking_chip_events(lines):
    list_res = []
    for line in lines:
        if len(line) >= 4 and bool(re.search(r"events \(.*\) != triggers sent \(.*\)",line[3])):
            match = re.search(r"h.-d.-f.-z., sensor \[tr,id,con\] \[.*, .*, .*\]",line[3])
            list_res.append(line[3][match.start():match.end()])
    return list_res

###############################################################################
# generate_file generate the summary of the given log file
def generate_file(filename):
    lines = open_log.lines(filename)
    
    
    # we see if there are some zone hit by warnings or errors
    error_zones = []
    warning_zones = []
    
    for line in lines:
        if len(line) >= 3 and line[2] == "ERROR":
            zone = find_concerned_zone(line)
            if zone != None and not zone in error_zones:
                error_zones.append(zone)
                
        if len(line) >= 3 and line[2] == "WARNING":
            zone = find_concerned_zone(line)
            if zone != None and not zone in warning_zones:
                warning_zones.append(zone)
                
    
    filetype = open_log.types(filename)
    main_infos = read_main_infos.find_infos(lines)
    
    # we take a new title for the file
    title = "testbench/" + filetype + "_" + main_infos["start_date"][:19].replace(":",".")  + main_infos["disk"] + ".txt"
    title = title.replace(" ","_")
    
    with open(log_summary_folder + title, "w") as filout:
        # it writes all the information of read_main_infos and the zones
        # concerned by an error or a warning
        filout.write(f"{'Original filename : ':<28}" + filename + "\n")
        filout.write(f"{'Disk concerned : ':<28}" + main_infos["disk"].replace(" ","") + "\n")
        filout.write(f"{'Start of the script : ':<28}" + main_infos["start_date"] + "\n")
        filout.write(f"{'End of the script : ':<28}" + main_infos["end_date"] + "\n")
        filout.write(f"{'Nb of triggers sent : ':<28}" + str(main_infos["number_of_triggers_sent"]) + "\n")
        filout.write(f"{'Correction of nb of triggers : ':<28}" + str(main_infos["correction_triggers"]) + "\n")
        filout.write(f"{'Frequency : ':<28}" + str(main_infos["freq"]*10**-3) + " kHz\n")
        filout.write(f"{'Disk concerned : ':<28}" + main_infos["disk"].replace(" ","") + "\n")
        filout.write(f"{'The script ended properly : ':<28}" + main_infos["proper_end"] + "\n")
        
        filout.write(f"{'Script duration : ':<28}" + str(main_infos["script_duration"]) + "\n")
        if main_infos["correction_triggers"]:
            filout.write(f"{'Acquisition duration : ':<28}" + str(main_infos["time_acquisition"]) + " s\n")
        
        if main_infos["mode"] == "continuous":
            filout.write(f"{'Mode : ':<28}" + "Continuous \n")
            filout.write(f"{'Nb of SOC : ':<28}" + str(main_infos["soc"]) + "\n")
            filout.write(f"{'Nb of EOC : ':<28}" + str(main_infos["eoc"]) + "\n")
            
        elif main_infos["mode"] == "triggered":
            filout.write(f"{'Mode : ':<28}" + "Triggered \n")
            filout.write(f"{'Nb of SOT : ':<28}" + str(main_infos["sot"]) + "\n")
            filout.write(f"{'Nb of EOT : ':<28}" + str(main_infos["eot"]) + "\n")
         
        elif main_infos["mode"] == "no run":
            filout.write(f"{'Mode : ':<28}" + "No run \n")
         
        else:
            filout.write(f"{'Mode : ':<28}" + "Unknown \n")
            filout.write(f"{'Nb of SOC : ':<28}" + str(main_infos["soc"]) + "\n")
            filout.write(f"{'Nb of EOC : ':<28}" + str(main_infos["eoc"]) + "\n")
            filout.write(f"{'Nb of SOT : ':<28}" + str(main_infos["sot"]) + "\n")
            filout.write(f"{'Nb of EOT : ':<28}" + str(main_infos["eot"]) + "\n")
        
        
        filout.write(f"{'Zone concerned by error : ':<28}")
        for zone in error_zones:
            filout.write("f" + str(zone[0]) + "z" + str(zone[1]) + ", ")
        filout.write("\n")
        
        filout.write(f"{'Zone concerned by warning : ':<28}")
        for zone in warning_zones:
            filout.write("f" + str(zone[0]) + "z" + str(zone[1]) + ", ") 
        filout.write("\n")
        
        
        filout.write(f"{'Unworking chips according to FIFO test : ':<28}\n")
        for chip in list_of_unworking_chip_fifo(lines):
            filout.write(f"\t{chip} \n")
            
        filout.write(f"{'Unworking chips according to event error : ':<28}\n")
        for chip in list_of_unworking_chip_events(lines):
            filout.write(f"\t{chip} \n")
        
        
        # it writes all the errors, warnings, and critical and give the lines 
        # just before the error appeared 
        filout.write("\n ============================================================================ \n")
        filout.write(" ============================== INITIALISATION ============================== ")
        filout.write("\n ============================================================================ \n")
        step = 0
        for i in range(len(lines)):
            line = lines[i]
            if len(line) >= 3 and line[2] in ["ERROR","WARNING","CRITICAL"]:
                if i > 0 and (len(lines[i-1]) < 3 or not lines[i-1][2] in ["ERROR","WARNING","CRITICAL"]):
                    filout.write("\n" + print_normal_line(lines[i-1])) 
                filout.write(print_info_line(line))
                
            elif step == 0 and len(line)>=4 and line[1] == "RoManager" and  "Configure RUs to " in line[3]:
                filout.write("\n ============================================================================ \n")
                filout.write(" ============================ SETTING COUNTERS TO 0 ========================= ")
                filout.write("\n ============================================================================ \n")
                step = 1
                
            elif step == 1 and len(line)>=4 and line[1] == "RoManager" and  "Start RU monitoring" in line[3]:
                filout.write("\n ============================================================================ \n")
                filout.write(  " ================================ RU MONITORING ============================= ")
                filout.write("\n ============================================================================ \n")
                step = 2
                
            elif step == 2 and len(line)>=4 and line[1] == "RoManager" and  "Stop RU monitoring" in line[3]:
                filout.write("\n ============================================================================ \n")
                filout.write(  " ================================ FINAL COUNTERS ============================ ")
                filout.write("\n ============================================================================ \n")
                step = 3
                
            if step == 1 and len(line)>= 4 and "events:" in line[3]:
                try:
                    if not event_0(line):
                        filout.write("ERROR :" + line[3] + "\n")
                except ValueError:
                    print("\n Error in event_0 because line in of wrong format")
                    print("\n" + filename)
                    print(print_normal_line(line))
                    print("\n")
                    
 
###############################################################################
# do_all generates the file for every file of the log folder
def do_all():
    basepath = open_log.log_folder
    for entry in tqdm(os.listdir(basepath)):
        if os.path.isfile(os.path.join(basepath, entry)):
            generate_file(entry)
            
                
                    
                    
                    
                
                