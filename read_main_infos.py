###############################################################################
# read_main_infos gives the main infos of the log file
# we give each function a list of lines created by open_files.py
# each function works by parsing threw the lines and finding a given 
# sentence that corresponds to what we want
###############################################################################

from datetime import datetime, timedelta
import re

###############################################################################
# find_name gives the name of the concerned disk in the log file
def find_name(lines):
    i = 0
    while len(lines[i])<2 or lines[i][1] != 'CruToRoZones':
        i += 1
    name = lines[i][3].replace('Selected','')
    return name

###############################################################################
# find_start_date gives the starting date of the log file
def find_start_date(lines):
    i = 0
    while len(lines[i])<2 or lines[i][1] != 'CruToRoZones':
        i += 1
    date = lines[i][0]
    return date

###############################################################################
# find_end_date gives the ending date of the log file and if the script ended 
# properly (i.e one line has "====== end of run ======")
def find_end_date(lines):
    n = len(lines)
    i = n - 1
    while len(lines[i])<2 or lines[i][0][0:2] != '20':
        i -= 1
    if lines[i][3] == "=============== end of run ================":
        test = True
    else:
        test = False
    date = lines[i][0]
    return date, str(test)


###############################################################################
# find_freq gives the frequency of the run (added in the log file on 21/10/2021)
def find_freq(lines):
    i = 0
    while len(lines[i])<4 or lines[i][0][0:2] != '20' or "freq" not in lines[i][3]:
        i += 1
    freq_str = re.search("freq.*",lines[i][3]).group()[5:]
    freq_float = float(freq_str[:-4])*10**3
    return freq_float

###############################################################################
# script_duration gives the duration of the script betwend end_date and start_date 
def script_duration(lines):
    start_date_str = find_start_date(lines)
    end_date_str = find_end_date(lines)[0]
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S,%f")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S,%f")
    return (end_date-start_date)

###############################################################################
# find_HB gives how many heart beats are sent
def find_HB(lines):
    n = len(lines)
    i = 1
    while lines[n-i][0][:5] != "- HB:":
        i += 1
    hb = lines[n-i][0][5:]
    return int(hb)

###############################################################################
# find_HBA gives how many heart beats are accepted
def find_HBA(lines):
    n = len(lines)
    i = 1
    while not bool(re.search("- HBA:",lines[n-i][0])):
        i += 1
    hba = lines[n-i][0][re.search("- HBA:",lines[n-i][0]).end():]
    return int(hba)      

###############################################################################
# find_trigerssent gives how many triggers are sent
# we have to do an operation because the maximal int coded by 32 bit can be
# reached. Thus we make a correspondance between HBA and the number given by 
# the triggers because they can be linked through the frequency
# it returns the number of trigger + the boolean showing that we know if it is 
# correct
def find_triggerssent(lines):
    n = len(lines)
    i = 1
    while lines[n-i][0][:16] != "- Triggers Sent:":
        i += 1
    triggerssent = int(lines[n-i][0][16:])
    
    try:
        freq = find_freq(lines)
        hba = find_HBA(lines)
        
        time_acquisition = float(hba) * 89.4e-6 #the acquisition lasted for number of hba * duration of 1 hb time frame
        while float(triggerssent) / float(freq) < time_acquisition:
            triggerssent += 4294967295 # max int coded by 32 bit
        return triggerssent, True, time_acquisition
        
    except IndexError:
        return triggerssent, False, 0

###############################################################################
# find_SOC gives the Starting of Continuous mode
def find_SOC(lines):
    n = len(lines)
    i = 1
    while lines[n-i][0][:6] != "- SOC:":
        i += 1
    soc = lines[n-i][0][6:]
    return int(soc)

###############################################################################
# find_EOC gives the End of Continuous mode
def find_EOC(lines):
    n = len(lines)
    i = 1
    while lines[n-i][0][:6] != "- EOC:":
        i += 1
    eoc = lines[n-i][0][6:]
    return int(eoc)

###############################################################################
# find_SOT gives the Starting of Triggered mode
def find_SOT(lines):
    n = len(lines)
    i = 1
    while lines[n-i][0][:6] != "- SOT:":
        i += 1
    sot = lines[n-i][0][6:]
    return int(sot)

###############################################################################
# find_EOT gives the End of Triggered mode
def find_EOT(lines):
    n = len(lines)
    i = 1
    while lines[n-i][0][:6] != "- EOT:":
        i += 1
    eot = lines[n-i][0][6:]
    return int(eot)

###############################################################################
# find_infos gathers all the preceding informations
def find_infos(lines):
    result = {}
    result["disk"]       = find_name(lines)
    result["start_date"] = find_start_date(lines)
    result["end_date"]   = find_end_date(lines)[0]
    result["proper_end"] = find_end_date(lines)[1]
    result["script_duration"] = script_duration(lines)
    try:
        trig = find_triggerssent(lines)
        result["number_of_triggers_sent"] = trig[0]
        result["correction_triggers"] = trig[1]
        if trig[1]:
            result["time_acquisition"] = trig[2]
        else: 
            result["time_acquisition"] = 0
    except IndexError:
        result["number_of_triggers_sent"] = 0
        result["correction_triggers"] = False
        result["time_acquisition"] = 0
    try:
        result["soc"] = find_SOC(lines)
    except IndexError:
        result["soc"] = 0
    try:
        result["eoc"] = find_EOC(lines)
    except IndexError:
        result["eoc"] = 0
    try:
        result["sot"] = find_SOT(lines)
    except IndexError:
        result["sot"] = 0
    try:
        result["eot"] = find_EOT(lines)
    except IndexError:
        result["eot"] = 0
        
    try:
        result["freq"] = find_freq(lines)
    except IndexError:
        result["freq"] = 0
        
    if result["eoc"] != 0 and result["soc"] != 0:
        result["mode"] = "continuous"
    elif result["eot"] != 0 and result["sot"] != 0:
        result["mode"] = "triggered"
    elif result["eoc"] == 0 and result["soc"] == 0 and result["eot"] == 0 and result["sot"] == 0:
        result["mode"] = "no run"
    else:
        result["mode"] = "unknown"
        
    return result