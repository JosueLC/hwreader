import os
import argparse
from dpsubsystem import DPSubsystem
from dpslave import DPSlave
from slot import Slot
import re
import logging
import pandas as pd

import tkinter as tk
from tkinter import filedialog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# is_Subsystem = r'^DPSUBSYSTEM{1}(?!.*DPADDRESS)(?!.*SLOT).*$'
# is_Slave = r'^DPSUBSYSTEM{1}(.*DPADDRESS)(?!.*SLOT).*$'
# is_Slot = r'^(?!MASTER)DPSUBSYSTEM{1}(.*DPADDRESS)(.*SLOT).*$'
is_Subsystem = r'^IOSUBSYSTEM{1}(?!.*IOADDRESS)(?!.*SLOT).*$'
is_Slave = r'^IOSUBSYSTEM{1}(.*IOADDRESS)(?!.*SLOT).*$'
is_Slot = r'^(?!MASTER)IOSUBSYSTEM{1}(.*IOADDRESS)(.*SLOT).*$'
is_Type_Address = r'^LOCAL(.*ADDRESS).*$'
is_Address = r'^(?!LOCAL)(.*ADDRESS).*$'
is_End = r'^(END)'

def get_pathfile():
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilenames()
    return filepath

def create_hw_tree(text):
    logger.info("Starting creation of hardware tree from text with {} lines.".format(len(text)))
    hw_tree = {}

    #last_object_create = "none"

    for i in range(len(text)):
        line = text[i].rstrip()
        
        if (re.match(is_Subsystem, line) is not None):
            init = i
            while (re.match(is_End, text[i]) is None):
                i += 1
            end = i
            new_subsystem = DPSubsystem(text[init:end]) 
            hw_tree[new_subsystem.get_id] = new_subsystem
        elif (re.match(is_Slave, line) is not None):
            init = i
            while (re.match(is_End, text[i]) is None):
                i += 1
            end = i
            new_slave = DPSlave(text[init:end])
            hw_tree[new_slave.get_subsystem_id].set_new_slave(new_slave)
        elif (re.match(is_Slot, line) is not None):
            init = i
            while (re.match(is_End, text[i]) is None):
                i += 1
            end = i
            new_slot = Slot(text[init:end])
            hw_tree[new_slot.get_subsystem_id].get_slave(new_slot.get_slave_id).set_new_slot(new_slot)

    return hw_tree

def main():

    filenames = get_pathfile()

    for filename in filenames:
        logger.info("Opening file: {}.".format(filename))
        file_to_read = open(filename,'r')
        try:
            lines = file_to_read.readlines()
        except UnicodeDecodeError as ude:
            lines = ""
            print(f'has occurred an error: {ude}')

        tree = create_hw_tree(lines)
        file_to_read.close()

        logger.info("Printing hardware description with {} subsystems.".format(len(tree)))

        data = list()
        for sys in tree:
            data_sys = tree[sys].description
            for addr in data_sys:
                data.append(addr)

        #get directory from args.filename
        directory = os.path.dirname(filename)
        #create a new file with the same name but with .xlsx extension
        new_file = os.path.join(directory, os.path.splitext(os.path.basename(filename))[0] + ".xlsx")
        #sheetname
        sheetname = filename.split('/')[-1].split('.')[0]
        sorted_cols =['red','dir_profibus','nombre_equipo','ref_equipo','comentario','slot_modulo','ref_modulo','nombre_modulo','dir','tipo','rango','tag','descripcion']
        cols_dtypes ={'red':str,'dir_profibus':int,'nombre_equipo':str,'ref_equipo':str,'comentario':str,'slot_modulo':int,'ref_modulo':str,'nombre_modulo':str,'dir':str,'tipo':str,'rango':str,'tag':str,'descripcion':str}
        df = pd.DataFrame(data,columns=sorted_cols)
        df = df.astype(dtype=cols_dtypes)
        # df = df.set_index(sorted_cols[:4])
        df.to_excel(new_file,sheet_name=sheetname,index=False)
        logger.info("File saved as {}.".format(new_file))

if __name__ == "__main__":
    main()