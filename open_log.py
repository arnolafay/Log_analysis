###############################################################################
# open_logs is the first step to analyze log files
# the main function is open_file
###############################################################################

log_folder = "C:/Users/alafay/cernbox/WINDOWS/Desktop/Log_analysis/Logs/cru/"

###############################################################################
# split_list takes in entry a list and a string (often a character) and split
# each element of the list according to the character
def split_list(list, char):
    n = len(list)
    list_v2 = []
    for i in range(n):
        list_v2.append(list[i].split(char))
    return list_v2

###############################################################################
# lines takes as argument a filename (with the folder) and gives the list of 
# the lines, and each lines is splitted according to '-' and some characters 
# are removed for it to be easier to read
def lines(filename):
    assert filename[-4:] != '.log' "The given file is not a logfile"
    f = open(log_folder + filename, "r")
    lines = split_list(f.readlines(), " - ")
    
    for line in lines:
        line[-1] = line[-1].replace('\n','')
        for i in range(len(line)):
            line[i] = line[i].replace("\t","")
            if i != 0 and i != len(line)-1:
                line[i] = line[i].replace(" ","")
    return lines
    
###############################################################################
# types return the type of the logfile according to the correspondance between
# list_keys and given_names
def types(filename):
    types = {}
    list_keys   = ["program","ecs","DaqBaseTest","HsLinkTest","Noise","Noise-masked","Physics","Physics-masked","program_ru","Pulser","Pulser-pbpb","Pulser-pp","RuMonitoring"]
    given_names = ["program","ecs","DaqBaseTest","PRBS"      ,"Noise","Noise-masked","Physics","Physics-masked","program_ru","Pulser","Pulser-PbPb","Pulser-pp","RuMonitoring"]
    for k in range(len(list_keys)):
        types[list_keys[k]] = given_names[k]
    logfile_type = types[filename.split("_")[0]]     
    return logfile_type