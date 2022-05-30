#################################################################
# save_load allows to save or load objects
#################################################################

import pickle
saving_folder = "C:/Users/alafay/cernbox/WINDOWS/Desktop/Log_analysis/Saved_Files/"

###############################################################################
# save takes an object and a filename and save it in Files/ with filename.pickle
def save(obj,filename):
  try:
    with open(saving_folder + filename + ".pickle", "wb") as f:
      pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
  except Exception as ex:
    print("Error during pickling object (Possibly unsupported):", ex)


###############################################################################
# load takes a filename, search for Files/filename.pickle and return the object
# if it exists
def load(filename):
  try:
    with open(saving_folder +filename+".pickle", "rb") as f:
      return pickle.load(f)
  except Exception as ex:
    print("Error during pickling object (Possibly unsupported):", ex) 