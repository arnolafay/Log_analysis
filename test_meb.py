
import pickle
import os
from tqdm import tqdm
import open_log
import read_main_infos
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import create_bc_bv

###############################################################################
# save takes an object and a filename and save it in Files/ with filename.pickle
def save(obj,filename):
  try:
    with open(filename + ".pickle", "wb") as f:
      pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
  except Exception as ex:
    print("Error during pickling object (Possibly unsupported):", ex)


###############################################################################
# load takes a filename, search for Files/filename.pickle and return the object
# if it exists
def load(filename):
  try:
    with open(filename+".pickle", "rb") as f:
      return pickle.load(f)
  except Exception as ex:
    print("Error during pickling object (Possibly unsupported):", ex) 
    
###############################################################################
# extract_from_lines extracts every error from the file and stores them in a 
# dictionnary given in argument according to this : {chip:([dates],[number given by the error])}
def extract_from_lines(filename, dict_error, error = ""):
    lines = open_log.lines(filename)
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
            
            chip = create_bc_bv.extract_id(id_chip)
            if not chip in dict_error.keys():
                dict_error[chip] = []
            if len(line) >= 4 and line[2] == "WARNING" and ("busy " + error) in line[3]:
                nb_error = line[3].split("busy "+ error + ":")[1]
                dict_error[chip].append((float(number_of_triggers),float(nb_error)))
            
            

###############################################################################
# 
def create_dicts():
    list_config = ["USE_ALL","USE_FIRST","USE_SECOND","USE_THIRD","USE_LAST_TWO","USE_FIRST_TWO"]
    
    for config in list_config:
        folder = "C:/Users/alafay/cernbox/WINDOWS/Desktop/Log_analysis/Logs/testbench/" + config + "/"
        dict_bv = {}
        dict_bc = {}
        for entry in tqdm(os.listdir(folder)):
            if os.path.isfile(os.path.join(folder, entry)):
                if entry[-4:] == ".log":
                    extract_from_lines(config + "/" + entry, dict_bv, "violations")
                    extract_from_lines(config + "/" + entry, dict_bc, "chip")    
        save(dict_bc, folder + "dict_bc")
        save(dict_bv, folder + "dict_bv")
        
        
###############################################################################
def create_results():
    list_config = ["USE_ALL","USE_FIRST","USE_SECOND","USE_THIRD","USE_LAST_TWO","USE_FIRST_TWO"]
    folder = "C:/Users/alafay/cernbox/WINDOWS/Desktop/Log_analysis/Logs/testbench/" + "USE_ALL" + "/"
    dict_bc = load(folder + "dict_bc")
    list_chip = dict_bc.keys()
    len_chip = len(list_chip)
    len_config = len(list_config)
    
    resultats_bc = np.zeros((len_chip,len_config))
    resultats_bv = np.zeros((len_chip,len_config))
    
    for i_config in range(len_config):
        config = list_config[i_config]
        folder = "C:/Users/alafay/cernbox/WINDOWS/Desktop/Log_analysis/Logs/testbench/" + config + "/"
        dict_bc = load(folder + "dict_bc")
        dict_bv = load(folder + "dict_bv")
        
        for i_chip in range(len_chip):
            list_bc = dict_bc[list(list_chip)[i_chip]]
            list_bv = dict_bv[list(list_chip)[i_chip]]
            
            nb_bc = 0.
            nb_bv = 0.
            nb_trigger_bc = 0.
            nb_trigger_bv = 0.
            
            for bc in list_bc:
                
                nb_trigger_bc += bc[0]
                nb_bc += bc[1]
            
            for bv in list_bv:
                nb_trigger_bv += bv[0]
                nb_bv += bv[1]
                
            if nb_trigger_bc != 0:
                resultats_bc[i_chip,i_config] = nb_bc / nb_trigger_bc
            if nb_trigger_bv != 0:
                
                resultats_bv[i_chip,i_config] = nb_bv / nb_trigger_bv
            
    return resultats_bc, resultats_bv, list_chip, list_config
        
        
###############################################################################
def plot():
    tab_bc, tab_bv, list_chip, list_config = create_results()
    fig, axs = plt.subplots(1, 2, figsize=(28,12))
    
    len_chip = len(list_chip)
    len_config = len(list_config)
    
    ax = axs[0]
    ax.pcolor(tab_bc, cmap="Reds", norm=LogNorm())
    
    ax.set_yticks(ticks = np.arange(0.5,len_chip+0.5))
    ax.set_yticklabels(list_chip)
    ax.set_xticks(ticks = np.arange(0.5,len_config+0.5))
    ax.set_xticklabels(list_config)
    
    ax = axs[1]
    ax.pcolor(tab_bv, cmap="Reds", norm=LogNorm())

    ax.set_yticks(ticks = np.arange(0.5,len_chip+0.5))
    ax.set_yticklabels(list_chip)
    ax.set_xticks(ticks = np.arange(0.5,len_config+0.5))
    ax.set_xticklabels(list_config)
    
    pcm = ax.pcolormesh(tab_bc,cmap = "Reds", norm=LogNorm())
    plt.colorbar(pcm, ax = axs.ravel().tolist())
    plt.show()
    
###############################################################################
def do_all():
    create_dicts()
    plot()