import os
import argparse
from dpsubsystem import DPSubsystem
from dpslave import DPSlave
from slot import Slot
import re
import logging
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

is_Subsystem = r'^DPSUBSYSTEM{1}(?!.*DPADDRESS)(?!.*SLOT).*$'
is_Slave = r'^DPSUBSYSTEM{1}(.*DPADDRESS)(?!.*SLOT).*$'
is_Slot = r'^(?!MASTER)DPSUBSYSTEM{1}(.*DPADDRESS)(.*SLOT).*$'
is_Type_Address = r'^LOCAL(.*ADDRESS).*$'
is_Address = r'^(?!LOCAL)(.*ADDRESS).*$'
is_End = r'^(END)'

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
    parser = argparse.ArgumentParser(description="Analize a Simatic hardware configuration file.")
    parser.add_argument('filename', type=str, help="Path to the file (*.cfg)")
    args = parser.parse_args()

    logger.info("Opening file: {}.".format(args.filename))
    file_to_read = open(args.filename,'r')
    lines = file_to_read.readlines()
    
    tree = create_hw_tree(lines)
    file_to_read.close()

    logger.info("Printing hardware description with {} subsystems.".format(len(tree)))
    
    data = list()
    for sys in tree:
        data_sys = tree[sys].description
        for addr in data_sys:
            data.append(addr)

    columns = ['id_red', 'dir_profibus','nombre_equipo','#Slot','nombre', 'type','dir_inicial', 'par1', 'par2', 'par3', 'par4', 'par5']
    df = pd.DataFrame(data=data, columns=columns)

    output_file_name =  os.path.dirname(os.path.abspath(args.filename)) + "/HW_results.csv"
    logger.info("Writing hardware description in {} file.".format(output_file_name))
    df.to_csv(output_file_name, index=False)

if __name__ == "__main__":
    main()